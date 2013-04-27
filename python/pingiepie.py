#!/usr/bin/env python
# coding: UTF-8
# vim: set ts=4 sw=4 sts=4 expandtab:

from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource

import json
from base64 import b64decode
import Image

from raumzeitlabor.pingie import display

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

site = server.Site(Hello())
reactor.listenTCP(8000, site)
print 'entering run loop'
reactor.run()
