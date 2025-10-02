# Copied from pimoroni: https://github.com/pimoroni/lsm6ds3-micropython/blob/main/src/lsm6ds3.py
# Edited to use struct and provide status

from struct import unpack
from micropython import const

# Registers
INT1_CTRL = const(0x0D)  # Interrupt 1 control register
WHO_AM_I = const(0x0F)
CTRL1_XL = const(0x10)  # accelerometer config
CTRL2_G = const(0x11)  # gyro config
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
WAKE_UP_DUR = const(0x5C)  # Wake-up duration
MD1_CFG = const(0x5E)  # INT1 pin behavior configuration

# CONFIG DATA
# mode: written to CTRL2_G and CTRL1_XL
NORMAL_MODE_104HZ = const(0x40)
NORMAL_MODE_208HZ = const(0x50)
PERFORMANCE_MODE_416HZ = const(0x60)
LOW_POWER_26HZ = const(0x20)
POWER_DOWN = const(0x00)

SET_FUNC_EN = const(0xBD)
RESET_STEPS = const(0x02)
TAP_EN_XYZ = const(0x8E)
TAP_THRESHOLD = const(0x02)
DOUBLE_TAP_EN = const(0x80)
DOUBLE_TAP_DUR = const(0x20)

# Interrupt enable bits for INT1_CTRL
INT1_DRDY_XL = const(0x01)  # Data ready interrupt
INT1_WU = const(0x20)  # Wake-up interrupt

# MD1_CFG bits
INT1_WU_CFG = const(0x20)  # Route wake-up to INT1

WAKE_UP_THS_LSB_SCALE = const(15.625)  # 1000/64

# WAKE_UP_SRC bits
FF_IA = const(0x20)
SLEEP_STATE_IA = const(0x10)
WU_IA = const(0x08)
X_WU = const(0x04)
Y_WU = const(0x02)
Z_WU = const(0x01)


ACCEL_FMT = "<hhh"
GYRO_FMT = "<hhh"
COMBO_FMT = "<hhhhhh"


class LSM6DS3:
    _FS_DECODE = {  # CTRL1_XL
        0b0000: 2,
        0b0100: 16,
        0b1000: 4,
        0b1100: 8,
    }
    _FS_ENCODE = {
        2: 0b0000,
        16: 0b0100,
        4: 0b1000,
        8: 0b1100,
    }

    def _read_reg(self, reg):
        """Reads 1 byte from the given register.
        Returns the integer value."""
        return self.bus.readfrom_mem(self.address, reg, 1)[0]

    def _read_regs(self, reg, size):
        """Reads size bytes from the given register.
        Returns a bytearray of the read data."""
        return self.bus.readfrom_mem(self.address, reg, size)

    def _write_reg(self, reg, *data):
        """Writes one or more bytes to the given register."""
        self.bus.writeto_mem(self.address, reg, bytearray(data))

    def __init__(
        self,
        i2c,
        address=0x6A,
        accel_mode=NORMAL_MODE_104HZ,
        gyro_mode=NORMAL_MODE_104HZ,
    ):
        self.bus = i2c
        self.address = address
        self.accel_mode = accel_mode
        self.gyro_mode = gyro_mode

        # Send the reset bit to clear the pedometer step count
        self._write_reg(CTRL10_C, RESET_STEPS)

        # Enable sensor functions (Tap, Tilt, Significant Motion)
        self._write_reg(CTRL10_C, SET_FUNC_EN)

        # Enable X Y Z Tap Detection
        self._write_reg(TAP_CFG, TAP_EN_XYZ)

        # Enable Double tap
        self._write_reg(WAKE_UP_THS, DOUBLE_TAP_EN)

        # Set tap threshold
        self._write_reg(TAP_THS_6D, TAP_THRESHOLD)

        # Set double tap max time gap
        self._write_reg(INT_DUR2, DOUBLE_TAP_DUR)

        # enable BDU and IF_INC
        self._write_reg(CTRL3_C, 0b0100_0100)

    @property
    def accel_mode(self):
        return self._accel_mode

    @accel_mode.setter
    def accel_mode(self, mode):
        self._accel_mode = mode
        self._accel_fs_g = self._FS_DECODE[mode & 0b1100]
        self._write_reg(CTRL1_XL, mode)

    @property
    def accel_fs_g(self):
        return self._accel_fs_g

    @accel_fs_g.setter
    def accel_fs_g(self, fs_g):
        self._accel_fs_g = fs_g
        self.accel_mode = (self._accel_mode & 0b11110011) | self._FS_ENCODE[fs_g]

    @property
    def gyro_mode(self):
        return self._gyro_mode

    @gyro_mode.setter
    def gyro_mode(self, mode):
        self._gyro_mode = mode
        self._write_reg(CTRL2_G, mode)

    def set_hp_filter(self, mode):
        self._write_reg(CTRL8_XL, mode)

    def get_readings(self) -> tuple[int, int, int, int, int, int]:
        # Read 12 bytes starting from 0x22. This covers the XYZ data for gyro and accel
        # return: (GX,GY,GZ,XLX,XLY,XLZ)
        data = self._read_regs(OUTX_L_G, 12)
        return unpack(COMBO_FMT, data)

    def get_accel_readings(self) -> tuple[int, int, int]:
        # Read 6 bytes starting at 0x28. This is the XYZ data for the accelerometer.
        data = self._read_regs(OUTX_L_XL, 6)
        return unpack(ACCEL_FMT, data)

    def get_gyro_readings(self) -> tuple[int, int, int]:
        # Read 6 bytes starting from 0x22. This covers the XYZ data for gyro
        data = self._read_regs(OUTX_L_G, 6)
        return unpack(GYRO_FMT, data)

    def get_step_count(self):
        data = self._read_regs(STEP_COUNTER_L, 2)
        steps = unpack("<h", data)[0]
        return steps

    def reset_step_count(self):
        # Send the reset bit
        self._write_reg(CTRL10_C, RESET_STEPS)
        # Enable functions again
        self._write_reg(CTRL10_C, SET_FUNC_EN)

    def tilt_detected(self):
        tilt = self._read_reg(FUNC_SRC1)
        tilt = (tilt >> 5) & 0b1
        return tilt

    def sig_motion_detected(self):
        sig = self._read_reg(FUNC_SRC1)
        sig = (sig >> 6) & 0b1
        return sig

    def single_tap_detected(self):
        s = self._read_reg(TAP_SRC)
        s = (s >> 5) & 0b1
        return s

    def double_tap_detected(self):
        d = self._read_reg(TAP_SRC)
        d = (d >> 4) & 0b1
        return d

    def freefall_detected(self):
        fall = self._read_reg(WAKE_UP_SRC)
        fall = fall >> 5
        return fall

    def accel_data_ready(self):
        status = self._read_reg(STATUS_REG)
        return status & 1

    def gyro_data_ready(self):
        status = self._read_reg(STATUS_REG)
        return status & 2

    def all_data_ready(self):
        status = self._read_reg(STATUS_REG)
        return (status & 3) == 3

    def set_wakeup_threshold(self, threshold_mg, duration_samples=1, use_hpf=False):
        """
        Set acceleration threshold for wake-up interrupt

        Args:
          threshold_mg: Threshold in milliG (mg).
          duration_samples: Number of consecutive samples above threshold (1-3)
        """
        # Convert mg to register value (LSB = _accel_fs_g / 64)
        reg_lsb_mg = self._accel_fs_g * WAKE_UP_THS_LSB_SCALE
        threshold_reg = min(63, max(1, int(threshold_mg / reg_lsb_mg)))

        # Configure wake-up threshold register (0x5B)
        # Bit 7: Single/Double tap (0 = single)
        # Bits 5-0: Wake-up threshold
        wake_up_ths_val = self._read_reg(WAKE_UP_THS) & 0x80
        self._write_reg(WAKE_UP_THS, wake_up_ths_val | (threshold_reg & 0x3F))

        # Configure wake-up duration (0x5C)
        # Bits 6-5: WAKE_DUR (number of samples)
        # Bits 3-0: SLEEP_DUR (not used for wake-up)
        wake_dur_val = min(3, max(0, duration_samples - 1))
        wake_dur_reg = self._read_reg(WAKE_UP_DUR) & 0x9F
        wake_dur_reg |= (wake_dur_val << 5) & 0x60
        self._write_reg(WAKE_UP_DUR, wake_dur_reg)

        # Enable interrupts in TAP_CFG register (0x58)
        # Bit 7: INTERRUPTS_ENABLE = 1
        # Bit 4: SLOPE_FDS (1:HPF, 0:SLOPE)
        # Keep existing tap configuration
        current_tap_cfg = self._read_reg(TAP_CFG)
        new_tap_cfg = current_tap_cfg | 0x80  # Set bit 7
        if use_hpf:
            new_tap_cfg |= 0x10
        else:
            new_tap_cfg &= ~0x10
        self._write_reg(TAP_CFG, new_tap_cfg)

        print(f"Set wake-up threshold: {threshold_reg * reg_lsb_mg:.1f}mg")

    def enable_wakeup_interrupt(self, enable=True):
        """Enable/disable wake-up interrupt on INT1 pin"""
        md1_reg_val = self._read_reg(MD1_CFG)
        if enable:
            # Route wake-up interrupt to INT1 pin (MD1_CFG register 0x5E)
            self._write_reg(MD1_CFG, md1_reg_val | INT1_WU_CFG)
            print("Wake-up interrupt enabled on INT1")
        else:
            # Disable wake-up interrupt routing
            self._write_reg(MD1_CFG, md1_reg_val & ~INT1_WU_CFG)
            print("Wake-up interrupt disabled")

    def wakeup_detected(self):
        """Check if wake-up event occurred"""
        wake_src = self._read_reg(WAKE_UP_SRC)
        return (wake_src >> 3) & 0x01  # WU_IA bit

    def get_wakeup_source(self):
        """Get which axis triggered wake-up"""
        wake_src = self._read_reg(WAKE_UP_SRC)
        return {
            "wake_up": (wake_src >> 3) & 0x01,
            "x_wake": (wake_src >> 2) & 0x01,
            "y_wake": (wake_src >> 1) & 0x01,
            "z_wake": wake_src & 0x01,
        }

    def wakeup_sources(self):
        return self._read_reg(WAKE_UP_SRC)
