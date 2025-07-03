import sys
sys.path.append("lib")

from micropython import const
import asyncio
from asyncio import sleep_ms
from time import ticks_us
from machine import I2C, Pin
from primitives import Delay_ms
import aiorepl
import lsm6ds
from xiao_ble_nrf52840 import BLUE_LED_PIN, RED_LED_PIN, GREEN_LED_PIN,

i2c = I2C("i2c0")
lsm = lsm6ds.LSM6DS3(i2c, mode=0x4C) # 208Hz, FS=4g

blue_led = Pin(BLUE_LED_PIN, Pin.OUT, value=1)
green_led = Pin(GREEN_LED_PIN, Pin.OUT, value=1)
red_led = Pin(RED_LED_PIN, Pin.OUT, value=1)

def white_led_on():
    blue_led.value(0)
    green_led.value(0)
    red_led.value(0)

def white_led_off():
    blue_led.value(1)
    green_led.value(1)
    red_led.value(1)

flash_delay = Delay_ms(white_led_off, (,), duration=100)

def flash_led():
    white_led_on()
    flash_delay.trigger()

THRESHOLD=const(10000)

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
    asyncio.create_task(test_accel(n))

asyncio.run(aiorepl.task())