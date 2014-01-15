#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 1.0.0 (20/10/2013)
# MTV on demand
# I programmi TV e le serie TV in streaming su MTV.
# By NeverWise
# <email>
# <web>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################
import re, sys, xbmcgui, xbmcplugin, tools#, datetime
from operator import itemgetter


def getEpisodes(path):
  index = path.rfind('/')
  response = tools.getResponseUrl('http://ondemand.mtv.it' + path[:index] + '.rss')
  videos = re.compile('<item><title><!\[CDATA\[(.+?)]]></title><link>(.+?)</link><description><!\[CDATA\[(.+?)]]></description><guid>.+?</guid><pubDate>(.+?)</pubDate><enclosure length="0" type="image/jpeg" url="(.+?)"/></item>').findall(response)
  season = path[index:] + '/'
  for name, link, descr, pubDate, img in videos:
    if link.find(season) > -1:
      name = tools.normalizeText(name)
      iResEnd = img.rfind('.')
      iResStart = iResEnd - 3
      if img[iResStart:iResEnd] == '140':
        img = img[:iResStart] + '640' + img[iResEnd:]
      tools.addDir(handle, name, img, '', 'video', { 'title' : name, 'plot' : tools.normalizeText(descr), 'duration' : -1, 'director' : '' }, { 'action' : 'r', 'path' : link })


# Entry point.
#startTime = datetime.datetime.now()

handle = int(sys.argv[1])
params = tools.urlParametersToDict(sys.argv[2])
succeeded = True
idPlugin = 'plugin.mtvondemand'

if len(params) == 0: # Programmi.
  response = tools.getResponseUrl('http://ondemand.mtv.it/serie-tv')
  programs = re.compile('<h3 class="showpass"><a href="(.+?)"> <img class="lazy" height="105" width="140" src=".+?" data-original="(.+?)\?width=0&amp;amp;height=0&amp;amp;matte=true&amp;amp;matteColor=black&amp;amp;quality=0\.91" alt=".+?"/><p><strong>(.+?)</strong>(.+?)</p>').findall(response)
  for link, img, name, descr in programs:
    name = tools.normalizeText(name)
    tools.addDir(handle, name, img, '', 'video', { 'title' : name, 'plot' : tools.normalizeText(descr), 'duration' : -1, 'director' : '' }, { 'action' : 's', 'path' : link })
elif params['action'] == 's': # Stagioni.
  response = tools.getResponseUrl('http://ondemand.mtv.it' + params['path'])
  if response.find('<h2>Troppo tardi! <b>&#9787;</b></h2>') == -1:
    seasonsMenu = re.compile('<ul class="nav">(.+?)</ul>').findall(response)
    seasons = re.compile('href="(.+?)">(.+?)</a></li>').findall(seasonsMenu[0])
    if len(seasons) > 1:
      title = tools.normalizeText(re.compile('<h1 itemprop="name">(.+?)</h1>').findall(response)[0])
      for link, season in seasons:
        season = tools.normalizeText(season)
        tools.addDir(handle, season, '', '', 'video', { 'title' : season, 'plot' : season + ' di ' + title, 'duration' : -1, 'director' : '' }, { 'action' : 'p', 'path' : link })
    else:
      getEpisodes(seasons[0][0])
  else:
    succeeded = False
    xbmcgui.Dialog().ok('MTV on demand', tools.getTranslation(idPlugin, 30001))
elif params['action'] == 'p': # Puntate.
  getEpisodes(params['path'])
elif params['action'] == 'r': # Risoluzioni.
  response = tools.getResponseUrl(params['path'])
  videoId = re.compile('<div class="MTVNPlayer".+? data-contenturi="(.+?)">').findall(response)
  if len(videoId) > 0:
    response = tools.getResponseUrl('http://intl.esperanto.mtvi.com/www/xml/media/mediaGen.jhtml?uri=mgid:uma:video:mtv.it:' + videoId[0][videoId[0].rfind(':') + 1:])
    streams = re.compile('<rendition cdn="akamai" duration="(.+?)".+?height="(.+?)".+?><src>(.+?)</src></rendition>').findall(response)
    streams.sort(key = itemgetter(1), reverse = True)
    idLabel = 30011 - len(streams)
    for duration, height, url in streams:
      title = tools.getTranslation(idPlugin, idLabel)
      idLabel += 1
      tools.addLink(handle, title, '', '', 'video', { 'title' : title, 'plot' : '', 'duration' : str( int( duration ) / 60 ), 'director' : '' }, url + ' swfUrl=http://media.mtvnservices.com/player/prime/mediaplayerprime.2.3.7.swf?uri=' + params['path'] + '.swf swfVfy=true')
  else:
    succeeded = False
    xbmcgui.Dialog().ok('MTV on demand', tools.getTranslation(idPlugin, 30002))

#print 'MTV on demand azione ' + str(datetime.datetime.now() - startTime)
xbmcplugin.endOfDirectory(handle, succeeded)
