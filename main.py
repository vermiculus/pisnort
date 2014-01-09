import gpioutil
import RPi.GPIO as gpio

gpio.setwarnings(False)

pins = {
    'led': gpioutil.Pin(7, gpio.OUT, gpio.HIGH)
    }

gpioutil.setup_all(pins)


import subprocess
def play_sound(relative_path):
    subprocess.call(["aplay",  relative_path])


if __name__ == '__main__':
    print 'Welcome to PiSnort!'

    print 'Importing libraries...',
    import time
    print 'Done.'

    while True:
        for i in range(5):
            print 'Toggling LED on pin {}'.format(pins['led'].number)
            gpioutil.toggle(pins['led'])
            time.sleep(1)
        print 'Playing siren'
        play_sound("police_s.wav")
