import sys
import time
import asyncio
import aiorepl
sys.path.append("lib")

import accel_flasher

def set_global_exception():
    def handle_exception(loop, context):
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    set_global_exception()

    await asyncio.gather(
        accel_flasher.task(threshold=10000, duration=50),
        aiorepl.task()
    )

try:
    asyncio.run(main())
finally:
    try:
        time.sleep(3)
        asyncio.new_event_loop()
    except KeyboardInterrupt:
        raise
