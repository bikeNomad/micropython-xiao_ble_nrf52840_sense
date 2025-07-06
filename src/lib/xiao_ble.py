"""
Utility functions for the Seeed Studio XIAO BLE NRF52840 SENSE board.
"""

from machine import Pin
from micropython import const
HAS_ADC = False
try:
    from machine import ADC
    HAS_ADC = True
except ImportError:
    pass

BLUE_LED_PIN = const(('gpio0', 6))  # active LOW
RED_LED_PIN = const(('gpio0', 26))  # active LOW
GREEN_LED_PIN = const(('gpio0', 30))  # active LOW
ACCEL_INT_PIN = const(('gpio0', 11))  # input, from LSM6DS IMU
# set LOW to read battery via AIN7, High-Z otherwise
READ_BAT_PIN = const(('gpio0', 14))
# set LOW to charge at 100mA, open circuit=50mA
HICHG_PIN = const(('gpio0', 13))
CHG_N_PIN = const(('gpio0', 17))   # input, LOW when charging
# HIGH to power MSM261D3526H1CPM PDM microphone
MIC_POWER_PIN = const(('gpio1', 10))

# Pins on J2
D0_PIN = const(('gpio0', 2))  # P0.02, J2/1
D1_PIN = const(('gpio0', 3))  # P0.03, J2/2
D2_PIN = const(('gpio0', 28))  # P0.28, J2/3
D3_PIN = const(('gpio0', 29))  # P0.29, J2/4
D4_PIN = const(('gpio0', 4))  # P0.04, J2/5
D5_PIN = const(('gpio0', 5))  # P0.05, J2/6
D6_PIN = const(('gpio1', 11))  # P1.11, J2/7

# Pins on J1
D7_PIN = const(('gpio1', 12))  # P1.12, J1/1
D8_PIN = const(('gpio1', 13))  # P1.13, J1/2
D9_PIN = const(('gpio1', 14))  # P1.14, J1/3
D10_PIN = const(('gpio1', 15))  # P1.15, J1/4


if HAS_ADC:
    # Pins on J2
    A0_PIN = const(('adc', 0))  # J2/1
    A1_PIN = const(('adc', 1))  # J2/2
    A4_PIN = const(('adc', 4))  # J2/3
    A5_PIN = const(('adc', 5))  # J2/4
    A2_PIN = const(('adc', 2))  # J2/5
    A3_PIN = const(('adc', 3))  # J2/6
    # Internal
    AIN7_BAT_PIN = const(('adc', 7))
    # 1M / 512k divider
    BATTERY_V_SCALE = const(1512/512/1000)

    def battery_mv() -> int:
        read_bat_pin = Pin(READ_BAT_PIN, Pin.OUT, value=0)
        adc = ADC(AIN7_BAT_PIN)
        val = adc.read_uv()
        read_bat_pin.init(Pin.IN)  # High-Z
        return int(val * BATTERY_V_SCALE)
else:
    def battery_mv() -> int:
        return 0


def is_battery_charging() -> bool:
    return Pin(CHG_N_PIN, Pin.IN).value() == 0


def charge_current_high(hi: bool):
    if hi:
        Pin(HICHG_PIN, Pin.OUT, value=0)
    else:
        Pin(HICHG_PIN, Pin.IN)

# Initialize pins to high-Z
Pin(READ_BAT_PIN, Pin.IN)
Pin(HICHG_PIN, Pin.IN)
