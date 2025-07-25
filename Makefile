HERE=$(PWD)
SRC_DIR=$(HERE)/src
LIB_DIR=$(SRC_DIR)/lib
MPY=$(HERE)/submodules/micropython
PORT_DIR=$(MPY)/ports/zephyr
BUILT_UF2=$(PORT_DIR)/build/zephyr/zephyr.uf2

SOURCE_PY=$(SRC_DIR)/accel_flasher.py $(SRC_DIR)/main.py
LIB_PY=$(LIB_DIR)/*.py


all: $(BUILT_UF2) copy_mpy

copy_mpy: format_filesystem install_asyncio_primitives
	mpremote cp $(SOURCE_PY) : + \
	cp $(LIB_PY) :lib

install_asyncio_primitives:
	mpremote mip install github:peterhinch/micropython-async/v3/primitives
 	mpremote mip install github:peterhinch/micropython-async/v3/threadsafe

$(BUILT_UF2):
	cd $(PORT_DIR) && \
	rm -rf build && \
	west build -b xiao_ble/nrf52840/sense .

format_filesystem:
	mpremote run $(SRC_DIR)/make_vfs.py

flash: $(BUILT_UF2)
	-cp $(BUILT_UF2) /Volumes/XIAO_SENSE
	sleep 5