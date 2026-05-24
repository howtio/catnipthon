"""Real implementations of all tools — MVP 6 + v4.0 web/search/browser."""

from __future__ import annotations

import re
import subprocess
import webbrowser
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ── MVP tools ────────────────────────────────────────────────────────────────


def list_files(path: str = ".") -> str:
    """List files and directories in a given path."""
    target = WORKSPACE_ROOT / path
    if not target.is_dir():
        return f"Error: not a directory: {path}"

    lines: list[str] = []
    try:
        for entry in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"{entry.name}{suffix}")
        return "\n".join(lines) if lines else "(empty directory)"
    except PermissionError:
        return f"Error: permission denied: {path}"
    except OSError as e:
        return f"Error: {e}"


def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    target = Path(file_path)
    if not target.is_file():
        return f"Error: file not found: {file_path}"
    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: binary file or non-UTF-8 encoding: {file_path}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except OSError as e:
        return f"Error: {e}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Creates parent dirs if needed."""
    target = Path(file_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Written {len(content)} bytes to {file_path}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except OSError as e:
        return f"Error: {e}"


def patch_file(file_path: str, old_string: str, new_string: str) -> str:
    """Apply a string replacement in a file."""
    target = Path(file_path)
    if not target.is_file():
        return f"Error: file not found: {file_path}"

    try:
        content = target.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        return f"Error: {e}"

    if old_string not in content:
        return f"Error: old_string not found in {file_path}"

    count = content.count(old_string)
    new_content = content.replace(old_string, new_string)
    target.write_text(new_content, encoding="utf-8")

    return f"Patched {count} occurrence(s) in {file_path}"


def shell_exec(command: str, timeout_ms: int = 30000) -> str:
    """Execute a shell command and return stdout/stderr."""
    timeout_s = timeout_ms / 1000.0
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        output_parts: list[str] = []
        if result.stdout:
            output_parts.append(result.stdout.rstrip())
        if result.stderr:
            output_parts.append(f"[stderr]\n{result.stderr.rstrip()}")
        output = "\n".join(output_parts) if output_parts else "(no output)"

        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"

        return output
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout_ms}ms"
    except FileNotFoundError:
        return "Error: shell not available on this system"
    except OSError as e:
        return f"Error: {e}"


def git_diff() -> str:
    """Show unstaged git diff."""
    try:
        result = subprocess.run(
            ["git", "diff"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stdout:
            return result.stdout
        staged = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if staged.stdout:
            return f"(staged changes)\n{staged.stdout}"
        return "(no changes)"
    except subprocess.TimeoutExpired:
        return "Error: git diff timed out"
    except FileNotFoundError:
        return "Error: git not available"
    except OSError as e:
        return f"Error: {e}"


# ── v4.0 tools: web fetch / search / browser / file search ──────────────────


def _fetch_url(url: str, timeout_s: int = 15) -> str:
    """Fetch URL content via httpx. Returns text (HTML stripped)."""
    try:
        import httpx
    except ImportError:
        return "Error: httpx not available"
    try:
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            text = resp.text
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > 10000:
                text = text[:10000] + "\n... [truncated to 10KB]"
            return text
    except httpx.TimeoutException:
        return f"Error: timeout fetching {url}"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} for {url}"
    except Exception as e:
        return f"Error: {e}"


def web_fetch(url: str) -> str:
    """Fetch a URL and return its text content (HTML stripped)."""
    if not url.startswith(("http://", "https://")):
        return "Error: only http/https URLs are allowed"
    return _fetch_url(url)


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web via DuckDuckGo HTML interface."""
    import urllib.parse

    try:
        import httpx
    except ImportError:
        return "Error: httpx not available"

    max_results = max(1, min(max_results, 10))
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return f"Error: search failed: {e}"

    results: list[str] = []
    link_pat = re.compile(r'class="result__a"[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>')
    snippet_pat = re.compile(r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>', re.DOTALL)

    links = link_pat.findall(html)
    snippets = snippet_pat.findall(html)

    for i, (href, title_text) in enumerate(links[:max_results]):
        title = re.sub(r"<[^>]+>", "", title_text).strip()
        snippet = ""
        if i < len(snippets):
            snippet = re.sub(r"<[^>]+>", "", snippets[i]).strip()
        results.append(f"{i+1}. {title}\n   {href}")
        if snippet:
            results.append(f"   {snippet}")

    if not results:
        return f"(no results for: {query})"
    return "\n".join(results)


def open_browser(url: str) -> str:
    """Open a URL or local file in the default browser (non-blocking, 5s timeout)."""
    # Resolve local file paths to file:// URLs
    if not url.startswith(("http://", "https://", "file://")):
        p = Path(url)
        if p.exists():
            url = p.resolve().as_uri()
        else:
            # Try relative to workspace
            wp = WORKSPACE_ROOT / url
            if wp.exists():
                url = wp.resolve().as_uri()
            else:
                return f"Error: file not found: {url} (use http/https or a valid local path)"
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as exe:
        fut = exe.submit(webbrowser.open, url)
        try:
            result = fut.result(timeout=5.0)
            if result:
                return f"Opened browser: {url}"
            return "Error: webbrowser.open returned False (no browser found)"
        except concurrent.futures.TimeoutError:
            return f"Opened browser (detached): {url}"
        except Exception as e:
            return f"Error: {e}"


def file_search(pattern: str, content: str = "", max_results: int = 20) -> str:
    """Search files by name glob or text content in workspace."""
    max_results = max(1, min(max_results, 50))
    matches: list[str] = []
    skip_dirs = {".venv", ".git", "__pycache__", "node_modules"}

    if content:
        for f in WORKSPACE_ROOT.rglob(pattern):
            if any(p in skip_dirs for p in f.parts):
                continue
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                if content in text:
                    rel = f.relative_to(WORKSPACE_ROOT)
                    matches.append(str(rel))
                    if len(matches) >= max_results:
                        break
            except Exception:
                continue
    else:
        for f in WORKSPACE_ROOT.rglob(pattern):
            if any(p in skip_dirs for p in f.parts):
                continue
            rel = f.relative_to(WORKSPACE_ROOT)
            matches.append(str(rel))
            if len(matches) >= max_results:
                break

    if not matches:
        return f"(no matches for: {pattern})"
    return "\n".join(matches)
