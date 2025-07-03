import sys
sys.path.append("lib")

from time import ticks_us
from machine import I2C, Pin
import asyncio
from asyncio import sleep_ms

import lsm6ds
i2c = I2C("i2c0")
lsm = lsm6ds.LSM6DS3(i2c, mode=0x5C) # 208Hz, FS=4g
# lsm.set_hp_filter(0b0100_0100) # ODR/9 = 208/9 = 23Hz, digital HPF
# lsm.set_hp_filter(0b0000_0100) # ODR/4 = 208/4 = 52Hz, slope filter
blue_led = Pin(('gpio0',6), Pin.OUT)
blue_led.value(1)

def flash_led(ms=100):
    async def flashit():
        blue_led.value(0)
        await sleep_ms(ms)
        blue_led.value(1)
    asyncio.create_task(flashit())

THRESHOLD=10000

async def test_accel(n):
    started = ticks_us()
    lastx = 0
    for _ in range(n):
        while not lsm.accel_data_ready():
            await sleep_ms(0)
        data = lsm.get_accel_readings()
        now = ticks_us()
        dx = abs(data[0] - lastx)
        lastx = data[0]
        if dx > THRESHOLD:
            flash_led()
        vals = [now-started, data[0], data[1], data[2], dx]
        print(','.join(map(str, vals)))
        await sleep_ms(1)


def ta(n):
    asyncio.run(test_accel(n))
