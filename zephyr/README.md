MicroPython port to Zephyr RTOS for the Seeed Studio XIAO BLE NRF52840 Sense board
===============================

Initializing your build environment
--------
    $ git submodule update
    $ cd submodules/micropython
    $ git submodule update --init lib/micropython-lib
    $ cd ../../zephyr

Building
--------
Once Zephyr is ready to use you can build this MicroPython port just like any
other Zephyr application. You can do this anywhere in your file system, it does
not have to be in the `ports/zephyr` directory. Assuming you have cloned this board port
repository into your home directory, you can build the Zephyr port
for a xiao_ble_nrf42840_sense board like this:

    $ west build -b xiao_ble/nrf52840/sense ~/micropython-xiao_ble_nrf52840_sense/zephyr

Running
-------

To flash the resulting firmware to your board, press the RESET button two times and copy
`build/zephyr/zephyr.uf2` to the XIAO_BLE drive presented by the board.

Peripheral names
----------------

led0 = &led0;
led1 = &led1;
led2 = &led2;
pwm-led0 = &pwm_led0;
bootloader-led0 = &led0;
mcuboot-led0 = &led0;
watchdog0 = &wdt0;
    
lsm6ds3tr_c: name of LSM6DS3TR-C sensor on i2c0

Quick example
-------------

To blink an LED:

    import time
    from machine import Pin

    LED = Pin(("gpiob", 21), Pin.OUT)
    while True:
        LED.value(1)
        time.sleep(0.5)
        LED.value(0)
        time.sleep(0.5)

The above code uses an LED location for a FRDM-K64F board (port B, pin 21;
following Zephyr conventions port are identified by their devicetree node
label. You will need to adjust it for another board (using board's reference
materials). To execute the above sample, copy it to clipboard, in MicroPython
REPL enter "paste mode" using Ctrl+E, paste clipboard, press Ctrl+D to finish
paste mode and start execution.

To respond to Pin change IRQs, on a FRDM-K64F board run:

    from machine import Pin

    SW2 = Pin(("gpioc", 6), Pin.IN)
    SW3 = Pin(("gpioa", 4), Pin.IN)

    SW2.irq(lambda t: print("SW2 changed"))
    SW3.irq(lambda t: print("SW3 changed"))

    while True:
        pass

Example of using I2C to scan for I2C slaves:

    from machine import I2C

    i2c = I2C("i2c0")
    i2c.scan()

Example of using SPI to write a buffer to the MOSI pin:

    from machine import SPI

    spi = SPI("spi0")
    spi.init(baudrate=500000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB)
    spi.write(b'abcd')

