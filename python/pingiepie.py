#!/usr/bin/env python
# coding: UTF-8
# vim: set ts=2 sw=2 sts=2 expandtab:

from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource

import cgi
import hashlib
import Image
import StringIO
from itertools import cycle

from pingiepie import display
from pingiepie.util import TextResource
from pingiepie import util

class CreateText(TextResource):
  def render_GET(self, request):
    return 'create text here'

  def post(self, request):
    text = request.args["text"][0].decode(encoding='utf-8')
    font = request.args["font"][0] if "font" in request.args else "5x8"

    img = display.render_text(text, font)
    sha = util.save_image(img)

    return sha

class CreateImage(TextResource):
  def render_GET(self, request):
    return 'upload images here'

  def post(self, request):
    str_image = util.extract_field(request, 'file')
    # lets see if its a usable image
    img = Image.open(StringIO.StringIO(buf))
    sha = util.save_image(img)
    return sha

class ShowImage(TextResource):
  def post(self, request):
    sha = request.args["id"][0]
    img = Image.open("/run/%s.png" % sha)
    display.update(cycle([(30, img)]))
    return 'ok'

class ShowScroll(TextResource):
  def post(self, request):
    sha = request.args["id"][0]
    img = Image.open("/run/%s.png" % sha)
    _, height = img.size
    if height <= display.HEIGHT:
      display.update(cycle([(30, img)]))
      return "ok"

    img_list = []
    for i in range(0, height - display.HEIGHT + 2, 2):
      img_cropped = img.crop((0, i, display.WIDTH, i + display.HEIGHT))
      img_list.append((3, img_cropped))

    img_list[-1] = (30, img_list[-1][1])
    img_list[0] = (30, img_list[0][1])

    display.update(cycle(img_list))

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
