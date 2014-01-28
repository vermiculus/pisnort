#!/usr/bin/sudo python
import RPi.GPIO as io
import time
import random
import subprocess
import logging

logging.basicConfig(
    filename='log',
    format='%(asctime)s (%(name)s) [%(funcName)s] %(levelname)s: %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s'))
log = logging.getLogger('')
log.addHandler(console)
log.setLevel(logging.DEBUG)

io.setmode(io.BOARD)

pin_led = 7
pin_pir = 12
pin_btn = 24
btn_old = io.LOW
btn_in  = io.LOW
motion_detected = False
current_recording = None
sounds = set()

io.setup(pin_pir, io.IN)
io.setup(pin_led, io.OUT, initial=io.LOW)
io.setup(pin_btn, io.IN, io.PUD_DOWN)

snorts = {'record2snort2.wav':     'some criterion',
          'record3snort1.wav':     'some criterion',
          'record3snort2.wav':     'some criterion',
          'record4snort1.wav':     'some criterion',
          'record4snort2.wav':     'some criterion',
          'recorded snort1-3.wav': 'some criterion',
          'recorded snort1.wav':   'some criterion',
          'recorded snort2.wav':   'some criterion'}

try:
    log.info('Starting monitoring system')
    while True:
        time.sleep(.1)
        
        for sound in list(sounds):
            if sound.poll() is not None:
                if sound.returncode is not 0:
                    log.debug('Process ended abnormally')
                    sounds.remove(sound)

        btn_old = btn_in
        led_in = io.input(pin_led)
        btn_in = io.input(pin_btn)
        pir_in = io.input(pin_pir)
        if btn_in is io.LOW and btn_old is io.HIGH:
            log.info('Turning ' + ('off' if led_in else 'on'))
            io.output(pin_led, not led_in)
            if led_in:
                for sound in sounds:
                    sound.kill()
        if led_in:
            if motion_detected is False and pir_in and led_in:
                log.info('Motion detected!')
                motion_detected = time.time()
            if motion_detected:
                if current_recording is None:
                    if time.time() - motion_detected > 20:
                        current_recording = random.choice(
                            [key for key in snorts if snorts[key]])
                        log.info('Playing %s', current_recording)
                        new =subprocess.Popen(
                            ['mplayer',
                             '-msglevel',
                             'all=-1',
                             '/home/pi/snort/sounds/recordings/{!s}'.format(current_recording)])
                        sounds.add(new)
                else:
                    if time.time() - motion_detected > 60:
                        current_recording = None
                        motion_detected = False
        else:
            motion_detected = False
except KeyboardInterrupt:
    log.debug('Caught C-c')
finally:
    log.info('Exiting and cleaning up')
    for sound in list(sounds):
        if sound.poll() is None:
            sound.terminate()
            log.debug('Process ended abnormally')
        else:
            sounds.remove(sound)
    io.cleanup()
