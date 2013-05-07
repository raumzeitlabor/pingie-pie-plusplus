# coding: UTF-8
# vim: set ts=4 sw=4 sts=4 expandtab:
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Needs to be run as superuser, because of RPi.GPIO")

import Image
import ImageDraw
import ImageFont

import pprint
from time import clock, sleep

BS = 7
B0 = 8
B1 = 10
B2 = 11
B3 = 12
B4 = 13
B5 = 15
B6 = 16
B7 = 18
PS = 3

WIDTH = 152
HEIGHT = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(BS, GPIO.OUT)
GPIO.setup(B0, GPIO.OUT)
GPIO.setup(B1, GPIO.OUT)
GPIO.setup(B2, GPIO.OUT)
GPIO.setup(B3, GPIO.OUT)
GPIO.setup(B4, GPIO.OUT)
GPIO.setup(B5, GPIO.OUT)
GPIO.setup(B6, GPIO.OUT)
GPIO.setup(B7, GPIO.OUT)
GPIO.setup(PS, GPIO.OUT)

fixed_9x15 = ImageFont.truetype("Fixed9x15.ttf", 15)

def transfer(image):
    # resize image to display size and rotate, because it's mounted upside down
    image = image.crop((0, 0, WIDTH, HEIGHT)).rotate(180)

    from itertools import cycle
    pins = cycle([B0, B1, B2, B3, B4, B5, B6, B7])

    pin = pins.next()
    for pixel in image.getdata():
        GPIO.output(pin, pixel)

        pin = pins.next()
        if pin == B0:
            GPIO.output(BS, GPIO.HIGH)
            GPIO.output(BS, GPIO.LOW)

    # test relais
    GPIO.output(B0, 1)

    GPIO.output(BS, GPIO.HIGH)
    GPIO.output(BS, GPIO.LOW)

    GPIO.output(PS, GPIO.HIGH)
    GPIO.output(PS, GPIO.LOW)

def render_text(text):
    pixmap = Image.new('1', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(pixmap)

    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=0)

    draw.text((0, 0), text, font=fixed_9x15, fill=1)
    return pixmap
