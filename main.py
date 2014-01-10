#!/usr/bin/sudo python

import gpioutil as gu
import RPi.GPIO as gpio
import random                   # For randomizing sound files
import time                     # To delay sound playing

import logging

logging.basicConfig(
    filename='log',
    format='%(asctime)s (%(name)s) [%(funcName)s] %(levelname)s: %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(levelname)-8s: %(message)s'))
logging.getLogger('').addHandler(console)

log = logging.getLogger('')
log.setLevel(logging.DEBUG)

def play_sound(relative_path):
    log = logging.getLogger('sounds')
    log.info('Playing sound: "%s"', relative_path)
    start_process(['aplay', '--quiet', 'sounds/{!s}'.format(relative_path)])

import subprocess

global child_processes
child_processes = set()

def start_process(cmd):
    child = subprocess.Popen(cmd)
    child_processes.add(child)

def gc_processes():
    for child in list(child_processes):
        child.poll()
        if child.returncode is not None:
            log.debug('Removing process %d from the set.')
            child_processes.remove(child)
            if child.returncode is not 0:
                log.error('Process %d ended abnormally; exit code %d', child.pid, child.returncode)

def kill_child_processes():
    gc_processes()
    for child in child_processes:
        try:
            log.info('Forcing process %d to exit', child.pid)
            child.terminate()
        except:
            log.error('Unable to kill child process %d', pid)

import atexit
atexit.register(kill_child_processes)

if __name__ == '__main__':
    log.info('Execution started.')

    print 'Welcome to PiSnort!'
    play_sound('system/welcome.wav')

    class State: pass
    state=State()
    state.testing               = True
    state.on                    = False
    state.button_depressed      = False
    state.button_depressed__old = True
    state.motion_detected       = False

    gpio.setmode(gpio.BCM)
    
    pins = {
        'LED power':    gu.Pin(4,           gpio.OUT, gpio.LOW),
        'PIR power':    gu.Pin(gu.Pin.VOLT, gpio.OUT),
        'Button power': gu.Pin(gu.Pin.VOLT, gpio.OUT),
        'PIR Signal':   gu.Pin(2,           gpio.IN,  pud=gpio.PUD_DOWN),
        'Button in':    gu.Pin(8,           gpio.IN,  pud=gpio.PUD_DOWN),
        'Button out':   gu.Pin(7,           gpio.IN,  pud=gpio.PUD_DOWN)
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
            if not gu.read_pin(pins['PIR Signal']):
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
                choices = ['recordings/'+key for key in snorts if bool(snorts[key][0])]
                soundfile = random.choice(choices)
                log.info('Waiting ten seconds to play sound.')
                time.sleep(5)
                
                play_sound(soundfile)
                
                log.info('Waiting five minutes to continue execution')
                time.sleep(10)
    except KeyboardInterrupt:
        print '\n\nCaught SIGINT'
        log.info('Process ended with C-c.')

    print 'Exiting.'
    log.info('Cleaning up GPIO...')
    gpio.cleanup()
    log.info('Cleaning up GPIO... Done.')
