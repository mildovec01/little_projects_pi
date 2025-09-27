from gpiozero import Buzzer, LED
import time

# Set pins to BCM numbering
led1 = LED(17) # --> Real PIN 11
led2 = LED(18) # --> Real PIN 12
led3 = LED(27) # --> Real PIN 13
buzzer = Buzzer(24) # --> Real PIN 18

# First LED that shows ==> S
def first_led(led1):
    # Set cycle for 3 repeats
    for i in range(3):
        led1.on()
        buzzer.on()
        time.sleep(0.4)
        led1.off()
        buzzer.off()
        time.sleep(0.3)

# Second LED that shows ==> O
def second_led(led2):
    for i in range(3):
        led2.on()
        buzzer.on()
        time.sleep(1)
        led2.off()
        buzzer.off()
        time.sleep(0.3)

# Third LED that shows ==> S, same as the first LED
def third_led(led3):
    for i in range(3):
        led3.on()
        buzzer.on()
        time.sleep(0.4)
        led3.off()
        buzzer.off()
        time.sleep(0.3)

# Set the loop cycle
while True:
    first_led(led1)
    second_led(led2)
    third_led(led3)
