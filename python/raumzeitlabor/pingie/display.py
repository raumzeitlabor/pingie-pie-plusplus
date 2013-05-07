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
fixed_5x8 = ImageFont.truetype("Fixed5x8.ttf", 8)

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

def render_text(text, font):
    from textwrap import wrap
    from math import floor

    if font == "5x8":
        font = fixed_5x8
    elif font == "9x15":
        font = fixed_9x15

    # doesn't matter which character
    (font_width, font_height) = font.getsize('m')

    # if the text is to large for a display-sized image,
    # wordwrap the text and use additional lines; enlarge it accordingly
    line_chars = floor(WIDTH / font_width)
    text = list(wrap(text, line_chars))
    lines = len(text)

    image = Image.new('1', (WIDTH, font_height * lines))
    draw = ImageDraw.Draw(image)

    line = 0
    for line in range(0, lines):
        text = text[line]
        draw.text((0, font_height * line), text, font=font, fill=1)
        line = line + 1

    return image
