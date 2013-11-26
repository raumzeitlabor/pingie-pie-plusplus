# coding: UTF-8
# vim: set ts=2 sw=2 sts=2 expandtab:

from twisted.web.resource import Resource
import traceback
import Image
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
