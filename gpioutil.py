import RPi.GPIO

RPi.GPIO.setmode(RPi.GPIO.BOARD)

class Pin:
    VOLT = 1
    GROUND = 0
    def __init__(self, number, mode, state=None):
        self.number = number
        self.mode = mode
        self.state = state
    def __int__(self):
        return self.number

def setup_all(pins):
    for pin in pins.values():
        if pin in [self.VOLT, self.GROUND]:
            continue

        assert pin.mode in [RPi.GPIO.IN, RPi.GPIO.OUT]
        assert pin.state in [RPi.GPIO.HIGH, RPi.GPIO.LOW, None]
        if pin.mode is RPi.GPIO.IN:
            assert pin.state is None

        print 'Running initial setup...'
        print '\tPin {} is {}'.format(pin.number, 'IN' if pin.mode is RPi.GPIO.IN else 'OUT')
        RPi.GPIO.setup(pin.number, pin.mode)
        if pin.mode is RPi.GPIO.OUT:
            print '\t\tSetting to {}'.format('HIGH' if pin.state is RPi.GPIO.HIGH else 'LOW')
            RPi.GPIO.output(pin.number, pin.state)

def set_pin(pin, state):
    assert pin.mode is RPi.GPIO.OUT
    pin.state = state
    RPi.GPIO.output(pin.number, pin.state)

def toggle(pin):
    assert pin.mode is RPi.GPIO.OUT
    if pin.state is RPi.GPIO.HIGH:
        set_pin(pin, RPi.GPIO.LOW)
    elif pin.state is RPi.GPIO.LOW:
        set_pin(pin, RPi.GPIO.HIGH)
    else:
        raise Exception('What happened?  Pin {} is neither HIGH nor LOW.'.format(pin))
