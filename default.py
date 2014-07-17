#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, sys, xbmcgui, xbmcplugin#, datetime
from neverwise import Util
from operator import itemgetter


class MTV:

  __handle = int(sys.argv[1])
  __params = Util.urlParametersToDict(sys.argv[2])
  __idPlugin = 'plugin.mtvondemand'
  __namePlugin = 'MTV on demand'
  __itemsNumber = 0

  def __init__(self):

    # Programmi.
    if len(self.__params) == 0:
      programs = self.__getMTVResponse('/serie-tv')
      if programs != None:
        programs = re.compile('<h3 class="showpass"><a href="(.+?)"> <img class="lazy" height="105" width="140" src=".+?" data-original="(.+?)\?width=0&amp;amp;height=0&amp;amp;matte=true&amp;amp;matteColor=black&amp;amp;quality=0\.91" alt=".+?"/><p><strong>(.+?)</strong>(.+?)</p>').findall(programs)
        for link, img, name, descr in programs:
          name = Util.normalizeText(name)
          Util.addItem(self.__handle, name, img, '', 'video', { 'title' : name, 'plot' : Util.normalizeText(descr) }, None, { 'action' : 's', 'path' : link }, True)
          self.__itemsNumber += 1

    # Stagioni.
    elif self.__params['action'] == 's':
      response = self.__getMTVResponse(self.__params['path'])
      if response != None:
        if response.find('<h2>Troppo tardi! <b>&#9787;</b></h2>') == -1:
          seasons = re.compile('<ul class="nav">(.+?)</ul>').findall(response)
          seasons = re.compile('href="(.+?)">(.+?)</a></li>').findall(seasons[0])
          if len(seasons) > 1:
            title = Util.normalizeText(re.compile('<h1 itemprop="name">(.+?)</h1>').findall(response)[0])
            for link, season in seasons:
              season = Util.normalizeText(season)
              Util.addItem(self.__handle, season, '', '', 'video', { 'title' : season, 'plot' : '{0} di {1}'.format(season, title) }, None, { 'action' : 'p', 'path' : link }, True)
              self.__itemsNumber += 1
          else:
            self.__getEpisodes(seasons[0][0])
        else:
          xbmcgui.Dialog().ok(self.__namePlugin, Util.getTranslation(self.__idPlugin, 30001)) # Troppo tardi! I diritti di questo video sono scaduti.

    # Puntate.
    elif self.__params['action'] == 'p':
      self.__getEpisodes(self.__params['path'])

    # Risoluzioni.
    elif self.__params['action'] == 'r':
      videoId = Util(self.__params['path']).getHtmlDialog(self.__namePlugin)
      if videoId != None:
        videoId = re.compile('<div class="MTVNPlayer".+? data-contenturi="(.+?)">').findall(videoId)
        if len(videoId) > 0:
          streams = Util('http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?uri=mgid:uma:video:mtv.it{0}'.format(videoId[0][videoId[0].rfind(':'):])).getHtmlDialog(self.__namePlugin)
          if streams != None:
            streams = re.compile('<rendition cdn="akamai" duration="(.+?)".+?height="(.+?)".+?><src>(.+?)</src></rendition>').findall(streams)
            streams.sort(key = itemgetter(1), reverse = True)
            idLabel = 30011 - len(streams)
            for duration, height, url in streams:
              title = Util.getTranslation(self.__idPlugin, idLabel)
              idLabel += 1
              Util.addItem(self.__handle, title, '', '', 'video', { 'title' : title }, int(duration), '{0} swfUrl=http://media.mtvnservices.com/player/prime/mediaplayerprime.2.3.7.swf?uri={1}.swf swfVfy=true'.format(url, self.__params['path']), False)
              self.__itemsNumber += 1
        else:
          xbmcgui.Dialog().ok(self.__namePlugin, Util.getTranslation(self.__idPlugin, 30002)) # Video non disponibile.

    if self.__itemsNumber > 0:
      xbmcplugin.endOfDirectory(self.__handle)


  def __getMTVResponse(self, link):
    return Util('http://ondemand.mtv.it{0}'.format(link)).getHtmlDialog(self.__namePlugin)


  def __getEpisodes(self, path):
    index = path.rfind('/')
    videos = self.__getMTVResponse('{0}.rss'.format(path[:index]))
    if videos != None:
      videos = re.compile('<item><title><!\[CDATA\[(.+?)]]></title><link>(.+?)</link><description><!\[CDATA\[(.+?)]]></description><guid>.+?</guid><pubDate>(.+?)</pubDate><enclosure length="0" type="image/jpeg" url="(.+?)"/></item>').findall(videos)
      season = '{0}/'.format(path[index:])
      for name, link, descr, pubDate, img in videos:
        if link.find(season) > -1:
          name = Util.normalizeText(name)
          iResEnd = img.rfind('.')
          iResStart = iResEnd - 3
          if img[iResStart:iResEnd] == '140':
            img = '{0}640{1}'.format(img[:iResStart], img[iResEnd:])
          Util.addItem(self.__handle, name, img, '', 'video', { 'title' : name, 'plot' : Util.normalizeText(descr) }, None, { 'action' : 'r', 'path' : link }, True)
          self.__itemsNumber += 1


# Entry point.
#startTime = datetime.datetime.now()
mtv = MTV()
del mtv
#print '{0} azione {1}'.format(self.__namePlugin, str(datetime.datetime.now() - startTime))
