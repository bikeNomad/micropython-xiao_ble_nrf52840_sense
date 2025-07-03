build-micropython: asyncio-lib
	west build -b xiao_ble/nrf52840/sense $(CWD)

clean:
	rm -rf build

asyncio-lib:
	mkdir -p modules/primitives
	cp ../submodules/micropython-async/v3/primitives/*.py modules/primitives/
	mkdir -p modules/threadsafe
	cp ../submodules/micropython-async/v3/threadsafe/*.py modules/threadsafe

flash:
	-cp build/zephyr/zephyr.uf2 /Volumes/XIAO-SENSE # Mac only

.PHONY: asyncio-lib build-micropython