# LCD1602 (I2C) + green led and red led + buzzer + matrix keypad
# Pins (BCM):
# rowsPins = [18, 23, 24, 25]
# colsPins = [22, 27, 17, 5]
# LED green=16, LED red=20, buzzer=12



import time
from gpiozero import LED, Buzzer
import smbus2

# Safe import
try:
    from keypad import Keypad as KeypadClass
except ImportError:
    try:
        from Keypad import Keypad as KeypadClass
    except ImportError as e:
        raise SystemExit("Couldnt find 'keypad.py' with class Keypad "
                         "in the same folder as the script.") from e

# LCD1602 i2c driver
class I2cLcd1602:
    LCD_CLEARDISPLAY   = 0x01
    LCD_RETURNHOME     = 0x02
    LCD_ENTRYMODESET   = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_FUNCTIONSET    = 0x20
    LCD_SETDDRAMADDR   = 0x80

    LCD_ENTRYLEFT      = 0x02
    LCD_ENTRYSHIFTDEC  = 0x00
    LCD_DISPLAYON      = 0x04
    LCD_CURSOROFF      = 0x00
    LCD_BLINKOFF       = 0x00
    LCD_2LINE          = 0x08
    LCD_5x8DOTS        = 0x00

    ENABLE = 0b00000100
    RW     = 0b00000010
    RS     = 0b00000001
    BACKLIGHT = 0b00001000

    def __init__(self, i2c_bus=1, i2c_addr=0x27, cols=16, rows=2):
        self.bus = smbus2.SMBus(i2c_bus)
        self.addr = i2c_addr
        self.cols = cols
        self.rows = rows
        self.backlight = self.BACKLIGHT

        time.sleep(0.05)
        self._write4(0x03 << 4); time.sleep(0.005)
        self._write4(0x03 << 4); time.sleep(0.005)
        self._write4(0x03 << 4); time.sleep(0.001)
        self._write4(0x02 << 4)  # 4-bit

        self.command(self.LCD_FUNCTIONSET | self.LCD_2LINE | self.LCD_5x8DOTS)
        self.command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF)
        self.command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDEC)
        self.clear()

    def _strobe(self, data):
        self.bus.write_byte(self.addr, data | self.ENABLE | self.backlight)
        time.sleep(0.0005)
        self.bus.write_byte(self.addr, (data & ~self.ENABLE) | self.backlight)
        time.sleep(0.0001)

    def _write4(self, data):
        self.bus.write_byte(self.addr, data | self.backlight)
        self._strobe(data)

    def command(self, cmd):
        self._write4(cmd & 0xF0)
        self._write4((cmd << 4) & 0xF0)

    def write_char(self, ch):
        data = self.RS | (ch & 0xF0)
        self.bus.write_byte(self.addr, data | self.backlight); self._strobe(data)
        data = self.RS | ((ch << 4) & 0xF0)
        self.bus.write_byte(self.addr, data | self.backlight); self._strobe(data)

    def clear(self):
        self.command(self.LCD_CLEARDISPLAY); time.sleep(0.002)

    def set_cursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(self.LCD_SETDDRAMADDR | (col + row_offsets[row]))

    def print(self, text):
        for ch in str(text):
            self.write_char(ord(ch))

    def backlight_on(self, on=True):
        self.backlight = self.BACKLIGHT if on else 0
        self.bus.write_byte(self.addr, self.backlight)

# Finding the LCD
def find_lcd_addr(bus=1):
    dev = smbus2.SMBus(bus)
    candidates = list(range(0x20, 0x28)) + list(range(0x38, 0x40))
    for addr in candidates:
        try:
            dev.write_byte(addr, 0x00)
            return addr
        except OSError:
            continue
    return None

# PINs and map
ROWS = 4
COLS = 4
KEYS = [
    '1','2','3','A',
    '4','5','6','B',
    '7','8','9','C',
    '*','0','#','D'
]
rowsPins = [18, 23, 24, 25]
colsPins = [22, 27, 17, 5]   

# LED + buzzer
led_green = LED(16)
led_red   = LED(20)
buzzer    = Buzzer(12)   # active buzzer (passive buzzer needs PWM)

# ATM logic
PIN_KOD = "4218"
PIN_MAX_LEN = 6
MAX_POKUSU = 3
LOCKOUT_S = 10

def beep_short():
    buzzer.on(); time.sleep(0.1); buzzer.off()

def beep_long():
    buzzer.on(); time.sleep(0.6); buzzer.off()

def led_success():
    led_green.on(); time.sleep(1.0); led_green.off()

def led_fail():
    led_red.on(); time.sleep(1.0); led_red.off()

def lcd_msg(lcd, line1="", line2=""):
    lcd.clear()
    lcd.set_cursor(0, 0); lcd.print(line1[:16])
    lcd.set_cursor(0, 1); lcd.print(line2[:16])

def wait_key(kp, timeout=None):
    start = time.time()
    while True:
        k = kp.getKey()
        if k != kp.NULL:
            return k
        if timeout is not None and (time.time() - start) > timeout:
            return None
        time.sleep(0.01)

def read_pin(kp, lcd, max_len=PIN_MAX_LEN, timeout=30):
    buffer = []
    lcd_msg(lcd, "Enter PIN:", "")
    while True:
        stars = "*" * len(buffer)
        lcd.set_cursor(0, 1); lcd.print((stars + " " * (16 - len(stars)))[:16])
        k = wait_key(kp, timeout=timeout)
        if k is None:
            lcd_msg(lcd, "Timeout.", "Try again")
            return None
        if k in "0123456789":
            if len(buffer) < max_len:
                buffer.append(k)
        elif k == 'B' and buffer:
            buffer.pop()
        elif k == '*':
            buffer = []
        elif k == 'C': #Cancel
            lcd_msg(lcd, "Cancelled", "")
            return None
        elif k == 'A':  # Enter
            return "".join(buffer)

def main():
    # LCD autodetection
    addr = find_lcd_addr(1)
    if addr is None:
        raise SystemExit("LCD wasnt found at I2C. Control SDA=GPIO2, SCL=GPIO3, connection a 'i2cdetect -y 1'.")
    lcd = I2cLcd1602(i2c_bus=1, i2c_addr=addr, cols=16, rows=2)
    lcd.backlight_on(True)

    # Keypad instance
    print("KeypadClass =", KeypadClass)  # debug info
    kp = KeypadClass(KEYS, rowsPins, colsPins, ROWS, COLS)
    if kp is None:
        raise SystemExit("Keypad constructor returned None. Make sure, that in 'keypad.py' is class Keypad.")
    kp.setDebounceTime(50)

    lcd_msg(lcd, "ATM demo", "Ready")
    time.sleep(0.8)

    pokusy = 0
    balance = 1000

    while True:
        pin = read_pin(kp, lcd)
        if pin is None:
            continue

        if pin == PIN_KOD:
            beep_short(); led_success()
            lcd_msg(lcd, "PIN OK", "Welcome!")
            time.sleep(0.8)
            pokusy = 0

            # Easy menu
            while True:
                lcd_msg(lcd, "1:Balance", "2:-100 3:+100")
                key = wait_key(kp, timeout=30)
                if key is None:
                    lcd_msg(lcd, "Timeout", "Log out"); time.sleep(0.8); break
                if key == '1':
                    lcd_msg(lcd, "Balance:", f"{balance} Kc"); time.sleep(1.3)
                elif key == '2':
                    if balance >= 100:
                        balance -= 100
                        lcd_msg(lcd, "Withdrawed", "100 Kc"); beep_short(); time.sleep(1.0)
                    else:
                        lcd_msg(lcd, "Not enough", "balance"); beep_long(); led_fail(); time.sleep(1.2)
                elif key == '3':
                    balance += 100
                    lcd_msg(lcd, "Deposited", "100 Kc"); beep_short(); time.sleep(1.0)
                elif key == 'D':
                    lcd_msg(lcd, "Logged out", "Bye"); time.sleep(0.8); break
                elif key == 'C':
                    lcd_msg(lcd, "Back", ""); time.sleep(0.5)
        else:
            pokusy += 1
            zbyva = MAX_POKUSU - pokusy
            lcd_msg(lcd, "Wrong PIN", f"Remaining tries:{max(0,zbyva)}")
            beep_long(); led_fail()
            time.sleep(0.9)

            if pokusy >= MAX_POKUSU:
                lcd_msg(lcd, "Blocked", f"Wait {LOCKOUT_S}s")
                beep_long()
                for _ in range(LOCKOUT_S*2):
                    led_red.toggle(); time.sleep(0.5)
                led_red.off()
                beep_long()
                pokusy = 0
                lcd_msg(lcd, "Try again", "")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        led_green.off(); led_red.off(); buzzer.off()
        print("\nBye.")
