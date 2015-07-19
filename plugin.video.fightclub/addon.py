#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Fight Club Kodi Plugin
    Copyright (C) 2015 SteveRob
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    '''
import os
import string
import sys
import re
import urlresolver
import urllib
import xbmc, xbmcaddon, xbmcplugin, xbmcgui

from t0mm0.common.addon import Addon
from t0mm0.common.net import Net

BASEURL = 'http://wweo.us/'
MEDIA_PAGE_REQ_URL = 'http://wweo.us/index.php'
MEDIA_REQ_URL = 'http://wweo.us/gkplugins/plugins/plugins_player.php'

VIEW_IDS = {
    'skin.confluence': {
        'thumb': 500,
        'biglist': 51
    },
    'skin.aeon.nox.silvo': {
        'thumb': 500,
        'biglist': 507
    },
    'default': {
        'thumb': 500,
        'biglist': 50
    }
}

skin = xbmc.getSkinDir()
this_view = VIEW_IDS.get(skin)

showfilm = '1'
itemsperpage = '13'
itemsperrow = '1'
categoryid = ''

addon_id = 'plugin.video.fightclub'

net = Net()
addon = Addon(addon_id, sys.argv)

#PATHS
AddonPath = addon.get_path()
skin_path = AddonPath+"/resources/skins/default/"
media_path = skin_path+"media/"

from universal import watchhistory

mode = addon.queries['mode']
url = addon.queries.get('url', '')
title = addon.queries.get('title', '')
img = addon.queries.get('img', '')
section = addon.queries.get('section', '')
page = addon.queries.get('page', '')
mediaid = addon.queries.get('mediaid', '')
typ = addon.queries.get('type', '')
historytitle = addon.queries.get('historytitle', '')
historylink = addon.queries.get('historylink', '')
iswatchhistory = addon.queries.get('watchhistory', '')
queued = addon.queries.get('queued', '')

def WatchedCallback():
    print 'Video completed successfully.'


def unescape(text):
    try:
        rep = {"&nbsp;": " ","\n": "","\t": ""}
        for s, r in rep.items():
            text = text.replace(s, r)
        
        # remove html comments
        text = re.sub(r"<!--.+?-->", "", text)
        text = re.sub(r"[^\x00-\x7F]+"," ", text)

    except TypeError:
        pass
    
    return text


def setView(view):
    if this_view:
        set_view = this_view.get(view)
    else:
        set_view = VIEW_IDS.get("default").get(view)
    
    cmd = 'Container.SetViewMode(%s)' % set_view
    xbmc.executebuiltin(cmd)


def MainMenu():  #home-page
    addon.add_directory({'mode' : 'SubMenu', 'section' : 'WWE'}, {'title':  'WWE'}, img=media_path+'wwe.png' )
    addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/12/', 'page' : '1','type' : 'TNA'}, {'title':  'TNA'}, img=media_path+'tna.png' )
    addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/45/', 'page' : '1','type' : 'NJPW'}, {'title':  'NJPW'}, img=media_path+'njpw.png' )
    addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/18/', 'page' : '1','type' : 'UFC'}, {'title':  'UFC'}, img=media_path+'ufc.png' )
    addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/46/', 'page' : '1','type' : 'LUCHA'}, {'title':  'LUCHA'}, img=media_path+'lucha.png' )
    addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/34/', 'page' : '1','type' : 'RKK'}, {'title':  'Ring Ka King'}, img=media_path+'rkk.png' )
    addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/43/', 'page' : '1', 'type' : 'ROH'}, {'title':  'Ring of Horror'}, img=media_path+'roh.png' )
    addon.add_directory({'mode' : 'Menu', 'section' : 'Categories'}, {'title':  'All Categories'}, img=media_path+'all_cat.png' )
    addon.add_directory({'mode' : 'Browse', 'section' : '1', 'page' : '1'}, {'title':  'Newest Added'}, img=media_path+'new.png' )
    addon.add_directory({'mode' : 'SubMenu', 'section' : 'F_V_R'}, {'title':  'Featured/Viewed/Rated'}, img=media_path+'f_v_r.png' )
    addon.add_directory({'mode' : 'Menu', 'section' : 'Type of Match', 'type' : 'ToM'}, {'title':  'Matches By Type'}, img=media_path+'m_b_t.png' )
    addon.add_directory({'mode' : 'Search', 'section' : 'SEARCH'}, {'title':  'Search'}, img=media_path+'search.png' )
    addon.add_directory({'mode' : 'SubMenu', 'section' : 'A_Z'}, {'title':  'List Matches A-Z'}, img=media_path+'a_z.png' )
    
    xbmcplugin.setContent(int(sys.argv[1]), content='files')
    setView("thumb")
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

def GetTitles(section, page):
    url_content = net.http_POST(MEDIA_PAGE_REQ_URL,
                                {'showfilm' : showfilm,
                                'num' : section,
                                'page' : page,
                                'number' : itemsperpage,
                                'apr' : itemsperrow,
                                'cat_id' : categoryid}
    ).content
        
    items = re.search(r"(?s)<table(.+?)pagecurrent", url_content)
    if items:
        items = addon.unescape(items.group(1))
        items = unescape(items)
        for item in re.finditer(r"<a.*?href=\"(.+?)\".*?title=\"(.+?)\".*?<img.*?src=\"(.+?)\"", items):
            item_url = BASEURL + item.group(1)
            item_img = item.group(3)
            item_title = item.group(2)
            addon.add_directory({'mode': 'GetLinks', 'url': item_url, 'title': item_title, 'img': item_img, 'type' : typ }, {'title': item_title}, img= item_img)

    if re.search(r"(?s)LAST", url_content):
        addon.add_directory({'mode': 'Browse', 'section' : section, 'page' : str(int(page) + 1), 'type' : typ }, {'title': 'Next Page >>'}, img=media_path+'next.png')
    
    xbmcplugin.setContent(int(sys.argv[1]), content='movies')
    setView("thumb")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def GetPage(url, page):
    
    url_content = net.http_GET(MEDIA_PAGE_REQ_URL + url + '/' + page).content
    items = re.search(r"(?s)player_field.*?<table(.+?)<td></td>", url_content)
    
    if items:
        
        items = addon.unescape(items.group(1))
        items = unescape(items)
        
        for item in re.finditer(r"<a.*?href=\"(.+?)\".*?title=\"(.+?)\".*?<img.*?src=\"(.+?)\"", items):
            item_url = MEDIA_PAGE_REQ_URL + item.group(1)
            item_img = item.group(3)
            item_title = item.group(2)
            addon.add_directory({'mode': 'GetLinks', 'url': item_url, 'title': item_title, 'img': item_img, 'type' : typ }, {'title': item_title}, img= item_img)
        
        if items:
            if re.search(r"(?s)>LAST<", items):
                addon.add_directory({'mode': 'Page', 'url' : url, 'page' : str(int(page) + 1), 'type' : typ }, {'title': 'Next Page >>'}, img=media_path+'next.png')
    
    xbmcplugin.setContent(int(int(sys.argv[1])), content='files')
    setView("thumb")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def Menu(section):
    
    url_content = net.http_GET(BASEURL).content
    
    items = re.search(r"(?s)" + section + "(.+?)</table>", url_content)
    
    if items:
        
        items = addon.unescape(items.group(1))
        items = unescape(items)
        
        for item in re.finditer(r"<a.*?href=(.+?)><b>(.+?)</b>", items):
            
            addon.add_directory({'mode' : 'Page', 'url' : item.group(1), 'page' : '1', 'type' : typ}, {'title':  item.group(2)}, img=media_path+'list.png')


    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmc.executebuiltin('XBMC.Container.SetSortMethod(1)')
    xbmcplugin.setContent(int(int(sys.argv[1])), content='files')
    
    setView("biglist")
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


def SubMenu(section):
    if section == 'F_V_R':
        addon.add_directory({'mode' : 'Browse', 'section' : '8', 'page' : '1', 'type' : 'Featured'}, {'title':  'Featured'}, img=media_path+'featured.png')
        addon.add_directory({'mode' : 'Browse', 'section' : '2', 'page' : '1', 'type' : 'TVT'}, {'title':  'Top Viewed (Today)'}, img=media_path+'viewed.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/list/view', 'page' : '1', 'type' : 'TVAT'}, {'title':  'Top Viewed (All)'}, img=media_path+'viewed.png')
        addon.add_directory({'mode' : 'Browse', 'section' : '4', 'page' : '1', 'type' : 'TRT'}, {'title':  'Top Rated (Today)'}, img=media_path+'f_v_r.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/list/rate', 'page' : '1', 'type' : 'TRAT'}, {'title':  'Top Rated (All)'}, img=media_path+'f_v_r.png')
        
        view_mode="thumb"
        xbmcplugin.setContent(int(int(sys.argv[1])), content='files')

    elif section == 'A_Z':
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/0-9/', 'page' : '1', 'type' : 'A_Z'}, {'title':  '0-9'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/A/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'A'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/B/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'B'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/C/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'C'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/D/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'D'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/E/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'E'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/F/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'F'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/G/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'G'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/H/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'H'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/I/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'I'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/J/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'J'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/K/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'K'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/L/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'L'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/M/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'M'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/N/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'N'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/O/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'O'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/P/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'P'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/Q/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'Q'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/R/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'R'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/S/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'S'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/T/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'T'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/U/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'U'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/V/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'V'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/W/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'W'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/X/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'X'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/Y/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'Y'}, img=media_path+'list.png')
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/quick_search/Z/', 'page' : '1', 'type' : 'A_Z'}, {'title':  'Z'}, img=media_path+'list.png')
        
        view_mode="biglist"
        xbmcplugin.setContent(int(int(sys.argv[1])), content='files')

    elif section == 'WWE':
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/1/', 'page' : '1','type' : 'WWE-RAW'}, {'title':  'RAW'}, img=media_path+'raw.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/2/', 'page' : '1','type' : 'WWE-SMACKDOWN'}, {'title':  'Smackdown'}, img=media_path+'smackdown.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/4/', 'page' : '1','type' : 'WWE-NXT'}, {'title':  'NXT'}, img=media_path+'nxt.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/5/', 'page' : '1','type' : 'WWE-SUPERSTARS'}, {'title':  'Superstars'}, img=media_path+'superstars.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/36/', 'page' : '1','type' : 'WWE-MAINEVENT'}, {'title':  'Main Event'}, img=media_path+'mainevent.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/41/', 'page' : '1','type' : 'WWE-PPV'}, {'title':  'Pay Per View'}, img=media_path+'ppv.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/23/', 'page' : '1','type' : 'WWE-DVD'}, {'title':  'DVD'}, img=media_path+'wwe.png' )
        addon.add_directory({'mode' : 'Page', 'url' : '?movie=/category/42/', 'page' : '1','type' : 'WWE-NETWORK'}, {'title':  'WWE Network'}, img=media_path+'wwe.png' )
        
        view_mode="thumb"
        xbmcplugin.setContent(int(int(sys.argv[1])), content='files')
    
    setView(view_mode)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

def Search():
    dialog = xbmcgui.Dialog()
    d = dialog.input("Enter Search", type=xbmcgui.INPUT_ALPHANUM)
    d = urllib.quote_plus(d)
    GetPage(str("?movie=/search/")+str(d), '1')

def ReformatHostedMediaUrl(url):
    myurl = url
    
    myurl = myurl.replace("-nocookie", "")
    if 'youtube' in myurl:
        return myurl
    
    if re.search("\?", myurl):
        myurl = myurl[0:myurl.index('?')]
    
    return myurl

def GetLinks(url):
    
    url_content = net.http_GET(url).content
    
    episode_id = re.search(r"return player\((.+?)\)", url_content).group(1)
    url_content = net.http_POST(MEDIA_PAGE_REQ_URL,{'watch' : '1','episode_id' : episode_id }).content
        
    search_for_parts = re.search(r"return player\((.+?)\)", url_content)
    if search_for_parts:
        related_episodes = re.search(r"(?s)BEGIN RELATE EPISODE(.+?) END ", url_content)
        if related_episodes:
            related_episodes = addon.unescape(related_episodes.group(1))
            related_episodes = unescape(related_episodes)
                
            for episode_meta in re.finditer(r"<tr><td>(.+?):.*?<td>(.+?)</td>", related_episodes):
                item_title = title + ' - ' + episode_meta.group(1)
                episodes = episode_meta.group(2)
                    
                curr_item = re.search(r"\[(.+?)\]", episodes)
                if curr_item:
                    queries = {'mode': 'GetMedia', 'mediaid' : episode_id, 'title' : item_title + ' -' + curr_item.group(1), 'type' : typ, 'historytitle' : title, 'historylink' : sys.argv[0]+sys.argv[2] }
                    contextMenuItems = []
                    from universal import playbackengine
                    contextMenuItems.insert(0, ('Queue Item', playbackengine.QueueItem(addon_id, item_title + ' -' + curr_item.group(1), addon.build_plugin_url( queries ) ) ) )
                        
                    addon.add_directory(queries, {'title': item_title + ' -' + curr_item.group(1) }, contextMenuItems, context_replace=False, img=media_path+'video.png')
                        
                    for episode in re.finditer(r"return player\((.+?)\).*?<b>(.+?)</b>", episodes):
                        queries = {'mode': 'GetMedia', 'mediaid' : episode.group(1), 'title' : item_title + ' - ' + episode.group(2), 'type' : typ, 'historytitle' : title, 'historylink' : sys.argv[0]+sys.argv[2]}
                        contextMenuItems = []
                        from universal import playbackengine
                        contextMenuItems.insert(0, ('Queue Item', playbackengine.QueueItem(addon_id, item_title + ' - ' + episode.group(2), addon.build_plugin_url( queries ) ) ) )
                            
                        addon.add_directory(queries, {'title': item_title + ' - ' + episode.group(2)}, contextMenuItems, context_replace=False, img=media_path+'video.png')

    else:
        #GetMedia(episode_id)
        queries = {'mode': 'GetMedia', 'mediaid' : episode_id, 'title' : title, 'type' : typ }
            
        contextMenuItems = []
        from universal import playbackengine
        contextMenuItems.insert(0, ('Queue Item', playbackengine.QueueItem(addon_id, title, addon.build_plugin_url( queries ) ) ) )
        
        addon.add_directory(queries, {'title': title}, contextMenuItems, context_replace=False, img=media_path+'video.png')
        
        xbmcplugin.setContent(int(int(sys.argv[1])), content='files')
        setView("biglist")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def GetMedia(mediaid):
    
    from universal import playbackengine
    
    if queued == 'true':
        wh = watchhistory.WatchHistory(addon_id)
        url_content = net.http_POST(MEDIA_PAGE_REQ_URL,{'watch' : '1','episode_id' : mediaid }).content
        media_req_data = re.search(r"proxy\.link\=(.+?)\"", url_content)
        if media_req_data:
           media_req_data = media_req_data.group(1)
           
           media_response_data = net.http_POST(MEDIA_REQ_URL, {'url':media_req_data}).content
           
           media_url = ''
           media_size = 0
           
           media_content = re.search(r"(?s)\"media\":(.+?),\"description\":", media_response_data)
           if media_content:
               media_links = addon.unescape(media_content.group(1))
               media_links = unescape(media_links)
               for link in re.finditer("\"url\":\"(.+?)\",\"height\":(.+?),\"width\":(.+?),\"type\":\"(.+?)\"", media_links):
               
                   if (link.group(4).startswith("image")):
                       continue
                   
                   size = int(link.group(2)) + int(link.group(3))
                   if (size <= media_size):
                       continue
                   
                   media_url = link.group(1)
                   media_size = size
               
               if media_url:
               
                   player = playbackengine.Play(resolved_url=media_url, addon_id=addon_id, video_type='wweonline',title=title,season='', episode='', year='', watchedCallback=WatchedCallback)
                   
                   # add watch history item
                   if historylink:
                       wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True, parent_title=historytitle)
                       wh.add_directory(historytitle, historylink, img=img, level='1')
                   else:
                       wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True)
                   
                   player.KeepAlive()
                                   
                                                               
        else:
            check_for_hosted_media = re.search(r"(?s)<embed.*?flashvars.+?file=(.+?)[&\"]{1}", url_content)
            if check_for_hosted_media:
                hosted_media_url = check_for_hosted_media.group(1)
                hosted_media_url = ReformatHostedMediaUrl(hosted_media_url)
                hosted_media = urlresolver.HostedMediaFile(url=hosted_media_url)
                if hosted_media:
                    resolved_media_url = urlresolver.resolve(hosted_media_url)
                    if resolved_media_url:

                        player = playbackengine.Play(resolved_url=resolved_media_url, addon_id=addon_id, video_type='wweonline',
                        title=title,season='', episode='', year='', watchedCallback=WatchedCallback)

                        # add watch history item                        
                        if historylink:
                            wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True, parent_title=historytitle)
                            wh.add_directory(historytitle, historylink, img=img, level='1')
                        else:
                            wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True)

                        player.KeepAlive()
            else:
                check_for_hosted_media = re.search(r"(?s)<embed.*?src=\"(.+?)\"", url_content)
                if check_for_hosted_media:        
                    hosted_media_url = check_for_hosted_media.group(1)
                    hosted_media_url = ReformatHostedMediaUrl(hosted_media_url)
                    hosted_media = urlresolver.HostedMediaFile(url=hosted_media_url)
                    if hosted_media:
                        resolved_media_url = urlresolver.resolve(hosted_media_url)
                        if resolved_media_url:
                            player = playbackengine.Play(resolved_url=resolved_media_url, addon_id=addon_id, video_type='wweonline', title=title,season='', episode='', year='', watchedCallback=WatchedCallback)

                            # add watch history item
                            if historylink:
                                wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True, parent_title=historytitle)
                                wh.add_directory(historytitle, historylink, img=img, level='1')
                            else:
                                wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True)

                            player.KeepAlive()
                else:
                    check_for_hosted_media = re.search(r"(?s)<iframe.*?src=\"(.+?)\"", url_content)
                    if check_for_hosted_media:        
                        hosted_media_url = check_for_hosted_media.group(1)
                        #hosted_media_url = ReformatHostedMediaUrl(hosted_media_url)
                        hosted_media = urlresolver.HostedMediaFile(url=hosted_media_url)
                        if hosted_media:
                            resolved_media_url = urlresolver.resolve(hosted_media_url)
                            if resolved_media_url:

                                player = playbackengine.Play(resolved_url=resolved_media_url, addon_id=addon_id, video_type='wweonline',title=title,season='', episode='', year='', watchedCallback=WatchedCallback)

                                # add watch history item
                                if historylink:
                                    wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True, parent_title=historytitle)
                                    wh.add_directory(historytitle, historylink, img=img, level='1')
                                else:
                                    wh.add_video_item(title, sys.argv[0]+sys.argv[2], img=img, is_playable=True)

                                player.KeepAlive()
    else:
      playbackengine.PlayInPL(title, img=img)
                                                                                                  
                                                                                                  
if mode == 'main':
    MainMenu()
elif mode == 'SubMenu':
    SubMenu(section)
elif mode == 'Search':
    Search()
elif mode == 'Browse':
    GetTitles(section, page)
elif mode == 'Page':
    GetPage(url, page)
elif mode == 'Menu':
    Menu(section)
elif mode == 'GetLinks':
    GetLinks(url)
elif mode == 'GetMedia':
    GetMedia(mediaid)
elif mode == 'universalsettings':    
    from universal import _common
    _common.addon.show_settings()
                                                                                                  
