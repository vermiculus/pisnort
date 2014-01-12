#!/usr/bin/sudo python

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

log = logging.getLogger('')
log.addHandler(console)
log.setLevel(logging.DEBUG)

def play_sound(relative_path):
    log = logging.getLogger('sounds')
    log.info('Playing sound: "%s"', relative_path)
    start_process(['mplayer', '-msglevel', 'all=-1', 'sounds/{!s}'.format(relative_path)], 'Play sound {}'.format(relative_path))

import subprocess

global child_processes
child_processes = set()

def start_process(cmd, purpose=None):
    child = subprocess.Popen(cmd)
    child.snort_purpose = purpose
    child_processes.add(child)

def gc_processes():
    for child in list(child_processes):
        child.poll()
        if child.returncode is not None:
            log.debug('Removing process %d from the set.', child.pid)
            child_processes.remove(child)
            if child.returncode is not 0:
                log.error('Process %d ended abnormally; exit code %d; purpose: %s',
                          child.pid,
                          child.returncode,
                          child.snort_purpose)

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
atexit.register(logging.shutdown)

if __name__ == '__main__':
    log.info('Execution started.')

    print 'Welcome to PiSnort!'
    play_sound('system/welcome.wav')

    class State: pass
    state=State()
    state.testing              = True
    state.button_depressed     = False
    state.button_depressed_old = True
    state.motion_detected      = False

    gpio.setmode(gpio.BOARD)
    
    pin_led = 7
    pin_pir = 11
    pin_btn_no = 24
    pin_btn_nc = 26
    
    gpio.setup(pin_led   , gpio.OUT, initial=gpio.LOW)
    gpio.setup(pin_pir   , gpio.IN , gpio.PUD_DOWN)
    gpio.setup(pin_btn_no, gpio.IN , gpio.PUD_DOWN)
    gpio.setup(pin_btn_no, gpio.IN , gpio.PUD_DOWN)
    
    for p in [pin_led, pin_pir, pin_btn_no, pin_btn_nc]:
        log.debug('Setup pin %d for function %s', p, gpio.gpio_function(p))

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
            log.log(0, 'Executing loop')
            log.log(0, 'Updating state...')
            state.button_depressed = gpio.input(pin_btn_no)
            
            if state.button_depressed is not state.button_depressed_old:
                state.button_depressed_old = state.button_depressed
                if state.button_depressed:
                    log.debug('Toggling state...')
                      
                    if gpio.input(pin_led):
                        log.debug('Turning LED OFF')
                        play_sound('system/deactivate.wav')
                    else:
                        log.debug('Turning LED ON')
                        play_sound('system/activate.wav')
                      
                    gpio.output(pin_led, not gpio.input(pin_led))
                    log.debug('Toggling state... Done.')
            if gpio.input(pin_pir):
                log.info('Motion detected!')
                state.motion_detected = True
            else:
                state.motion_detected = False
            log.log(0, 'Updating state... Done.')
            if state.button_depressed:
                pass
                # log.debug('Toggling state...')
                #   
                # if gpio.input(pin_led):
                #     log.debug('Turning LED OFF')
                #     play_sound('system/deactivate.wav')
                # else:
                #     log.debug('Turning LED ON')
                #     play_sound('system/activate.wav')
                #   
                # gpio.output(pin_led, not gpio.input(pin_led))
                # log.debug('Toggling state... Done.')
            if state.testing:
                log.info('Running diagnostic...')
                for i in range(4):
                    log.debug('Toggling LED on pin {}'.format(pin_led))
                    gpio.output(pin_led, not gpio.input(pin_led))
                    time.sleep(1)
                play_sound('system/diagnostic.wav')
                log.info('Running diagnostic... Done')
                state.testing = False
            elif gpio.input(pin_led) and state.motion_detected:
                choices = ['recordings/'+key for key in snorts if bool(snorts[key][0])]
                soundfile = random.choice(choices)
                log.info('Waiting ten seconds to play sound.')
                time.sleep(5)
                
                play_sound(soundfile)
                
                log.info('Waiting five minutes to continue execution')
                time.sleep(10)
    except KeyboardInterrupt:
        log.info('Process ended with C-c.')

    log.info('Cleaning up GPIO...')
    gpio.cleanup()
    log.info('Cleaning up GPIO... Done.')
    log.info('Program exit.')
