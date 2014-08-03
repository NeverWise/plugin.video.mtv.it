#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re, xbmcgui#, datetime
from neverwise import Util
from operator import itemgetter


class MTV(object):

  _handle = int(sys.argv[1])
  _params = Util.urlParametersToDict(sys.argv[2])

  def __init__(self):

    # Programmi.
    if len(self._params) == 0:
      programs = self._getMTVResponse('/serie-tv')
      if programs != None:
        programs = re.compile('<h3 class="showpass"><a href="(.+?)"> <img class="lazy" height="105" width="140" src=".+?" data-original="(.+?)\?width=0&amp;amp;height=0&amp;amp;matte=true&amp;amp;matteColor=black&amp;amp;quality=0\.91" alt=".+?"/><p><strong>(.+?)</strong>(.+?)</p>').findall(programs)
        items = []
        for link, img, name, descr in programs:
          name = Util.normalizeText(name)
          li = Util.createListItem(name, thumbnailImage = img, streamtype = 'video', infolabels = { 'title' : name, 'plot' : Util.normalizeText(descr) })
          items.append([{ 'action' : 's', 'path' : link }, li, True, True])
        Util.addItems(self._handle, items)

    # Stagioni.
    elif self._params['action'] == 's':
      response = self._getMTVResponse(self._params['path'])
      if response != None:
        if response.find('<h2>Troppo tardi! <b>&#9787;</b></h2>') == -1:
          seasons = re.compile('<ul class="nav">(.+?)</ul>').findall(response)
          seasons = re.compile('href="(.+?)">(.+?)</a></li>').findall(seasons[0])
          if len(seasons) > 1:
            title = Util.normalizeText(re.compile('<h1 itemprop="name">(.+?)</h1>').findall(response)[0])
            items = []
            for link, season in seasons:
              season = Util.normalizeText(season)
              li = Util.createListItem(season, streamtype = 'video', infolabels = { 'title' : season, 'plot' : '{0} di {1}'.format(season, title) })
              items.append([{ 'action' : 'p', 'path' : link }, li, True, True])
            Util.addItems(self._handle, items)
          else:
            self._getEpisodes(seasons[0][0])
        else:
          xbmcgui.Dialog().ok(Util._addonName, Util.getTranslation(30000)) # Troppo tardi! I diritti di questo video sono scaduti.

    # Puntate.
    elif self._params['action'] == 'p':
      self._getEpisodes(self._params['path'])

    # Risoluzioni.
    elif self._params['action'] == 'r':
      videoId = Util(self._params['path']).getHtml(True)
      if videoId != None:
        videoId = re.compile('<div class="MTVNPlayer".+? data-contenturi="(.+?)">').findall(videoId)
        if len(videoId) > 0:
          streams = Util('http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?uri=mgid:uma:video:mtv.it{0}'.format(videoId[0][videoId[0].rfind(':'):])).getHtml(True)
          if streams != None:
            streams = re.compile('<rendition cdn="akamai" duration="(.+?)".+?height="(.+?)".+?><src>(.+?)</src></rendition>').findall(streams)
            streams.sort(key = itemgetter(1), reverse = True)
            idLabel = 30008 - len(streams)
            items = []
            for duration, height, url in streams:
              title = Util.getTranslation(idLabel)
              idLabel += 1
              li = Util.createListItem(title, streamtype = 'video', infolabels = { 'title' : title }, duration = int(duration))
              items.append(['{0} swfUrl=http://media.mtvnservices.com/player/prime/mediaplayerprime.2.3.7.swf?uri={1}.swf swfVfy=true'.format(url, self._params['path']), li, False, False])
            Util.addItems(self._handle, items)
        else:
          xbmcgui.Dialog().ok(Util._addonName, Util.showVideoNotAvailableDialog()) # Video non disponibile.


  def _getMTVResponse(self, link):
    return Util('http://ondemand.mtv.it{0}'.format(link)).getHtml(True)


  def _getEpisodes(self, path):
    index = path.rfind('/')
    videos = self._getMTVResponse('{0}.rss'.format(path[:index]))
    if videos != None:
      videos = re.compile('<item><title><!\[CDATA\[(.+?)]]></title><link>(.+?)</link><description><!\[CDATA\[(.+?)]]></description><guid>.+?</guid><pubDate>(.+?)</pubDate><enclosure length="0" type="image/jpeg" url="(.+?)"/></item>').findall(videos)
      season = '{0}/'.format(path[index:])
      items = []
      for name, link, descr, pubDate, img in videos:
        if link.find(season) > -1:
          name = Util.normalizeText(name)
          iResEnd = img.rfind('.')
          iResStart = iResEnd - 3
          if img[iResStart:iResEnd] == '140':
            img = '{0}640{1}'.format(img[:iResStart], img[iResEnd:])
          li = Util.createListItem(name, thumbnailImage = img, streamtype = 'video', infolabels = { 'title' : name, 'plot' : Util.normalizeText(descr) })
          items.append([{ 'action' : 'r', 'path' : link }, li, True, True])
      Util.addItems(self._handle, items)


# Entry point.
#startTime = datetime.datetime.now()
mtv = MTV()
del mtv
#print '{0} azione {1}'.format(Util._addonName, str(datetime.datetime.now() - startTime))
