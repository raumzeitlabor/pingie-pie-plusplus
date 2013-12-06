# coding: UTF-8
# vim: set ts=2 sw=2 sts=2 expandtab:

from twisted.web.resource import Resource
import traceback
import Image
import ImageDraw
import ImageFont
import StringIO
import hashlib

# twisted's Resource normally formats exceptions in html, so we wrap it here
# to generate plain text errors
class TextResource(Resource):
  def render_POST(self, request):
    try:
      return self.post(request)
    except:
      e = traceback.format_exc()
      print e
      request.setResponseCode(400)
      return e

# PriorityQueue actually sorts it entries,
# workaround it by having a counter to normalize it to a FIFO
from Queue import PriorityQueue
class PriorityFifo(PriorityQueue):
  def __init__(self):
    PriorityQueue.__init__(self)
    self.counter = 0

  def put(self, item, priority):
    PriorityQueue.put(self, (priority, self.counter, item))
    self.counter += 1

  def get(self, *args, **kwargs):
    _, _, item = PriorityQueue.get(self, *args, **kwargs)
    return item

# twisted can't decode formdata on its own,
# the internets suggests this is "best practice":
def extract_field(request, field):
  headers = request.getAllHeaders()
  post = cgi.FieldStorage(
    fp = request.content,
    headers = headers,
    environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': headers['content-type']}
  )
  return post[field].value

# given an Image, save it on the ramdisk and return its sha256
def save_image(img):
  buf = StringIO.StringIO()
  img.save(buf, format="png", bits=1)
  sha = hashlib.sha256(buf.getvalue()).hexdigest()
  # maybe check if we are overwriting a exisiting file?
  img.save("/run/%s.png" % sha, bits=1)

  return sha

fixed_9x15 = ImageFont.truetype("Fixed9x15.ttf", 15)
fixed_5x8 = ImageFont.truetype("Fixed5x8.ttf", 8)

def render_text(text, font):
  from textwrap import wrap
  from math import floor

  if font == "5x8":
    font = fixed_5x8
  elif font == "9x15":
    font = fixed_9x15
  else:
    font = fixed_5x8

  # doesn't matter which character
  (font_width, font_height) = font.getsize('m')

  # if the text is to large for a display-sized image,
  # wordwrap the text and use additional lines; enlarge it accordingly
  line_chars = floor(WIDTH / font_width)
  text = list(wrap(text, line_chars))
  lines = len(text)

  image = Image.new('1', (WIDTH, font_height * lines))
  draw = ImageDraw.Draw(image)

  for line in range(0, lines):
    t = text[line]
    draw.text((0, font_height * line), t, font=font, fill=1)
    line = line + 1

  return image
