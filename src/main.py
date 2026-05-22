from __future__ import annotations

import asyncio

from src.bootstrap import bootstrap
from src.shared import get_logger


async def main() -> None:
    log = get_logger("main")
    app = bootstrap()
    worker_task = asyncio.create_task(app.worker.start())

    user_message = app.gateway.parse_args()
    log.info("Starting with message: %s", user_message)

    try:
        result = await app.gateway.submit(user_message)
        if result.status == "done":
            print(f"\n✓ Task completed: {result.id}")
            print(f"  Result: {result.result}")
        else:
            print(f"\n✗ Task failed: {result.id}")
            print(f"  Error: {result.error}")
    finally:
        app.worker.stop()
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
