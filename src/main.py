from __future__ import annotations

import asyncio

from src.bootstrap import bootstrap
from src.shared import get_logger
from src.shared.cli import print_header, print_result_fail, print_result_ok, print_task_bar


async def main() -> None:
    log = get_logger("main")
    app = bootstrap()
    worker_task = asyncio.create_task(app.worker.start())

    user_message = app.gateway.parse_args()

    print_header()
    print_task_bar(user_message)

    try:
        result = await app.gateway.submit(user_message)
        if result.status == "done":
            print_result_ok(result.id, result.result or "(no output)")
        else:
            print_result_fail(result.id, result.error)
    finally:
        app.worker.stop()
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
