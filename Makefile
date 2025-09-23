# Mac-specific makefile for now.
VARS_OLD := $(.VARIABLES)
HERE=$(PWD)
SRC_DIR=$(HERE)/src
LIB_DIR=$(SRC_DIR)/lib
MPY=$(HERE)/submodules/micropython
PORT_DIR=$(MPY)/ports/zephyr
# Get latest build directory
BUILD_DIR=$(shell ls -dt1 $(PORT_DIR)/build* | head -n 1)
ifeq ($(BUILD_DIR),)
	BUILD_DIR=$(PORT_DIR)/build
endif
BUILT_UF2=$(BUILD_DIR)/zephyr/zephyr.uf2

SOURCE_PY=$(SRC_DIR)/accel_flasher.py $(SRC_DIR)/main.py
LIB_PY=$(LIB_DIR)/*.py

# TODO Determine host OS

ifeq ($(OS),Windows_NT)
    # Commands specific to Windows
    PLATFORM := WINDOWS
else
    # Fallback to uname for Unix-like systems
    OS_NAME := $(shell uname)
    ifeq ($(OS_NAME),Darwin)
        PLATFORM := MACOS
    else ifeq ($(OS_NAME),Linux)
        PLATFORM := LINUX
    else
        PLATFORM := UNKNOWN
    endif
endif

ifeq ($(PLATFORM),MACOS)
	FLASH_CP_ARGS=-X
	FLASH_DRIVE_DEST=/Volumes/XIAO?SENSE
else
	$(error Unsupported platform)
endif


all: $(BUILT_UF2) copy_mpy

copy_mpy: format_filesystem install_asyncio_primitives
	mpremote cp $(SOURCE_PY) : + \
	cp $(LIB_PY) :lib

install_asyncio_primitives:
	mpremote mip install github:peterhinch/micropython-async/v3/primitives
 	mpremote mip install github:peterhinch/micropython-async/v3/threadsafe

clean:
	rm -rf $(PORT_DIR)/build*

$(BUILT_UF2):
	cd $(PORT_DIR) && west build -b xiao_ble/nrf52840/sense $(BUILD_DIR)

format_filesystem:
	mpremote run $(SRC_DIR)/make_vfs.py

flash: $(BUILT_UF2)
	-cp $(FLASH_CP_ARGS) $(BUILT_UF2) $(FLASH_DRIVE_DEST)
	sleep 5

program_bootloader:
	nrfjprog -f NRF52 --program $(HERE)/xiao_nrf52840_ble_sense_bootloader-0.9.2_s140_7.3.0.hex --recover --verify --reset

# Erase both MCU and external QSPI flash
erase:
	nrfjprog -f NRF52 --qspieraseall --eraseall

print_variables:
	$(foreach v, $(filter-out $(VARS_OLD) VARS_OLD,$(.VARIABLES)), \
	    $(info $(v) = $($(v))))