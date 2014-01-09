#!/usr/bin/sudo python

import gpioutil as gu
import RPi.GPIO as gpio
import subprocess               # For playing sound files
import random                   # For randomizing sound files
import time                     # To delay sound playing
import logging

import logging.config
logging.config.fileConfig('logging.conf')

def play_sound(relative_path):
    log = logging.getLogger('sounds')
    log.info('Playing sound: %s', relative_path)
    subprocess.call(['aplay',  'sounds/{!s}'.format(relative_path)])

if __name__ == '__main__':
    log = logging.getLogger('root')
    log.info('Execution started.')

    print 'Welcome to PiSnort!'
    play_sound('system/welcome.wav')

    class State: pass
    state=State()
    state.testing = True
    state.on = False
    state.led_on = True
    state.button_depressed = False
    state.motion_detected = False

    gpio.setmode(gpio.BCM)
    
    pins = {
        'LED power':    gu.Pin(4,           gpio.OUT, gpio.LOW),
        'PIR power':    gu.Pin(gu.Pin.VOLT, gpio.OUT, gpio.HIGH),
        'Button power': gu.Pin(gu.Pin.VOLT, gpio.OUT, gpio.HIGH),
        'PIR Signal':   gu.Pin(2,           gpio.IN),
        'Button in':    gu.Pin(8,           gpio.IN),
        'Button out':   gu.Pin(7,           gpio.IN)
      }
    
    gu.setup_all(pins)

    snorts = {'record2snort2.wav':     ('some criterion'),
              'record3snort1.wav':     ('some criterion'),
              'record3snort2.wav':     ('some criterion'),
              'record4snort1.wav':     ('some criterion'),
              'record4snort2.wav':     ('some criterion'),
              'recorded snort1-3.wav': ('some criterion'),
              'recorded snort1.wav':   ('some criterion'),
              'recorded snort2.wav':   ('some criterion')}
  
    log.info('Beginning main loop.')
    try:
        while True:
            log.debug('Executing loop')
            log.debug('Updating state...')
            if gu.read_pin(pins['Button in']):
                if not state.button_depressed:
                    log.debug('Caught button state change.')
                    state.button_depressed = True
            else:
                state.button_depressed = False
            if gu.read_pin(pins['PIR Signal']):
                log.info('Motion detected!')
                state.motion_detected = True
            else:
                state.motion_detected = False
            log.debug('Updating state... Done.')
            if state.button_depressed:
                log.debug('Toggling state...')
                  
                if state.on:
                    log.debug('Turning LED OFF')
                    gu.set_pin(pins['LED power'], gpio.LOW)
                    play_sound('system/deactivate.wav')
                else:
                    log.debug('Turning LED ON')
                    gu.set_pin(pins['LED power'], gpio.HIGH)
                    play_sound('system/activate.wav')
                  
                state.on = not state.on
                log.debug('Toggling state... Done.')
            if state.testing:
                for i in range(10):
                    print 'Toggling LED on pin {}'.format(pins['LED power'].number)
                    gu.toggle(pins['LED power'])
                    time.sleep(1)
                print 'Diagnostic complete.'
                play_sound('system/diagnostic.wav')
                state.testing = False
            elif state.on and state.motion_detected:
                choices = [key for key in snorts if bool(snorts[key][0])]
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
