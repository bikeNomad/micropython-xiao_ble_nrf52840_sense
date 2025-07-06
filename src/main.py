import sys
import asyncio
import aiorepl

import accel_flasher

sys.path.append("lib")

asyncio.run(aiorepl.task())
