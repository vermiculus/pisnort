
import RPi.GPIO
import logging
log = logging.getLogger('')

class Pin:
    VOLT = 1
    GROUND = 0
    def __init__(self, number, mode, state=None, pud=RPi.GPIO.PUD_OFF):
        self.number = number
        self.mode = mode
        self.state = state
        self.pud = pud
    def __int__(self):
        return self.number

def set_pin(pin, state):
    assert pin.mode is RPi.GPIO.OUT
    pin.state = state
    RPi.GPIO.output(pin.number, pin.state)

def read_pin(pin):
    assert pin.mode is RPi.GPIO.IN

    return RPi.GPIO.input(pin.number)

def toggle(pin):
    assert pin.mode is RPi.GPIO.OUT
    if pin.state is RPi.GPIO.HIGH:
        set_pin(pin, RPi.GPIO.LOW)
    elif pin.state is RPi.GPIO.LOW:
        set_pin(pin, RPi.GPIO.HIGH)
    else:
        log.critical('What happened?  Pin %d is neither HIGH nor LOW.', pin.number)

def setup_all(pins):
    log.info('Running initial setup...')
    for pin in sorted(pins.values(), key=lambda p: p.number):
        if pin.number in [Pin.VOLT, Pin.GROUND]:
            continue

        assert pin.mode in [RPi.GPIO.IN, RPi.GPIO.OUT]
        assert pin.state in [RPi.GPIO.HIGH, RPi.GPIO.LOW, None]
        if pin.mode is RPi.GPIO.IN:
            assert pin.state is None

        log.info('Pin {} is {} ({})'.format(pin.number,
                                       'IN' if pin.mode is RPi.GPIO.IN else 'OUT',
                                       pin.pud))
        RPi.GPIO.setup(pin.number, pin.mode, pull_up_down=pin.pud)
        if pin.mode is RPi.GPIO.OUT:
            log.debug('Setting to {}'.format('HIGH' if pin.state is RPi.GPIO.HIGH else 'LOW'))
            RPi.GPIO.output(pin.number, pin.state)
    log.info('Running initial setup... Done.')
