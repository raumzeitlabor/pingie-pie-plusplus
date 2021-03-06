# coding: UTF-8
# vim: set ts=2 sw=2 sts=2 expandtab:
try:
  from RPi import GPIO
except RuntimeError:
  print("Needs to be run as superuser, because of RPi.GPIO")

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

import Image

import pprint
from twisted.internet.task import LoopingCall
from twisted.internet import reactor # needed for timers

from pingiepie.util import PriorityFifo

backlight = 1
disable_timer = None
queue = PriorityFifo()
def update(image, priority=100):
  global queue, backlight
  queue.put(image, priority)

  def disable_backlight():
    global backlight
    backlight = 0
    print("disabling backlight")

  backlight = 1

  global disable_timer
  if disable_timer is None or not disable_timer.active():
    disable_timer = reactor.callLater(10 * 60, disable_backlight) # 10 minutes
  else:
    # re-new the timeout
    disable_timer.reset(10 * 60)

frame = None
framelist = None
next_frame = 0
def _refresh():
  global frame, framelist, next_frame, backlight
  if not queue.empty():
    print("new frame")
    framelist = queue.get()
    next_frame, frame = framelist.next()
    queue.task_done()
    transfer(frame)

  if frame:
    next_frame = next_frame - 1
    if next_frame <= 0:
      next_frame, frame = framelist.next()
      transfer(frame)

def transfer(image):
  global backlight

  from itertools import cycle
  pins = cycle([B0, B1, B2, B3, B4, B5, B6, B7])
  pin = pins.next()

  # resize image to display size and rotate, because it's mounted upside down
  image = image.crop((0, 0, WIDTH, HEIGHT)).rotate(180)

  for pixel in image.getdata():
    GPIO.output(pin, pixel)

    pin = pins.next()
    if pin == B0:
      GPIO.output(BS, GPIO.HIGH)
      GPIO.output(BS, GPIO.LOW)

  GPIO.output(B0, backlight)
  GPIO.output(BS, GPIO.HIGH)
  GPIO.output(BS, GPIO.LOW)

  GPIO.output(PS, GPIO.HIGH)
  GPIO.output(PS, GPIO.LOW)

refresh = LoopingCall(_refresh)
refresh.start(0.05)
