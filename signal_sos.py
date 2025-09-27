from gpiozero import Buzzer, LED
import time

led1 = LED(11)
led2 = LED(12)
led3 = LED(13)
buzzer = Buzzer(18)

def first_led(led1):
    for i in range(3):
        led1.on()
        buzzer.on()
        time.sleep(0.4)
        led1.off()
        buzzer.off()
        time.sleep(0.3)

def second_led(led2):
    for i in range(3):
        led2.on()
        buzzer.on()
        time.sleep(1)
        led2.off()
        buzzer.off()
        time.sleep(0.3)

def third_led(led3):
    for i in range(3):
        led3.on()
        buzzer.on()
        time.sleep(0.4)
        led3.off()
        buzzer.off()
        time.sleep(0.3)

while True:
    first_led(led1)
    second_led(led2)
    third_led(led3)