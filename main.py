#!/usr/bin/sudo python

import gpioutil as gu
import RPi.GPIO as gpio
import subprocess               # For playing sound files
import random                   # For randomizing sound files
import time                     # To delay sound playing
import logging

gpio.setmode(gpio.BOARD)

import logging.config
logging.config.fileConfig('logging.conf')

def play_sound(relative_path):
    log = logging.getLogger('sounds')
    log.info('Playing sound: %s', relative_path)
    subprocess.call(["aplay",  "sounds/{!s}".format(relative_path)])

if __name__ == '__main__':
    log = logging.getLogger('root')
    log.info('Execution started.')

    print 'Welcome to PiSnort!'
    play_sound("welcome.wav")

    state=object()
    state.testing = True
    state.on = False
    state.led_on = True
    state.button_depressed = False
    state.motion_detected = False

    pins = {
        'LED power':    gu.Pin(7,             gpio.OUT, gpio.LOW),
        'PIR power':    gu.Pin(gu.Pin.VOLT,   gpio.OUT, gpio.HIGH),
        'Button power': gu.Pin(gu.Pin.VOLT,   gpio.OUT, gpio.HIGH),
        'PIR Signal':   gu.Pin(25,            gpio.IN),
        'Button in':    gu.Pin(21,            gpio.IN),
        'Button out':   gu.Pin(gu.Pin.GROUND, gpio.IN)
        # will 'button out' fry coming right from volt?
      }
    
    gu.setup_all(pins)

    snorts = {('record2snort2.wav',     'some criterion'),
              ('record3snort1.wav',     'some criterion'),
              ('record3snort2.wav',     'some criterion'),
              ('record4snort1.wav',     'some criterion'),
              ('record4snort2.wav',     'some criterion'),
              ('recorded snort1-3.wav', 'some criterion'),
              ('recorded snort1.wav',   'some criterion'),
              ('recorded snort2.wav',   'some criterion')}
  
    log.info('Beginning main loop.')
    try:
        while True:
            log = logging.getLogger('root')
            log.debug('Executing loop')
              
            log.debug('Updating state...')
              
            # Check for changes in button state.  This logic should allow the
            # system to manage a toggle on/off button for the system state
            # using the momentary latch provided by the button.
            if gu.read_pin(pins['Button in']):
                if not state.button_depressed:
                    log.debug('Caught button state change.')
                    state.button_depressed = True
            else:
                state.button_depressed = False
              
            # Check for any input from the PIR.  If motion is detected, set
            # the appropriate flag.  (This can easily be collapsed to one
            # line, but is expanded here for clarity.)
            if gu.read_pin(pins['PIR Signal']):
                log.info('Motion detected!')
                state.motion_detected = True
            else:
                state.motion_detected = False
              
            log.debug('Updating state... Done.')
            
            if state.button_depressed:
                log = logging.getLogger('root')
                log.debug('Toggling state...')
                  
                if state.on:
                    log.debug('Turning LED OFF')
                    gu.set_pin(pins['LED power'], gpio.LOW)
                    play_sound("deactivate.wav")
                else:
                    log.debug('Turning LED ON')
                    gu.set_pin(pins['LED power'], gpio.HIGH)
                    play_sound("activate.wav")
                  
                state.on = not state.on
                log.debug('Toggling state... Done.')
              
            if state.testing:
                for i in range(5):
                    print 'Toggling LED on pin {}'.format(pins['LED power'].number)
                    gu.toggle(pins['LED power'])
                    time.sleep(1)
                print 'Playing siren'
                play_sound("police_s.wav")
            elif state.on and state.motion_detected:
                choices = [snorts[key][0] for key in snorts]
                soundfile = random.choice(choices)
                log.info('Waiting ten seconds to play sound.')
                time.sleep(10)
                play_sound(soundfile)
                log.info('Waiting five minutes to continue execution')
                time.sleep(600)
    except KeyboardInterrupt:
        log.info('Process ended with C-c C-c.')
        print '\n\nCaught SIGINT'
    finally:
        print 'Exiting.'
        log.info('Cleaning up GPIO...')
        gpio.cleanup()
        log.info('Cleaning up GPIO... Done.')
