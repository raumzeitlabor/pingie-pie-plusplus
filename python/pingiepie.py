#!/usr/bin/env python
# coding: UTF-8
# vim: set ts=2 sw=2 sts=2 expandtab:

from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource

import cgi
import hashlib
import Image
import traceback
import StringIO

from raumzeitlabor.pingie import display

def extract_image(request):
  headers = request.getAllHeaders()
  post = cgi.FieldStorage(
    fp = request.content,
    headers = headers,
    environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': headers['content-type']}
  )

  return post["file"].value

def save_image(img):
  buf = StringIO.StringIO()
  img.save(buf, format="png")
  sha = hashlib.sha256(buf.getvalue()).hexdigest()
  # maybe check if we are overwriting a exisiting file?
  img.save("/run/%s.png" % sha)

  return sha


class CreateText(Resource):
  def render_GET(self, request):
    return 'create text here'

  def render_POST(self, request):
    try:
      text = request.args["text"][0].decode(encoding='utf-8')
      font = (request.args["font"][0]
          if "font" in request.args else "9x15")

      img = display.render_text(text, font)
      sha = save_image(img)

      return sha

    except:
      return traceback.format_exc()

class CreateImage(Resource):
  def render_GET(self, request):
    return 'upload images here'

  def render_POST(self, request):
    try:
      buf = extract_image(request)
      # lets see if its a usable image
      img = Image.open(StringIO.StringIO(buf))
      #if img.mode != "1":
      #  return "Image has more than 2 colours"
      sha = save_image(img)

      return sha

    except:
      return traceback.format_exc()

class ShowImage(Resource):
  def render_POST(self, request):
    sha = request.args["id"][0]
    img = Image.open("/run/%s.png" % sha)
    display.update(img)
    return 'ok'

class ShowScroll(Resource):
  def render_POST(self, request):
    sha = request.args["id"][0]
    img = Image.open("/run/%s.png" % sha)
    (_, height) = img.size
    img_list = []
    for i in range(0, height - display.HEIGHT + 2, 2):
      print i
      img_cropped = img.crop((0, i, display.WIDTH, i + display.HEIGHT))
      display.update(img_cropped)


    return "ok"


root = Resource()
create = Resource()
show = Resource()

root.putChild("create", create)
root.putChild("show", show)

create.putChild("image", CreateImage())
create.putChild("text", CreateText())
show.putChild("image", ShowImage())
show.putChild("scroll", ShowScroll())

site = server.Site(root)
reactor.listenTCP(80, site)
print 'entering run loop'
reactor.run()
