#!/usr/bin/env python
# coding: UTF-8
# vim: set ts=2 sw=2 sts=2 expandtab:

from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource

import cgi
import json
from base64 import b64decode
import hashlib
import Image
import traceback

from raumzeitlabor.pingie import display

import StringIO

def extract_image(request):
  headers = request.getAllHeaders()
  post = cgi.FieldStorage(
    fp = request.content,
    headers = headers,
    environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': headers['content-type']}
  )

  return post["file"].value

class Hello(Resource):

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
        text = request.prepath[0]
        print text
        pixmap = display.render_text(text)
        display.transfer(pixmap)
        return 'got: %r' % text

    def render_POST(self, request):
        content = request.content.read()
        obj = json.loads(content)
        pixmap = Image.fromstring('1', (display.WIDTH, display.HEIGHT), b64decode(obj['pixmap']) )
        display.transfer(pixmap)
        return 'okay.'

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

      sha = hashlib.sha256(buf).hexdigest()
      # maybe check if we are overwriting a exisiting file?
      f = open("%s" % sha, 'w')
      f.write(buf)
      f.close()

      return sha
    except:
      return traceback.format_exc()

class ShowImage(Resource):
  def render_POST(self, request):
    sha = request.args["id"][0]
    img = Image.open(sha)
    display.transfer(img)
    return 'ok'

root = Resource()
create = Resource()
show = Resource()

root.putChild("create", create)
root.putChild("show", show)

create.putChild("image", CreateImage())
show.putChild("image", ShowImage())

site = server.Site(root)
reactor.listenTCP(80, site)
print 'entering run loop'
reactor.run()
