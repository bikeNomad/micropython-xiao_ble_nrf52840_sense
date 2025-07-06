# Copied from pimoroni: https://github.com/pimoroni/lsm6ds3-micropython/blob/main/src/lsm6ds3.py
# Edited to use struct and provide status

import asyncio
from struct import pack, unpack
from micropython import const

# Registers
WHO_AM_I = const(0x0F)
CTRL1_XL = const(0x10) # accelerometer config
CTRL2_G = const(0x11) # gyro config
CTRL3_C = const(0x12)
CTRL8_XL = const(0x17)
CTRL10_C = const(0x19)
STATUS_REG = const(0x1E)

# This is the start of the data registers for the Gyro and Accelerometer
# There are 12 Bytes in total starting at 0x23 and ending at 0x2D
OUTX_L_G = const(0x22)
OUTX_L_XL = const(0x28)

STEP_COUNTER_L = const(0x4B)
STEP_COUNTER_H = const(0x4C)
TAP_SRC = const(0x1C)
TAP_CFG = const(0x58)
FUNC_SRC1 = const(0x53)
FUNC_SRC2 = const(0x54)
TAP_THS_6D = const(0x59)
FREE_FALL = const(0x5D)
WAKE_UP_THS = const(0x5B)
WAKE_UP_SRC = const(0x1B)
INT_DUR2 = const(0x5A)

# CONFIG DATA
NORMAL_MODE_104HZ = const(0x40)
NORMAL_MODE_208HZ = const(0x50)
PERFORMANCE_MODE_416HZ = const(0x60)
LOW_POWER_26HZ = const(0x02)
SET_FUNC_EN = const(0xBD)
RESET_STEPS = const(0x02)
TAP_EN_XYZ = const(0x8E)
TAP_THRESHOLD = const(0x02)
DOUBLE_TAP_EN = const(0x80)
DOUBLE_TAP_DUR = const(0x20)

ACCEL_FMT = "<hhh"
GYRO_FMT = "<hhh"
COMBO_FMT = "<hhhhhh"


class LSM6DS3:
    def __init__(self, i2c, address=0x6A, mode=NORMAL_MODE_104HZ):
        self.bus = i2c
        self.address = address
        self.mode = mode

        # Set gyro mode/enable
        self.bus.writeto_mem(self.address, CTRL2_G, bytearray([self.mode]))

        # Set accel mode/enable
        self.bus.writeto_mem(self.address, CTRL1_XL, bytearray([self.mode]))

        # Send the reset bit to clear the pedometer step count
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([RESET_STEPS]))

        # Enable sensor functions (Tap, Tilt, Significant Motion)
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([SET_FUNC_EN]))

        # Enable X Y Z Tap Detection
        self.bus.writeto_mem(self.address, TAP_CFG, bytearray([TAP_EN_XYZ]))

        # Enable Double tap
        self.bus.writeto_mem(self.address, WAKE_UP_THS, bytearray([DOUBLE_TAP_EN]))

        # Set tap threshold
        self.bus.writeto_mem(self.address, TAP_THS_6D, bytearray([TAP_THRESHOLD]))

        # Set double tap max time gap
        self.bus.writeto_mem(self.address, INT_DUR2, bytearray([DOUBLE_TAP_DUR]))

        # enable BDU and IF_INC
        self.bus.writeto_mem(self.address, CTRL3_C, bytearray([0b0100_0100]))

    def _read_reg(self, reg, size):
        return self.bus.readfrom_mem(self.address, reg, size)
    
    def set_hp_filter(self, mode):
        self.bus.writeto_mem(self.address, CTRL8_XL, bytearray([self.mode]))

    def get_readings(self) -> tuple[int, int, int, int, int, int]:
        # Read 12 bytes starting from 0x22. This covers the XYZ data for gyro and accel
        # return: (GX,GY,GZ,XLX,XLY,XLZ)
        data = self._read_reg(OUTX_L_G, 12)
        return unpack(COMBO_FMT, data)

    def get_accel_readings(self) -> tuple[int, int, int]:
        # Read 6 bytes starting at 0x28. This is the XYZ data for the accelerometer.
        data = self._read_reg(OUTX_L_XL, 6)
        return unpack(ACCEL_FMT, data)

    def get_gyro_readings(self) -> tuple[int, int, int]:
        # Read 6 bytes starting from 0x22. This covers the XYZ data for gyro
        data = self._read_reg(OUTX_L_G, 6)
        return unpack(GYRO_FMT, data)

    def get_step_count(self):
        data = self._read_reg(STEP_COUNTER_L, 2)
        steps = unpack("<h", data)[0]
        return steps

    def reset_step_count(self):
        # Send the reset bit
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([RESET_STEPS]))
        # Enable functions again
        self.bus.writeto_mem(self.address, CTRL10_C, bytearray([SET_FUNC_EN]))

    def tilt_detected(self):
        tilt = self._read_reg(FUNC_SRC1, 1)
        tilt = (tilt[0] >> 5) & 0b1
        return tilt

    def sig_motion_detected(self):
        sig = self._read_reg(FUNC_SRC1, 1)
        sig = (sig[0] >> 6) & 0b1
        return sig

    def single_tap_detected(self):
        s = self._read_reg(TAP_SRC, 1)
        s = (s[0] >> 5) & 0b1
        return s

    def double_tap_detected(self):
        d = self._read_reg(TAP_SRC, 1)
        d = (d[0] >> 4) & 0b1
        return d

    def freefall_detected(self):
        fall = self._read_reg(WAKE_UP_SRC, 1)
        fall = fall[0] >> 5
        return fall

    def accel_data_ready(self):
        status = self._read_reg(STATUS_REG, 1)
        return status[0] & 1

    def gyro_data_ready(self):
        status = self._read_reg(STATUS_REG, 1)
        return status[0] & 2

    def all_data_ready(self):
        status = self._read_reg(STATUS_REG, 1)
        return (status[0] & 3) == 3