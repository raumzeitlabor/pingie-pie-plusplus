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

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def transfer(pixmap):
    pixmap_rotated = pixmap.rotate(180)

    for x in chunks(list(pixmap_rotated.getdata()),8):
        GPIO.output(B0, x[0])
        GPIO.output(B1, x[1])
        GPIO.output(B2, x[2])
        GPIO.output(B3, x[3])
        GPIO.output(B4, x[4])
        GPIO.output(B5, x[5])
        GPIO.output(B6, x[6])
        GPIO.output(B7, x[7])

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

    font = ImageFont.truetype("/root/miso-bold.ttf", 24)
    draw.text((0, 0), text, font=font, fill=1)
    return pixmap
