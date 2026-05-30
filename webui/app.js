const paperColumnCount = 10;
const STORAGE_KEY = "catnip-conversations";
const demoMode = new URLSearchParams(window.location.search).get("demo");

const initialConversations = [
  {
    id: createId(),
    question: "阿嬷，今天的风很轻，我想在这里慢慢和你说话。",
    answer:
      "那就把心事写下来吧。\n左下的木槿花会替你添一张新纸，右下的纸飞机会把字送出去。\n以后接入真正的 agent 时，这里就会像一封封回信那样，稳稳落下来。",
    createdAt: "2026-05-30T09:18:00",
  },
];

function loadConversations() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      }
    }
  } catch (_) {}
  return null;
}

function saveConversations() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.conversations));
  } catch (_) {}
}

const savedConvs = loadConversations();
const state = {
  conversations: savedConvs || [...initialConversations],
  composing: false,
  sending: false,
  draft: "",
  historyOpen: false,
  openedConversationId: null,
};

if (!savedConvs) {
  saveConversations();
}

const historyPanel = document.querySelector(".history-panel");
const historyChestToggle = document.querySelector("#historyChestToggle");
const historyChestHint = document.querySelector("#historyChestHint");
const composeButton = document.querySelector("#composeButton");
const sendButton = document.querySelector("#sendButton");
const paperStack = document.querySelector("#paperStack");
const historyList = document.querySelector("#historyList");
const historyDialog = document.querySelector("#historyDialog");
const historyDialogTitle = document.querySelector("#historyDialogTitle");
const historyDialogSheets = document.querySelector("#historyDialogSheets");

historyChestToggle.addEventListener("click", () => {
  state.historyOpen = !state.historyOpen;
  render();
});

composeButton.addEventListener("click", () => {
  state.composing = true;
  render();
  focusDraftEditor();
});

sendButton.addEventListener("click", async () => {
  if (state.sending) {
    return;
  }

  const content = state.draft.trim();
  if (!content) {
    state.composing = true;
    render();
    focusDraftEditor();
    return;
  }

  const conversation = {
    id: createId(),
    question: content,
    answer: "",
    thinking: "",
    pending: true,
    createdAt: new Date().toISOString(),
  };

  const priorConversations = [...state.conversations];
  state.conversations = [...priorConversations, conversation];
  state.draft = "";
  state.composing = false;
  state.sending = true;
  saveConversations();
  render();

  try {
    const answer = await requestAgentReply(content, priorConversations, (thinking) => {
      state.conversations = state.conversations.map((item) =>
        item.id === conversation.id
          ? { ...item, thinking }
          : item,
      );
      render();
    });
    state.conversations = state.conversations.map((item) =>
      item.id === conversation.id
        ? {
            ...item,
            answer,
            thinking: "",
            pending: false,
          }
        : item,
    );
    saveConversations();
  } catch (error) {
    state.conversations = state.conversations.map((item) =>
      item.id === conversation.id
        ? {
            ...item,
            answer: "这封回信暂时被风拦住了，稍后我们再试一次。",
            thinking: "",
            pending: false,
          }
        : item,
    );
    saveConversations();
    console.error(error);
  } finally {
    state.sending = false;
    render();
  }
});

document.querySelector("#clearHistoryBtn").addEventListener("click", () => {
  if (state.conversations.length === 0) return;
  if (!confirm("确定要清空所有信纸吗？")) return;

  // Clear localStorage
  localStorage.removeItem(STORAGE_KEY);
  // Reset conversations to initial welcome
  state.conversations = [...initialConversations];
  saveConversations();
  render();

  // Also clear server-side memory
  fetch("/api/history/clear", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }).catch(() => {});
});

historyList.addEventListener("click", (event) => {
  const note = event.target.closest("[data-conversation-id]");
  if (!note) {
    return;
  }

  const conversation = state.conversations.find(
    (item) => item.id === note.dataset.conversationId,
  );
  if (!conversation) {
    return;
  }

  state.openedConversationId = conversation.id;
  renderHistoryDialog(conversation);
  historyDialog.showModal();
});

historyDialog.addEventListener("click", (event) => {
  const btn = event.target.closest("[data-export-conversation]");
  if (btn) {
    const conversation = state.conversations.find(
      (item) => item.id === btn.dataset.exportConversation,
    );
    if (conversation) {
      exportConversation(conversation);
    }
    return;
  }
  if (event.target === historyDialog) {
    historyDialog.close();
  }
});

window.addEventListener("resize", queuePaperAlignment);

paperStack.addEventListener("click", (event) => {
  const btn = event.target.closest("[data-export-conversation]");
  if (!btn) return;
  const conversation = state.conversations.find(
    (item) => item.id === btn.dataset.exportConversation,
  );
  if (conversation) {
    exportConversation(conversation);
  }
});

applyDemoState();
render();

function render() {
  renderHistoryChest();
  renderHistoryList();
  renderPaperStack();
  sendButton.disabled = !state.draft.trim() || state.sending;
  queuePaperAlignment();
}

function renderHistoryChest() {
  historyPanel.classList.toggle("is-open", state.historyOpen);
  historyChestToggle.setAttribute("aria-expanded", String(state.historyOpen));
  historyChestHint.textContent = state.historyOpen
    ? "再点一下，把旧信一封封收回匣里"
    : "点一下，摊开旧信匣";
}

function renderHistoryList() {
  const history = [...state.conversations].reverse();

  historyList.innerHTML =
    history.length === 0
      ? `<div class="history-empty">匣中还空着，等第一封旧信收进来。</div>`
      : history
          .map((conversation, index) => {
            const noteStyle = buildHistoryNoteStyle(conversation.id, index);
            return `
              <button
                class="history-note"
                type="button"
                data-conversation-id="${conversation.id}"
                style="${noteStyle}"
              >
                <span class="history-note__tag">${conversation.pending ? "回信途中" : "已归档"}</span>
                <span class="history-note__excerpt">${escapeHtml(
                  truncate(conversation.question, 28),
                )}</span>
                <span class="history-note__date">${escapeHtml(
                  formatHistoryDate(conversation.createdAt),
                )}</span>
              </button>
            `;
          })
          .join("");
}

function renderPaperStack() {
  const papers = getVisiblePapers();

  paperStack.innerHTML = papers
    .map((paper, index) => {
      const stackIndex = papers.length - index - 1;
      const metaTime = formatSheetTime(paper.createdAt);
      const footerText = paper.footer || "阿嬷会在下一页等你。";
      const motion = buildPaperMotion(paper, stackIndex);
      const isFresh = stackIndex <= 1 || paper.pending || paper.id === "draft";

      return `
        <article
          class="letter-sheet letter-sheet--${paper.kind} ${isFresh ? "letter-sheet--fresh" : ""}"
          style="${motion}"
        >
          <div class="sheet__meta">
            <span>${escapeHtml(paper.meta)}</span>
            <span class="sheet__stamp">${escapeHtml(paper.stamp)}</span>
          </div>
          ${
            paper.kind === "draft"
              ? `
                <div
                  id="draftEditor"
                  class="sheet__editor ${paper.content ? "" : "is-empty"}"
                  contenteditable="true"
                  role="textbox"
                  aria-multiline="true"
                  spellcheck="false"
                  data-placeholder="在这里竖着写下你想问的话……"
                >${escapeHtml(paper.content)}</div>
              `
              : `<div class="sheet__content">${formatVerticalText(paper.content)}</div>`
          }
          ${
            paper.pending
              ? `<div class="sheet__status">回信正在落款</div>`
              : ""
          }
          <div class="sheet__footer">
            <span>${escapeHtml(metaTime)}</span>
            <span>
              ${escapeHtml(footerText)}
              ${paper.kind === "answer" && !paper.pending
                ? `<button class="sheet__print-trigger" data-export-conversation="${paper.conversationId}">印一份</button>`
                : ""}
            </span>
          </div>
        </article>
      `;
    })
    .join("");

  const draftEditor = document.querySelector("#draftEditor");
  if (draftEditor) {
    draftEditor.addEventListener("input", syncDraftFromEditor);
    draftEditor.addEventListener("keydown", handleDraftKeydown);
    draftEditor.classList.toggle("is-empty", !draftEditor.textContent.trim());
  }
}

function renderHistoryDialog(conversation) {
  const conversationIndex =
    state.conversations.findIndex((item) => item.id === conversation.id) + 1;

  historyDialogTitle.textContent = `第 ${conversationIndex} 封`;

  const oldPrintBtn = historyDialog.querySelector(".history-dialog__print");
  if (oldPrintBtn) oldPrintBtn.remove();
  const printBtn = document.createElement("button");
  printBtn.className = "history-dialog__print";
  printBtn.textContent = "印一份";
  printBtn.dataset.exportConversation = conversation.id;
  historyDialog.querySelector(".history-dialog__meta").appendChild(printBtn);

  historyDialogSheets.innerHTML = [
    {
      meta: "来信",
      content: conversation.question,
      createdAt: conversation.createdAt,
    },
    {
      meta: "回信",
      content: conversation.pending ? "这封回信还在慢慢写。" : conversation.answer,
      createdAt: conversation.createdAt,
    },
  ]
    .map(
      (paper) => `
        <article class="archive-sheet">
          <div class="archive-sheet__meta">
            <span>${escapeHtml(paper.meta)}</span>
            <span>${escapeHtml(formatHistoryDate(paper.createdAt))}</span>
          </div>
          <div class="archive-sheet__content">${formatVerticalText(paper.content)}</div>
        </article>
      `,
    )
    .join("");

  queuePaperAlignment();
}

function getVisiblePapers() {
  const paperEntries = state.conversations.flatMap((conversation) => [
    {
      id: `${conversation.id}-question`,
      conversationId: conversation.id,
      kind: "question",
      meta: "来信",
      stamp: "所问",
      content: conversation.question,
      createdAt: conversation.createdAt,
      footer: "问题会被细细收好。",
    },
    {
      id: `${conversation.id}-answer`,
      conversationId: conversation.id,
      kind: "answer",
      meta: "回信",
      stamp: conversation.pending ? "未封缄" : "已回",
      content: conversation.pending
        ? (conversation.thinking || "稍等一会儿，回信正在路上。")
        : conversation.answer,
      createdAt: conversation.createdAt,
      footer: conversation.pending ? "正在替你铺开下一页。" : "回答会像回信一样压在上层。",
      pending: conversation.pending,
    },
  ]);

  const basePapers =
    paperEntries.length > 0
      ? paperEntries.slice(-4)
      : [
          {
            id: "system-empty",
            kind: "system",
            meta: "空白信面",
            stamp: "待书",
            content: "还没有任何往来。\n点击左下角木槿花，先添一页新纸。",
            createdAt: new Date().toISOString(),
            footer: "故事会从第一封开始。",
          },
        ];

  if (!state.composing) {
    return basePapers;
  }

  return [
    ...basePapers.slice(-3),
    {
      id: "draft",
      kind: "draft",
      meta: "新纸",
      stamp: "未寄",
      content: state.draft,
      createdAt: new Date().toISOString(),
      footer: "写好后，点右下角纸飞机。",
    },
  ];
}

function syncDraftFromEditor(event) {
  state.draft = normalizeEditorText(event.currentTarget);
  event.currentTarget.classList.toggle("is-empty", !state.draft.trim());
  sendButton.disabled = !state.draft.trim() || state.sending;
}

function handleDraftKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    sendButton.click();
  }
}

function focusDraftEditor() {
  const editor = document.querySelector("#draftEditor");
  if (!editor) {
    return;
  }

  editor.focus();

  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(editor);
  range.collapse(false);
  selection.removeAllRanges();
  selection.addRange(range);
}

async function requestAgentReply(question, conversations, onThinking) {
  if (window.agentConnector && typeof window.agentConnector.ask === "function") {
    const result = await window.agentConnector.ask({
      question,
      history: conversations.map(({ question: ask, answer }) => ({
        question: ask,
        answer,
      })),
    });
    return typeof result === "string" ? result : result.answer || "";
  }

  if (window.location.protocol.startsWith("http")) {
    return requestHttpAgentReply(question, conversations, onThinking);
  }

  return simulateReply(question);
}

async function requestHttpAgentReply(question, conversations, onThinking) {
  // Step 1: POST /api/chat — agent starts in background, returns run_id
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      history: conversations.map(({ question: ask, answer }) => ({
        question: ask,
        answer,
      })),
    }),
  });

  if (response.status === 429) {
    throw new Error("上一封回信还在落款，请稍后再寄下一封。");
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const payload = await response.json();
  if (payload.answer) {
    return String(payload.answer).trim();
  }

  if (!payload.run_id) {
    throw new Error("No run_id returned");
  }

  // Step 2: Poll /api/chat/think/{run_id} until completed
  let lastThinking = "";
  const startedAt = Date.now();

  while (Date.now() - startedAt < 90000) {
    await sleep(650);

    const pollRes = await fetch(`/api/chat/think/${payload.run_id}`);
    if (!pollRes.ok) {
      throw new Error(`Poll HTTP ${pollRes.status}`);
    }

    const data = await pollRes.json();

    if (data.thinking && data.thinking !== lastThinking) {
      lastThinking = data.thinking;
      if (onThinking) onThinking(summarizeThinking(data.thinking));
    }

    if (data.status === "completed") {
      return String(data.answer || "").trim();
    }

    if (data.status === "error") {
      throw new Error(data.error || "Agent run failed");
    }
  }

  throw new Error("Agent response timed out");
}

function simulateReply(question) {
  return new Promise((resolve) => {
    const references = [
      "我替你把这句话收好了。等接入真正的 agent 后，它就会顺着这页纸继续答你。",
      "这套界面已经准备好了来信与回信的节奏，剩下的只差把真实能力接进来。",
      "如果你愿意，我们下一步可以把模型回复、流式输出、历史持久化一起接上。",
    ];

    const trimmed = question.replace(/\s+/g, " ").trim();

    if (/天气|下雨|晴|风/.test(trimmed)) {
      resolve(
        `风声我听见了。\n现在这版前端会先温柔地接住你的问题，等真正的 agent 连上来，就能把天气、时间和现实里的消息写成回信。\n${references[0]}`,
      );
      return;
    }

    if (/代码|开发|界面|前端|agent/i.test(trimmed)) {
      resolve(
        `这封来信很清楚。\n我会把它理解成一次新的开发任务：先收问题，再叠回答，最后把历史归进旧信匣。\n${references[1]}`,
      );
      return;
    }

    resolve(
      `你的话已经落在纸上了。\n“${trimmed.slice(0, 28)}${trimmed.length > 28 ? "…" : ""}”会被放在最上层，等待一封真正的回信。\n${references[2]}`,
    );
  }).then(
    (reply) =>
      new Promise((resolve) => {
        window.setTimeout(() => resolve(reply), 980);
      }),
  );
}

function normalizeEditorText(node) {
  return node.innerText
    .replace(/\u00a0/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trimStart();
}

function formatVerticalText(text) {
  return escapeHtml(text).replace(/\n/g, "<br />");
}

function formatHistoryDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatSheetTime(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  }).format(date);
}

function truncate(text, limit) {
  return text.length > limit ? `${text.slice(0, limit)}…` : text;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function summarizeThinking(thinking) {
  const lines = String(thinking)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    return "回信正在铺纸。";
  }

  const latest = lines.at(-1).replace(/^——\s*/, "");
  return truncate(latest, 40);
}

function createId() {
  return `letter-${Math.random().toString(36).slice(2, 10)}`;
}

function queuePaperAlignment() {
  window.requestAnimationFrame(syncPaperAlignment);
}

function syncPaperAlignment() {
  document
    .querySelectorAll(".sheet__content, .sheet__editor, .archive-sheet__content")
    .forEach((node) => {
      const columnWidth = node.clientWidth / paperColumnCount;
      if (!columnWidth) {
        return;
      }

      const fontSize = Math.max(18, Math.min(32, columnWidth * 0.4));
      node.style.lineHeight = `${columnWidth}px`;
      node.style.fontSize = `${fontSize}px`;
    });
}

function buildHistoryNoteStyle(id, index) {
  const hash = hashFromString(id);
  const tilt = (((hash >> 2) % 9) - 4) * 0.9;
  const shift = (((hash >> 5) % 9) - 4) * 2;
  const delay = index * 45;

  return `--note-tilt:${tilt.toFixed(2)}deg;--note-shift:${shift}px;--note-delay:${delay}ms;`;
}

function buildPaperMotion(paper, stackIndex) {
  const hash = hashFromString(paper.id);
  const settleX = stackIndex * 16 + ((((hash >> 4) % 7) - 3) * 1.7);
  const settleY = stackIndex * -11 + ((((hash >> 8) % 7) - 3) * 1.3);
  const baseTiltMap = {
    question: -1.6,
    answer: 1.25,
    draft: -0.85,
    system: -2.1,
  };
  const tilt = (baseTiltMap[paper.kind] ?? -0.6) + ((((hash >> 10) % 11) - 5) * 0.16);
  const dropX = settleX + ((((hash >> 14) % 50) - 25) * 1.1);
  const dropY = settleY - 96 - stackIndex * 10;
  const dropRotate = tilt + ((((hash >> 18) % 15) - 7) * 0.45);

  return [
    `--settle-x:${settleX.toFixed(2)}px`,
    `--settle-y:${settleY.toFixed(2)}px`,
    `--tilt:${tilt.toFixed(2)}deg`,
    `--drop-x:${dropX.toFixed(2)}px`,
    `--drop-y:${dropY.toFixed(2)}px`,
    `--drop-rotate:${dropRotate.toFixed(2)}deg`,
  ].join(";");
}

function hashFromString(value) {
  let hash = 0;

  for (const char of value) {
    hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  }

  return hash;
}

function applyDemoState() {
  if (demoMode === "compose") {
    state.composing = true;
    state.draft = "阿嬷，今天先把 GUI 写好，等会儿再把真正的 agent 接进来。";
    return;
  }

  if (demoMode === "answer") {
    state.conversations = [
      ...state.conversations,
      {
        id: createId(),
        question: "阿嬷，这套前端已经会叠信纸了，下一步应该先接流式输出还是历史持久化？",
        answer:
          "若想让它更像真的回信，先接流式输出会更有呼吸感；若想把往来留住，再补历史持久化。\n两者都适合这张纸，只是先后不同。",
        createdAt: new Date().toISOString(),
      },
    ];
    saveConversations();
    return;
  }

  if (demoMode === "history") {
    state.historyOpen = true;
    state.conversations = [
      ...state.conversations,
      {
        id: createId(),
        question: "阿嬷，如果以后这里接入多轮对话，信匣还能继续保留这种旧信纸的感觉吗？",
        answer:
          "当然能。\n外面仍是旧纸与花朵，里面只需悄悄换成真正的 agent 记忆。\n形式不必变，灵魂会慢慢长出来。",
        createdAt: new Date().toISOString(),
      },
    ];
    saveConversations();
  }
}

function exportConversation(conversation) {
  const ts = conversation.createdAt.slice(0, 19).replace(/[T:]/g, "-");

  // Build a print-friendly element matching the letter style
  const el = document.createElement("div");
  el.style.cssText = "padding:40px;max-width:800px;margin:0 auto;font-family:'Noto Serif SC','Songti SC',serif;color:#333;";
  el.innerHTML = `
    <div style="display:flex;justify-content:space-between;color:#666;font-size:14px;border-bottom:1px solid #ddd;padding-bottom:10px;margin-bottom:20px;">
      <span>来信</span>
      <span>${escapeHtml(formatHistoryDate(conversation.createdAt))}</span>
    </div>
    <div style="font-size:16px;line-height:2;white-space:pre-wrap;margin-bottom:28px;">${escapeHtml(conversation.question).replace(/\n/g, "<br />")}</div>
    <hr style="border:none;border-top:1px dashed #ccc;margin:28px 0;" />
    <div style="display:flex;justify-content:space-between;color:#666;font-size:14px;border-bottom:1px solid #ddd;padding-bottom:10px;margin-bottom:20px;">
      <span>回信</span>
      <span></span>
    </div>
    <div style="font-size:16px;line-height:2;white-space:pre-wrap;">${escapeHtml(conversation.pending ? "这封回信还在慢慢写。" : conversation.answer).replace(/\n/g, "<br />")}</div>
  `;

  // Use html2pdf to auto-save as PDF
  const opt = {
    margin: [15, 15],
    filename: `情书-${ts}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
    pagebreak: { mode: "avoid-all" },
  };
  html2pdf().set(opt).from(el).save();
}
