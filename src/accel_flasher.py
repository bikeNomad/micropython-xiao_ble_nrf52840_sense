"""
Micropython module to monitor the acceleration value of the on-board LSM6DSTR3 accelerometer.
When the X acceleration value changes by more than THRESHOLD, flash both the on-board RGB LED
and an external LED triggered by the D0 pin going HIGH.
"""

from time import sleep_ms
from micropython import const
from machine import I2C, Pin, lightsleep
import lsm6ds
from xiao_ble import BLUE_LED_PIN, RED_LED_PIN, GREEN_LED_PIN, D0_PIN, ACCEL_INT_PIN

blue_led = Pin(BLUE_LED_PIN, Pin.OUT, value=1)
green_led = Pin(GREEN_LED_PIN, Pin.OUT, value=1)
red_led = Pin(RED_LED_PIN, Pin.OUT, value=1)
external_white_led = Pin(D0_PIN, Pin.OUT, value=0)
interrupt_pin = Pin(ACCEL_INT_PIN, Pin.IN)

DEFAULT_THRESHOLD_MG = 500
DEFAULT_DURATION = 100  # ms
DURATION_SAMPLES = 2    # 19ms
NO_ARGS = const(())


def white_led_on():
    blue_led.value(0)
    green_led.value(0)
    red_led.value(0)
    external_white_led.value(1)


def white_led_off():
    blue_led.value(1)
    green_led.value(1)
    red_led.value(1)
    external_white_led.value(0)


def run(threshold=DEFAULT_THRESHOLD_MG, duration=DEFAULT_DURATION, duration_samples=DURATION_SAMPLES):
    i2c = I2C("i2c0")
    lsm = lsm6ds.LSM6DS3(
        i2c, accel_mode=lsm6ds.NORMAL_MODE_104HZ, gyro_mode=lsm6ds.POWER_DOWN
    )
    lsm.accel_fs_g = 4
    if threshold > lsm.accel_fs_g * 1000:
        print(f"warning: threshold {threshold}mg exceeds max {lsm.accel_fs_g * 1000}mg")
        threshold = lsm.accel_fs_g * 1000

    lsm.set_wakeup_threshold(threshold, duration_samples=duration_samples)
    lsm.enable_wakeup_interrupt(True)
    interrupt_occurred = False
    wus = lsm.wakeup_sources  # cache
    xwu = lsm6ds.X_WU  # cache

    def motion_callback(pin):
        nonlocal interrupt_occurred
        nonlocal wus, xwu
        interrupt_occurred = True
        if wus() & xwu:
            white_led_on()
            sleep_ms(duration)
            white_led_off()

    interrupt_pin.irq(trigger=Pin.IRQ_RISING, handler=motion_callback)
    print("Monitoring started.")
    try:
        while True:
            if interrupt_occurred:
                interrupt_occurred = False

                if lsm.wakeup_detected():
                    wake_source = wus()
                    print(f"Wake-up detected: {wake_source:b}")

            lightsleep(10000)

    except KeyboardInterrupt:
        # clean up
        lsm.enable_wakeup_interrupt(False)
        interrupt_pin.irq(trigger=Pin.IRQ_RISING, handler=None)
        white_led_off()
        print("Monitoring stopped.")
