#!/usr/bin/sudo python
import gpioutil as gu
import RPi.GPIO as gpio

pins = {
    'LED power':    gu.Pin(7,             gpio.OUT, gpio.LOW),
    'PIR power':    gu.Pin(gu.Pin.VOLT,   gpio.OUT, gpio.HIGH),
    'Button power': gu.Pin(gu.Pin.VOLT,   gpio.OUT, gpio.HIGH),
    'PIR Signal':   gu.Pin(25,            gpio.IN),
    'Button in':    gu.Pin(21,            gpio.IN),
    'Button out':   gu.Pin(gu.Pin.GROUND, gpio.IN)
    # will 'button out' fry coming right from volt?

    # Ground wires are not listed.
    }

gu.setup_all(pins)

import subprocess
def play_sound(relative_path):
    subprocess.call(["aplay",  "sounds/{!s}".format(relative_path)])

state={}
state.on = False
state.led_on = True
state.button_depressed = False

def update(state):
    if gu.read(pins['Button in']):
        if not state.button_depressed:
            state.button_depressed = True
        else:
            print '''I don't think I should ever get here'''
            state.button_depressed = False
    else:
        state.button_depressed = False

def toggle(state):
    if state.on:
        gu.set_pin(pins['LED power'], gpio.LOW)
        play_sound("deactivate.wav")
    else:
        gu.set_pin(pins['LED power'], gpio.HIGH)
        play_sound("activate.wav")

    state.on = not state.on


def loop(state):
    update(state)
    if state.button_depressed:
        toggle(state)
    if state.on:
        if gu.read(
        for i in range(5):
            print 'Toggling LED on pin {}'.format(pins['LED power'].number)
            gu.toggle(pins['LED power'])
            time.sleep(1)
        print 'Playing siren'
        play_sound("police_s.wav")
    else:









if __name__ == '__main__':
    print 'Welcome to PiSnort!'
    play_sound("welcome.wav")

    print 'Importing libraries...',
    import time
    print 'Done.'

    try:
        while True:
            loop(state)
    except KeyboardInterrupt:
        print '\n\nCaught SIGINT'
        print 'Exiting.'
        gpio.cleanup()
