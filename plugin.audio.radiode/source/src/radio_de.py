
import os
import html
import xbmcaddon
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

from datetime import datetime

from addon_utils import ListItem, DataHandler, get_text_from_keyboard
from radionet_api import RadionetApi
from m3u_parser import M3UParser


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


SEARCH_MENU_STATIONS = [
    # !!! memo to myself: don't rename 'mode' data, data is used in lists !!!
    {'mode': 'do_search_stations', 'data': {'name': 'New search', 'query': '', 'cm': None}},
]

SEARCH_MENU_PODCASTS = [
    # !!! memo to myself: don't rename 'mode' data, data is used in lists !!!
    {'mode': 'do_search_podcasts', 'data': {'name': 'New search', 'query': '', 'cm': None}},
]

PODCAST_MENU =  [
    {'mode': 'root', 'data': {'name': 'Switch to radio view', 'view': 'radio'}},
    {'mode': 'get_my_episodes', 'data': {'name': 'My episodes'}},
    {'mode': 'get_my_podcasts', 'data': {'name': 'My podcasts'}},
    {'mode': 'get_recently_episodes', 'data': {'name': 'Recently played'}},
    {'mode': 'search_podcast', 'data': {'name': 'Search'}},
    {'mode': 'get_podcast_charts', 'data': {'name': 'Podcast charts'}},
    {'mode': 'get_top_podcast_categories', 'data': {'name': 'Top categories'}},
    {'mode': 'get_all_podcast_categories', 'data': {'name': 'All categories'}},
]

RADIO_MENU =  [
    {'mode': 'root', 'data': {'name': 'Switch to podcast view', 'view': 'podcast'}},
    {'mode': 'get_my_stations', 'data': {'name': 'My stations'}},
    {'mode': 'get_recently_stations', 'data': {'name': 'Recently played'}},
    {'mode': 'search_station', 'data': {'name': 'Search', 'query': ''}},
    {'mode': 'get_local_stations', 'data': {'name': 'Local stations'}},
    {'mode': 'get_genres', 'data': {'name': 'Browse by genre'}},
    {'mode': 'get_topics', 'data': {'name': 'Browse by topic'}},
    {'mode': 'get_countries', 'data': {'name': 'Browse by country'}},
    {'mode': 'get_cities', 'data': {'name': 'Browse by city'}},
    {'mode': 'get_regions', 'data': {'name': 'Browse by region'}},
    {'mode': 'get_languages', 'data': {'name': 'Browse by language'}},
    #============================================================================================
    # testing only
    #============================================================================================
    # {'mode': '_test_search', 'data': {'name': '_test_search'}},
    # {'mode': '_test_get_similar', 'data': {'name': '_test_get_similar'}},
    # {'mode': '_test_get_family', 'data': {'name': '_test_get_family'}},
    # {'mode': '_test_get_local_stations', 'data': {'name': '_test_get_local_stations'}},
    # {'mode': '_test_get_genres', 'data': {'name': '_test_get_genres'}},
    # {'mode': '_test_get_cities', 'data': {'name': '_test_get_cities'}},
    # {'mode': '_test_get_countries', 'data': {'name': '_test_get_countries'}},
    # {'mode': '_test_get_stations_by_char', 'data': {'name': '_test_get_stations_by_char'}},
    # {'mode': '_test_get_now_playing', 'data': {'name': '_test_get_now_playing'}},
    # {'mode': '_test_get_songs', 'data': {'name': '_test_get_songs'}},
    # {'mode': '_test_get_station_details', 'data': {'name': '_test_get_station_details'}},
    # {'mode': '_test_get_stations_by_genre', 'data': {'name': '_test_get_stations_by_genre'}},
    # {'mode': '_test_get_stations_by_city', 'data': {'name': '_test_get_stations_by_city'}},
    # {'mode': '_test_get_topics', 'data': {'name': '_test_get_topics'}},
    # {'mode': '_test_get_stations_by_topic', 'data': {'name': '_test_get_stations_by_topic'}},
    # {'mode': '_test_get_tags', 'data': {'name': '_test_get_tags'}},
    # {'mode': '_test_get_podcast_details', 'data': {'name': '_test_get_podcast_details'}},
    # {'mode': '_test_get_podast_episodes', 'data': {'name': '_test_get_podast_episodes'}},
    # {'mode': '_test_get_podcasts_by_author', 'data': {'name': '_test_get_podcast_by_author'}},
    # {'mode': '_test_get_podcasts_by_category', 'data': {'name': '_test_get_podcast_by_category'}},
    # {'mode': '_test_get_podcast_categories', 'data': {'name': '_test_get_podcast_categories'}},
    # {'mode': '_test_search_podcast', 'data': {'name': '_test_search_podcast'}},
    # {'mode': '_test_get_podcast_charts', 'data': {'name': '_test_get_podcast_category_charts'}},
]

CM_MAP = {
    # !!! don't rename keys (search_cm, recently_cm, add_station, remove_station) !!!
    # !!! keys are maybe used in legacy v1.0.1 lists (data: {'cm': key}) !!! 
    'search_cm': [
        {'name': 'Remove from search', 'mode': 'remove_from_search_stations', 'data': {}, 'action': 'RunPlugin'},
    ],
    'recently_cm': [
        {'name': 'Add to my stations', 'mode': 'add_to_stations', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Show similar stations', 'mode': 'get_similar', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Show station family', 'mode': 'get_family', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Export to IPTV Simple', 'mode': 'add_to_iptv', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Recently played songs', 'mode': 'recently_played_songs', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Remove from recently', 'mode': 'remove_from_recently_stations', 'data': {}, 'action': 'RunPlugin'},
    ],
    'add_station': [
        {'name': 'Add to my stations', 'mode': 'add_to_stations', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Show similar stations', 'mode': 'get_similar', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Show station family', 'mode': 'get_family', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Export to IPTV Simple', 'mode': 'add_to_iptv', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Recently played songs', 'mode': 'recently_played_songs', 'data': {}, 'action': 'RunPlugin'},
    ],
    'remove_station': [
        {'name': 'Show similar stations', 'mode': 'get_similar', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Show station family', 'mode': 'get_family', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Export to IPTV Simple', 'mode': 'add_to_iptv', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Recently played songs', 'mode': 'recently_played_songs', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Remove from my stations', 'mode': 'remove_from_stations', 'data': {}, 'action': 'RunPlugin'},
    ],
    'search_podcast_cm': [
        {'name': 'Remove from search', 'mode': 'remove_from_search_podcasts', 'data': {}, 'action': 'RunPlugin'},
    ],
    'recently_episodes_cm': [
        {'name': 'Show episodes', 'mode': 'show_podcast_episodes', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Add to my episodes', 'mode': 'add_to_episodes', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Remove from recently', 'mode': 'remove_from_recently_episodes', 'data': {}, 'action': 'RunPlugin'},
    ],
    'add_podcast_cm': [
        {'name': 'Show description', 'mode': 'show_podcast_description', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Add to my podcasts', 'mode': 'add_to_podcasts', 'data': {}, 'action': 'RunPlugin'},
    ],
    'remove_podcast_cm': [
        {'name': 'Show description', 'mode': 'show_podcast_description', 'data': {}, 'action': 'RunPlugin'},
        {'name': 'Remove from my podcasts', 'mode': 'remove_from_podcasts', 'data': {}, 'action': 'RunPlugin'},
    ],
    'add_episode_cm': [
        {'name': 'Add to my episodes', 'mode': 'add_to_episodes', 'data': {}, 'action': 'RunPlugin'},
    ],
    'remove_episode_cm': [
        {'name': 'Show episodes', 'mode': 'show_podcast_episodes', 'data': {}, 'action': 'Container.Refresh'},
        {'name': 'Remove from my episodes', 'mode': 'remove_from_episodes', 'data': {}, 'action': 'RunPlugin'},
    ],
}




class RadioDE():
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_id = self.addon.getAddonInfo('id')
        self.addon_name = self.addon.getAddonInfo('name')
        self.log_name = self.addon_name.replace(' ', '_')
        self.addon_path = None
        self.addon_handle = None
        
        self.min_cnt = self.addon.getSettingInt('min_cnt')
        self.show_all_languages = self.addon.getSettingBool('show_all_languages')
        self.show_all_countries = self.addon.getSettingBool('show_all_countries')
        self.show_all_regions = self.addon.getSettingBool('show_all_regions')
        self.show_all_cities = self.addon.getSettingBool('show_all_cities')
        self.icon = os.path.join(CURRENT_DIR, '..', 'icon.png')
        self.fanart_radio = os.path.join(CURRENT_DIR, '..', 'fanart.jpg')
        self.fanart_podcast = os.path.join(CURRENT_DIR, '..', 'fanart_podcast.jpg')
        self._set_fanart()
        
        region = self.addon.getSetting('radio_region').lower()
        self.radio = RadionetApi(region)
        
        self.search_list_stations = 'search'
        self.recent_list_stations = 'recent'
        self.search_list_podcasts = 'search_podcasts'
        self.recent_list_episodes = 'recent_episodes'
        self.my_stations_list = 'stations'
        self.my_podcasts_list = 'podcasts'
        self.my_episodes_list = 'episodes'
        
        self.dh = DataHandler()
        self.dh.register_path(self.my_stations_list, '/.radiode', 'use_xchange_folder', 'xchange_folder')
        self.dh.register_path(self.my_podcasts_list, '/.radiode', 'use_xchange_folder', 'xchange_folder')
        self.dh.register_path(self.my_episodes_list, '/.radiode', 'use_xchange_folder', 'xchange_folder')
    
    
    def set_addon_data(self, addon_path, addon_handle):
        self.addon_path = addon_path
        self.addon_handle = addon_handle


    def root(self, data):
        update = False
        view = data.get('view')
        
        if None == view:
            view = self.addon.getSetting('current_view')
        
        if 'radio' == view:
            if self._set_current_view('radio'):
                update = True
            self._handle_result('menu_list', RADIO_MENU, update_listing=update)
        else:
            if self._set_current_view('podcast'):
                update = True
            self._handle_result('menu_list', PODCAST_MENU, update_listing=update)
    

    #==================================================
    #--- radio functions
    #==================================================
    def recently_played_songs(self, data):
        station = data['id']
        api_result = self.radio.get_songs(station)
        
        songs = ''
        for item in api_result:
            songs += f'{item["rawInfo"]}\n'
        
        if not songs:
            songs = 'No information available'
        
        xbmcgui.Dialog().textviewer('Recently played songs', songs, usemono=False)
    
    
    def search_station(self, data):
        result = SEARCH_MENU_STATIONS
        history = self.dh.load_list(self.search_list_stations)
        result.extend(history)
        self._handle_result('menu_list', result, 'search_cm')
    
    
    def do_search(self, data):
        # legacy function call for version < v1.1.0
        self.do_search_stations(data)
    
    
    def do_search_stations(self, data):
        query = data['query']
        count, offset = self._get_count(data)
        
        if '' == query:
            query = get_text_from_keyboard()
            self._add_to_search(query, self.search_list_stations, 'do_search_stations')

        api_result = self.radio.search(query, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'do_search_stations', query=query)
        self._handle_result('stations_list', result, 'add_station')
        
        
    def remove_from_search_stations(self, data):
        self._remove_from_my_list(data, self.search_list_stations)
    
    
    def get_similar(self, data):
        station = data['id']
        count, offset = self._get_count(data, 50, 0)
        api_result = self.radio.get_similar(station, count)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_family(self, data):
        station = data['id']
        api_result = self.radio.get_family(station, 50)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_local_stations(self, data):
        count, offset = self._get_count(data)
        api_result = self.radio.get_local_stations(count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_local_stations')
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_genres(self, data):
        api_result = self.radio.get_shortlist_genres()
        result = self._unify_menu(api_result, 'get_stations_by_genre')
        self._handle_result('menu_list', result)
        
    
    def get_stations_by_genre(self, data):
        genre = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_stations_by_genre(genre, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_stations_by_genre', slug=genre)
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_topics(self, data):
        api_result = self.radio.get_shortlist_topics()
        result = self._unify_menu(api_result, 'get_stations_by_topic')
        self._handle_result('menu_list', result)
    
    
    def get_stations_by_topic(self, data):
        topic = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_stations_by_topic(topic, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_stations_by_topic', slug=topic)
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_countries(self, data):
        min_cnt = 0 if self.show_all_countries else self.min_cnt
        api_result = self.radio.get_countries(min_cnt)
        result = self._unify_menu(api_result, 'get_stations_by_country')
        self._handle_result('menu_list', result)
        
    
    def get_stations_by_country(self, data):
        country = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_stations_by_country(country, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_stations_by_country', slug=country)
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_cities(self, data):
        min_cnt = 0 if self.show_all_cities else self.min_cnt
        api_result = self.radio.get_cities(min_cnt)
        result = self._unify_menu(api_result, 'get_stations_by_city')
        self._handle_result('menu_list', result)
        
    
    def get_stations_by_city(self, data):
        city = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_stations_by_city(city, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_stations_by_city', slug=city)
        self._handle_result('stations_list', result, 'add_station')
        
    
    def get_regions(self, data):
        min_cnt = 0 if self.show_all_regions else self.min_cnt
        api_result = self.radio.get_regions(min_cnt)
        result = self._unify_menu(api_result, 'get_stations_by_region')
        self._handle_result('menu_list', result)
        
    
    def get_stations_by_region(self, data):
        region = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_stations_by_region(region, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_stations_by_region', slug=region)
        self._handle_result('stations_list', result, 'add_station')
    
    
    def get_languages(self, data):
        min_cnt = 0 if self.show_all_languages else self.min_cnt
        api_result = self.radio.get_languages(min_cnt)
        result = self._unify_menu(api_result, 'get_stations_by_language')
        self._handle_result('menu_list', result)
        
    
    def get_stations_by_language(self, data):
        language = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_stations_by_language(language, count, offset)
        result = self._unify_stations(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_stations_by_city', slug=language)
        self._handle_result('stations_list', result, 'add_station')
    

    def play_stream(self, data):
        # called from addon itself
        station_id = data["id"]
        name = data["name"]
        icon = data["icon_url"]
        url_resolved = None
        is_custom = False
        
        if "" != station_id:
            station = self.radio.get_station_details(station_id)
            if station.get('hasValidStreams'):
                name = station["name"]
                icon = station["logo300x300"]
                url_resolved = self._parse_stream_urls(station["streams"])
        else:
            url_resolved = data["stream_url"]
            is_custom = True
            
        if None != url_resolved:
            # simulate play error: 
            # url_resolved = url_resolved[2:]
            xbmc.log(f'[{self.log_name}] play stream {name}, custom: {is_custom}, id: {station_id}, url: {url_resolved}', xbmc.LOGINFO)
            self._add_to_recently_stations(data)
            li = xbmcgui.ListItem(label=name, path=url_resolved)
            li.setArt({'thumb': icon, 'icon': icon, 'fanart': self.fanart_radio})
            # ensure that list item gets interpreted as music item. otherwise can cause issue with json rpc calls, e.g. from favourites menu.
            # see https://github.com/MoojMidge/plugin.video.youtube/commit/3308ba48784866527cc6945dbcf5f994e8107cc7#diff-c272a8aaa71e5d90864871bc68c162cd995e0026723995e7eb055641d15c33e0R415
            li.setProperty('playlist_type_hint', str(xbmc.PLAYLIST_MUSIC))
        
            # clear playlist to ensure to not play next item in case of a play error. may lead to Kodi crash:
            # "Logic error due to two concurrent busydialogs, this is a known issue. The application will exit."
            # add just current item to playlist.
            playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
            playlist.clear()
            playlist.add(url=url_resolved, listitem=li, index=1)
            
            xbmcplugin.setResolvedUrl(self.addon_handle, True, listitem=li)
            return
        
        xbmc.log(f'[{self.log_name}] play error {name}, id: {station_id}, url: {url_resolved}', xbmc.LOGERROR)
        heading = name
        message = "Cannot play stream"
        xbmcgui.Dialog().notification(heading, message, xbmcgui.NOTIFICATION_WARNING)
    

    def play_station(self, data):
        # can be used to play a stream e.g. by using json RPC
        station_id = data["id"]
        name = data['id']
        url_resolved = None
        
        station = self.radio.get_station_details(station_id)
            
        if station.get('hasValidStreams'):
            name = station["name"]
            icon = station["logo300x300"]
            url_resolved = self._parse_stream_urls(station["streams"])
                
            # ensure that "data" keys are populated since play_stream() was called just with "id"
            data["name"] = name
            data["stream_url"] = url_resolved
            data["icon_url"] = icon
        
        if( None == url_resolved ):
            xbmc.log(f'[{self.log_name}] play_station error, id: {station_id}', xbmc.LOGERROR)
            heading = name
            message = "Cannot play stream"
            xbmcgui.Dialog().notification(heading, message, xbmcgui.NOTIFICATION_WARNING)
        else:
            xbmc.log(f'[{self.log_name}] play station {name}, id: {station_id}, url: {url_resolved}', xbmc.LOGINFO)
            self._add_to_recently_stations(data)
            li = xbmcgui.ListItem(label=name)
            li.setArt({'thumb': icon, 'icon': icon, 'fanart': self.fanart_radio})
            
            fullscreen = False
            if fullscreen:
                player = xbmc.Player()
                player.stop()
                player.play(url_resolved, li)
            else:
                playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
                playlist.clear()
                playlist.add(url=url_resolved, listitem=li, index=1)
    
                player = xbmc.Player()
                player.play()


    def get_my_stations(self, data):
        result = self.dh.load_list(self.my_stations_list)
        if '0' == self.addon.getSetting('sortmethod_stations'):
            result = sorted(result, key=lambda k: k['data']['name'].lower())
        self._handle_result('stations_list', result, 'remove_station')
    
    
    def add_to_stations(self, data):
        self._add_to_my_list(data, self.my_stations_list, 'play_stream', "Added to my stations")
    
    
    def remove_from_stations(self, data):
        self._remove_from_my_list(data, self.my_stations_list)

    
    def add_to_iptv(self, data):
        retry = 2
        
        while retry:
            retry -= 1
            
            m3u_file = self.addon.getSetting('m3u_file')
            m3u_bak = m3u_file + 'bak'
            
            if not xbmcvfs.exists(m3u_file):
                if retry:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Radio.de", "Please choose a valid m3u file")
                    self.addon.openSettings()
                else:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Radio.de", "No valid m3u file list specified")
                    return
            else:
                break
            
        tvg_name = data['name']
        group_title = 'Radio-DE'
        tvg_logo = data['icon_url']
        stream_url = self.radio.resolve_url(data['stream_url'])
        
        if None == stream_url:
            heading = tvg_name
            message = "No valid stream found"
            xbmcgui.Dialog().notification(heading, message, xbmcgui.NOTIFICATION_WARNING)
            return
        
        fh = xbmcvfs.File(m3u_file, 'r')
        m3u_dat = fh.read()
        fh.close()
        
        if tvg_name in m3u_dat:
            heading = tvg_name
            message = "Already exported to IPTV Simple"
            xbmcgui.Dialog().notification(heading, message, xbmcgui.NOTIFICATION_WARNING)
            return
        
        if not m3u_dat.startswith('#EXTM3U'):
            m3u_tmp = m3u_dat
            m3u_dat = '#EXTM3U\n'
            m3u_dat = m3u_dat + m3u_tmp
        
        fh = xbmcvfs.File(m3u_bak, 'w')
        fh.write(m3u_dat)
        fh.close() 

        new_line = f'#EXTINF:-1 tvg-name="{tvg_name}" group-title="{group_title}" radio="true" tvg-logo="{tvg_logo}",{tvg_name}\n'
        new_stream = f'{stream_url}\n'
        m3u_dat = m3u_dat + new_line + new_stream
            
        fh = xbmcvfs.File(m3u_file, 'w')
        fh.write(m3u_dat)
        fh.close()
        
        heading = tvg_name
        message = "Exported to IPTV Simple"
        xbmcgui.Dialog().notification(heading, message, self.icon)


    def import_iptv(self, data):
        default = self.addon.getSettingString('import_iptv_path')
        file_mask = '.m3u'
        file = xbmcgui.Dialog().browse(1, "Select m3u file", "", mask=file_mask, defaultt=default)
        
        if not file.endswith(file_mask):
            return

        head = os.path.split(file)[0] + '\\'
        self.addon.setSettingString('import_iptv_path', head)
        
        fh = xbmcvfs.File(file)
        data = fh.read()
        fh.close()
        
        parser = M3UParser()
        result = parser.parse_data(data)
        
        added = 0
        updated = 0
        my_stations = self.dh.load_list(self.my_stations_list)
        
        for item in result:
            add = True
            for station in my_stations:
                if station['data']['name'] == item['name']:
                    add = False
                    updated += 1
                    station['data']['icon_url'] = item['icon_url']
                    station['data']['stream_url'] = item['stream_url']
                    break
                
            if add:
                if False != item['is_radio']:
                    added += 1
                    record = {'data': {}, 'mode': ''}
                    record['mode'] = 'play_stream'
                    record['data']['id'] = ''
                    record['data']['name'] = item['name']
                    record['data']['icon_url'] = item['icon_url']
                    record['data']['stream_url'] = item['stream_url']
                    my_stations.append(record)
            
        self.dh.save_list(self.my_stations_list, my_stations)
        
        xbmc.log(f'[{self.log_name}] import_iptv: {added} stations added, {updated} stations updated', xbmc.LOGINFO)
        dialog = xbmcgui.Dialog()
        dialog.ok("Radio.de", f"{added} stations added\r\n{updated} stations updated")


    def get_recently_stations(self, data):
        result = self.dh.load_list(self.recent_list_stations)
        self._handle_result('stations_list', result, 'recently_cm')
        
        
    def remove_from_recently_stations(self, data):
        self._remove_from_recently(data, self.recent_list_stations)
            
            
    #==================================================
    #--- podcast functions
    #==================================================
    def get_top_podcast_categories(self, data):
        api_result = self.radio.get_podcast_categories()
        result = self._get_podcast_categories(api_result, False)
        self._handle_result('menu_list', result)


    def get_all_podcast_categories(self, data):
        api_result = self.radio.get_podcast_categories()
        result = self._get_podcast_categories(api_result, True)
        self._handle_result('menu_list', result)
        
        
    
    def get_podcasts_by_category(self, data):
        category = data['slug']
        count, offset = self._get_count(data)
        api_result = self.radio.get_podcasts_by_category(category, count, offset)
        result = self._unify_podcasts(api_result)
        result = self._add_next(api_result, result, count, offset, 'get_podcasts_by_category', slug=category)
        self._handle_result('menu_list', result, cm_menu='add_podcast_cm')
    
    
    def show_podcast_episodes(self, data):
        data['id'] = data['podcast_id']
        self.get_podcast_episodes(data)


    def get_podcast_episodes(self, data):
        podcast_id = data['id']
        count, offset = self._get_count(data)
        api_result = self.radio.get_podcast_episodes(podcast_id, count, offset)

        result = []
        if api_result:
            for item in api_result['episodes']:
                record = {'data': {}, 'mode': ''}

                ts = item['publishDate']
                date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
                
                record['data']['id'] = item['id']
                record['data']['podcast_id'] = podcast_id
                # record['data']['name'] = item['title']
                record['data']['name'] = date + ' | ' + item['title']
                record['data']['icon_url'] = item['parentLogo300x300']
                record['data']['stream_url'] = item['url']
                record['data']['duration'] = item['duration']
                record['data']['published'] = item['publishDate']
                record['mode'] = 'play_episode'

                result.append(record)
            
        # result = sorted(result, key=lambda k: k['data']['published'])
        result = self._add_next(api_result, result, count, offset, 'get_podcast_episodes', id=podcast_id)
        self._handle_result('episodes_list', result, cm_menu='add_episode_cm')
    
    
    def get_podcast_charts(self, data):
        api_result = self.radio.get_podcast_charts(count=100)
        result = self._unify_podcasts(api_result)
        self._handle_result('menu_list', result, cm_menu='add_podcast_cm')        
    
    
    def search_podcast(self, data):
        result = SEARCH_MENU_PODCASTS
        history = self.dh.load_list(self.search_list_podcasts)
        result.extend(history)
        self._handle_result('menu_list', result, 'search_podcast_cm')
    
    
    def do_search_podcasts(self, data):
        query = data['query']
        count, offset = self._get_count(data)
        
        if '' == query:
            query = get_text_from_keyboard()
            self._add_to_search(query, self.search_list_podcasts, 'do_search_podcasts')

        api_result = self.radio.search_podcast(query, count, offset)
        print(api_result)
        result = self._unify_podcasts(api_result)
        result = self._add_next(api_result, result, count, offset, 'do_search_podcasts', query=query)
        self._handle_result('menu_list', result, cm_menu='add_podcast_cm')
        
        
    def remove_from_search_podcasts(self, data):
        self._remove_from_my_list(data, self.search_list_podcasts)
        
    
    def get_my_episodes(self, data):
        result = self.dh.load_list(self.my_episodes_list)
        self._handle_result('episodes_list', result, 'remove_episode_cm')


    def get_my_podcasts(self, data):
        result = self.dh.load_list(self.my_podcasts_list)
        if '0' == self.addon.getSetting('sortmethod_podcasts'):
            result = sorted(result, key=lambda k: k['data']['name'].lower())
        self._handle_result('menu_list', result, 'remove_podcast_cm')


    def get_recently_episodes(self, data):
        result = self.dh.load_list(self.recent_list_episodes)
        self._handle_result('episodes_list', result, 'recently_episodes_cm')
            
            
    def remove_from_recently_episodes(self, data):
        self._remove_from_recently(data, self.recent_list_episodes)
    
    
    def add_to_podcasts(self, data):
        self._add_to_my_list(data, self.my_podcasts_list, 'get_podcast_episodes', "Added to my podcasts")
    
    
    def remove_from_podcasts(self, data):
        self._remove_from_my_list(data, self.my_podcasts_list)
    
    
    def add_to_episodes(self, data):
        self._add_to_my_list(data, self.my_episodes_list, 'play_episode', "Added to my episodes")
    
    
    def remove_from_episodes(self, data):
        self._remove_from_my_list(data, self.my_episodes_list)
    
    
    def show_podcast_description(self, data):
        podcast_id = data['id']
        api_result = self.radio.get_podcast_details(podcast_id)
        name = api_result[0]['name']
        description = api_result[0]['description']
        description = html.unescape(description)
        description = f"{description}\n\nHomepage: {api_result[0]['homepageUrl']}"
        xbmcgui.Dialog().textviewer(name, description, usemono=False)
        
        
    def play_episode(self, data):
        stream_url = data["stream_url"]
        name = data["name"]
        icon = data["icon_url"]
        
        #hmk: check for valid address? url_resolved = self.radio.resolve_url(stream_url)
        url_resolved = stream_url
            
        if None != url_resolved:
            # simulate play error: 
            # url_resolved = url_resolved[2:]
            xbmc.log(f'[{self.log_name}] play episide {name}, url_resolved: {url_resolved}', xbmc.LOGINFO)
            self._add_to_recently_episodes(data)
            li = xbmcgui.ListItem(label=name, path=url_resolved)
            li.setArt({'thumb': icon, 'icon': icon, 'fanart': self.fanart_podcast})
            li.setProperty('playlist_type_hint', str(xbmc.PLAYLIST_MUSIC))
            xbmcplugin.setResolvedUrl(self.addon_handle, True, listitem=li)
            return
        
        xbmc.log(f'[{self.log_name}] play error {name}, url: {stream_url}, url_resolved: {url_resolved}', xbmc.LOGERROR)
        heading = name
        message = "Cannot play stream"
        xbmcgui.Dialog().notification(heading, message, xbmcgui.NOTIFICATION_WARNING)


    #==================================================
    #--- private functions
    #==================================================
    def _get_count(self, data, count=20, offset=0):
        count = data.get('count', count)
        offset = data.get('offset', offset)
        return count, offset
        
        
    def _add_to_search(self, query, search_list, mode, max_items=50):
        result = self.dh.load_list(search_list)
        
        for item in result:
            if item['data']["query"] == query:
                return
        
        record = {'data': {}, 'mode': ''}
        record['mode'] = mode
        record['data']['name'] = query
        record['data']['query'] = query
        
        result.insert(0, record)
               
        if( max_items < len(result) ):
            result.pop(max_items)

        self.dh.save_list(search_list, result)
    
    
    def _add_to_recently_stations(self, data, max_items=50):
        self._add_to_recently(data, self.recent_list_stations, 'play_stream', max_items=max_items)
    
    
    def _add_to_recently_episodes(self, data, max_items=50):
        self._add_to_recently(data, self.recent_list_episodes, 'play_episode', max_items=max_items)
        
        
    def _add_to_recently(self, data, recently_list, mode, max_items=50):
        result = self.dh.load_list(recently_list)
        
        for item in result:
            # use "name" as key, "id" might be empty due to custom station
            if item['data']["name"] == data["name"]:
                result.remove(item)
                break
        
        record = {'data': {}, 'mode': ''}
        record['mode'] = mode
        record['data'] = data
        
        result.insert(0, record)
               
        if( max_items < len(result) ):
            result.pop(max_items)

        self.dh.save_list(recently_list, result)
        
        
    def _remove_from_recently(self, data, recently_list):
        result = self.dh.load_list(recently_list)
        
        for item in result:
            # use "name" as key, "id" might be empty due to custom station
            if item['data']["name"] == data['name']:
                result.remove(item)
                self.dh.save_list(recently_list, result)
                xbmc.executebuiltin( "Container.Refresh" )
                break
        
        
    def _add_to_my_list(self, data, my_list, mode, message):
        name = data["name"]
        result = self.dh.load_list(my_list)
        
        if( [] != result ):
            for item in result:
                if( item['data']["id"] == data["id"] ):
                    heading = name
                    message = "Already added to list"
                    xbmcgui.Dialog().notification(heading, message, xbmcgui.NOTIFICATION_WARNING)
                    return
                
        record = {}
        record['data'] = data
        record['mode'] = mode
        result.insert(0, record)
        
        self.dh.save_list(my_list, result)
        heading = name
        xbmcgui.Dialog().notification(heading, message, self.icon)
    
    
    def _remove_from_my_list(self, data, my_list):
        result = self.dh.load_list(my_list)
        
        for item in result:
            # use "name" as key, "id" might be empty due to custom station
            if item['data']["name"] == data["name"]:
                result.remove(item)
                self.dh.save_list(my_list, result)
                xbmc.executebuiltin( "Container.Refresh" )
                break

        
    def _unify_stations(self, data):
        result = []
        
        if data:
            stations = data.get('playables', [])
            for item in stations:
                record = {'data': {}, 'mode': ''}
                record['mode'] = 'play_stream'
                record['data']['id'] = item['id']
                record['data']['name'] = item['name']
                record['data']['icon_url'] = item['logo300x300']
                record['data']['stream_url'] = item['streams'][0]['url']
                result.append(record)

        return result
    
    
    def _unify_menu(self, data, mode):
        result = []

        if data:
            for item in data:
                record = {'data': {}, 'mode': ''}
                record['data']['count'] = 20
                record['data']['offset'] = 0
                record['data']['name'] = item['name']
                record['data']['slug'] = item['slug']
                record['mode'] = mode
                result.append(record)
            
        return result
        
        
    def _unify_podcasts(self, data):
        result = []
        if data:
            podcasts = data.get('playables', [])
            for item in podcasts:
                record = {'data': {}, 'mode': ''}
                record['data']['count'] = 20
                record['data']['offset'] = 0
                record['data']['id'] = item['id']
                record['data']['name'] = item['name']
                record['data']['icon_url'] = item['logo300x300']
                record['mode'] = 'get_podcast_episodes'
                result.append(record)
                
        return result

    
    def _get_podcast_categories(self, data, list_all=False):
        result = []
        if data:
            for main_item in data['categories']:
                # add main category
                record = {'data': {}, 'mode': ''}
                record['data']['count'] = 20
                record['data']['offset'] = 0
                record['data']['name'] = main_item['name']
                record['data']['slug'] = main_item['slug']
                record['mode'] = 'get_podcasts_by_category'
                result.append(record)
                
                if list_all:
                    sub_category = main_item.get('subCategories', [])
                    for item in sub_category:
                        # add all sub-categories
                        record = {'data': {}, 'mode': ''}
                        record['data']['count'] = 20
                        record['data']['offset'] = 0
                        record['data']['name'] = item['name']
                        record['data']['slug'] = item['slug']
                        record['mode'] = 'get_podcasts_by_category'
                        result.append(record)
                    
            result = sorted(result, key=lambda k: k['data']['name'].lower())
        
        return result
    

    def _add_next(self, data, result, count, offset, mode, **kwargs):
        if data:
            total = data.get('totalCount', 0)
            
            if  (count + offset) < total:
                record = {'data': {}, 'mode': ''}
                record['mode'] = mode
                record['data']['id'] = ''
                record['data']['name'] = 'Next >>'
                record['data']['icon_url'] = ''
                record['data']['stream_url'] = ''
                record["data"]['count'] = count
                record["data"]['offset'] = offset + count
                
                for key, val in kwargs.items():
                    record["data"][key] = val

                result.append(record)
            
        return result
        
        
    def _handle_result(self, mode, result, cm_menu=None, update_listing=False):
        li = ListItem(self.addon_path, self.addon_handle)

        if 'menu_list' == mode:
            for item in result:
                context_menu = cm_menu
                if 'cm' in item['data']:
                    context_menu = item['data']['cm']
                
                if context_menu:
                    for cm in CM_MAP[context_menu]:
                        # add 'data' from cm to 'data' from item
                        #hmk item['data'].update(cm['data'])
                        li.add_context_menu_item(cm['name'], cm['mode'], item['data'], cm['action'])
   
                icon = item['data'].get('icon_url')
                if not icon:
                    icon = self.icon

                li.add_item(item['data']["name"], item["mode"], item["data"], icon, self.fanart)
                
        elif 'stations_list' == mode:
            for item in result:
                context_menu = cm_menu
                # if 'cm' in item['data']:
                #     context_menu = item['data']['cm']

                if context_menu:
                    for cm in CM_MAP[context_menu]:
                        li.add_context_menu_item(cm['name'], cm['mode'], item['data'], cm['action'])

                if '' == item['data']["icon_url"]:
                    item["data"]['icon_url'] = self.icon
                
                if 'play_stream' == item["mode"]:
                    li.add_music_item(item['data']["name"], item["mode"], item["data"], item['data']["icon_url"], self.fanart)
                else:
                    li.add_item(item['data']["name"], item["mode"], item["data"], item['data']["icon_url"], self.fanart)
                
        elif 'episodes_list' == mode:
            for item in result:
                context_menu = cm_menu
                # if 'cm' in item['data']:
                #     context_menu = item['data']['cm']

                if context_menu:
                    for cm in CM_MAP[context_menu]:
                        li.add_context_menu_item(cm['name'], cm['mode'], item['data'], cm['action'])

                if '' == item['data']["icon_url"]:
                    item["data"]['icon_url'] = self.icon

                if 'play_episode' == item["mode"]:
                    li.add_music_item(item['data']["name"], item["mode"], item["data"], item['data']["icon_url"], self.fanart, item['data']['duration'])
                else:
                    li.add_item(item['data']["name"], item["mode"], item["data"], item['data']["icon_url"], self.fanart)
                    
        li.end_of_directory(update_listing=update_listing)
    

    def _parse_stream_urls(self, streams):
        stream_url = None
        
        for stream in streams:
            if 'VALID' == stream.get('status'):
                stream_url = self.radio.resolve_url(stream['url'])
                if stream_url:
                    break
            
        return stream_url
        

    def _set_current_view(self, current_view):
        last_view = self.addon.getSetting('current_view')
        
        if last_view != current_view:
            self.addon.setSetting('current_view', current_view)
            xbmc.log(f'[{self.log_name}] set current view to {current_view}', xbmc.LOGDEBUG)
            self._set_fanart()
            return True
        
        return False


    def _set_fanart(self):
        if not self.addon.getSettingBool('use_fanart'):
            self.fanart = ''
        elif 'radio' == self.addon.getSetting('current_view'):
            self.fanart = self.fanart_radio
        else:
            self.fanart = self.fanart_podcast





    
    # =====================================================================
    #--- test section
    #======================================================================
    def _test_search(self, data):
        query = 'rock antenn'
        count = 20
        offset = 0
        api_result = self.radio.search(query, count, offset)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result)
    
    
    def _test_get_similar(self, data):
        station = 'swr3'
        count = 20
        offset = 0
        api_result = self.radio.get_similar(station, count)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result)
    
    
    def _test_get_family(self, data):
        station = 'swr3'
        count = 20
        offset = 0
        api_result = self.radio.get_family(station, count)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result)
    
    
    def _test_get_local_stations(self, data):
        count = 20
        offset = 0
        api_result = self.radio.get_local_stations(count, offset)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result)
    
    
    def _test_get_genres(self, data):
        api_result = self.radio.get_shortlist_genres()
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_menu(api_result, 'get_stations_by_genre')
        self._handle_result('menu_list', result)
        
    
    def _test_get_stations_by_genre(self, data):
        genre = 'rock'
        count = 20
        offset = 0
        api_result = self.radio.get_stations_by_genre(genre, count, offset)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result)
    
    
    def _test_get_cities(self, data):
        api_result = self.radio.get_shortlist_cities()
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_menu(api_result, 'get_stations_by_cities')
        self._handle_result('menu_list', result)
        
    
    def _test_get_stations_by_city(self, data):
        # returns only station names, ids and frequencies
        city = 'berlin'
        count = 20
        offset = 0
        api_result = self.radio.get_stations_by_city(city, count, offset)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
                
        result = []
        for item in api_result:
            record = {'data': {}, 'mode': ''}
            record['mode'] = 'play_stream'
            record['data']['id'] = item['stationId']
            record['data']['name'] = item['stationName']
            record['data']['icon_url'] = ''
            record['data']['stream_url'] = ''
            result.append(record)

        self._handle_result('stations_list', result)
    
    
    def _test_get_countries(self, data):
        api_result = self.radio.get_shortlist_countries()
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_menu(api_result, 'get_stations_by_countries')
        self._handle_result('menu_list', result)
    
    
    def _test_get_stations_by_char(self, data):
        # returns only a list with stations, but no stream information available
        char = 'a'
        count = 20
        offset = 0
        api_result = self.radio.get_stations_by_char(char, count, offset)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = []
        
        if data:
            stations = data.get('playables', [])
            for item in stations:
                record = {'data': {}, 'mode': ''}
                record['mode'] = 'play_stream'
                record['data']['id'] = item['id']
                record['data']['name'] = item['name']
                record['data']['icon_url'] = ''
                record['data']['stream_url'] = ''
                result.append(record)

        self._handle_result('stations_list', result)
    
    
    def _test_get_now_playing(self, data):
        station = 'swr3'
        api_result = self.radio.get_now_playing(station)
        # result: [{"title":"Cruel Summer / Taylor Swift","stationId":"swr3"}]
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
    
    
    def _test_get_songs(self, data):
        station = 'swr3'
        api_result = self.radio.get_songs(station)
        # result: [{"rawInfo":"RELAX mit Marcus Barsch"},{"rawInfo":"Stumblin' in / CYRIL"},{"rawInfo":"Cruel Summer / Taylor Swift"},{"rawInfo":"Running back to you / Martin Jensen, Alle Farben \u0026 Nico Santos"},{"rawInfo":"Ride / Twenty One Pilots"},{"rawInfo":"Use somebody / Kings Of Leon"},{"rawInfo":"Houdini / Dua Lipa"},{"rawInfo":"SWR3 Nachrichten - auch zum Nachhören in der SWR3 App"},{"rawInfo":"Looking for love / Lena"},{"rawInfo":"RELAX mit Nicola Müntefering"}]
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
    
    
    def _test_get_station_details(self, data):
        station = 'swr3'
        api_result = self.radio.get_station_details(station)
        #[{"id":"swr3","name":"SWR3","lastModified":1700138079,"logo44x44":"https://d3kle7qwymxpcy.cloudfront.net/images/broadcasts/cd/0c/2275/3/c44.png","logo100x100":"https://d3kle7qwymxpcy.cloudfront.net/images/broadcasts/cd/0c/2275/3/c100.png","logo175x175":"https://d3kle7qwymxpcy.cloudfront.net/images/broadcasts/cd/0c/2275/3/c175.png","logo300x300":"https://d3kle7qwymxpcy.cloudfront.net/images/broadcasts/cd/0c/2275/3/c300.png","logo630x630":"","logo1200x1200":"","hasValidStreams":true,"streams":[{"url":"https://liveradio.swr.de/rddez3a/swr3/","contentFormat":"audio/aac","status":"VALID"},{"url":"https://d131.rndfnk.com/ard/swr/swr3/live/mp3/128/stream.mp3","contentFormat":"audio/mpeg","status":"VALID"}],"city":"Baden-Baden","country":"Germany","genres":["Top 40 \u0026 Charts","Pop"],"type":"STATION","description":"SWR3 plays the best pop songs, radio comics and live concerts around the clock.","homepageUrl":"https://www.swr3.de/","adParams":"advertising=true\u0026family=SWR3\u0026genres=Top 40 \u0026 Charts\u0026genres=Pop\u0026languages=German\u0026st_city=Baden-Baden\u0026st_cont=Europe\u0026st_country=Germany\u0026st_region=Baden-Wuerttemberg\u0026station=swr3\u0026type=radio_station","hideReferer":false,"continent":"Europe","languages":["German"],"families":["SWR3"],"region":"Baden-Wuerttemberg","genreTags":[{"systemName":"Top 40 \u0026 Charts","name":"Top 40 \u0026 Charts","slug":"top-40-and-charts","count":3289},{"systemName":"Pop","name":"Pop","slug":"pop","count":14085}],"cityTag":{"systemName":"Baden-Baden","name":"Baden-Baden","slug":"baden-baden","count":17},"parentTag":{"systemName":"Südwestrundfunk","name":"Südwestrundfunk","slug":"suedwestrundfunk","count":25},"familyTag":{"systemName":"SWR3","name":"SWR3","slug":"swr3","count":4},"languageTags":[{"systemName":"German","name":"German","slug":"german","count":15468}],"regionTag":{"systemName":"Baden-Wuerttemberg","name":"Baden-Wuerttemberg","slug":"baden-wuerttemberg","count":773},"countryTag":{"systemName":"Germany","name":"Germany","slug":"germany","count":14515},"frequencies":[{"area":"Haardtkopf","type":"FM","value":90},{"area":"Saarburg/Geisberg","type":"FM","value":90.6},{"area":"Koblenz/Naßheck (Waldesch)","type":"FM","value":91.6},{"area":"Alf-Bullay","type":"FM","value":92.6},{"area":"Bad Marienberg","type":"FM","value":92.8},{"area":"Kirn","type":"FM","value":93.3},{"area":"Rüdesheim","type":"FM","value":93.3},{"area":"Bad Kreuznach/Kauzenburg","type":"FM","value":93.5},{"area":"Mainz-Kastel","type":"FM","value":93.7},{"area":"Linz/Ginsterhahn","type":"FM","value":94.8},{"area":"Bornberg","type":"FM","value":97.5},{"area":"Idar-Oberstein","type":"FM","value":98.1},{"area":"Diez","type":"FM","value":98.2},{"area":"Trier/Markusberg","type":"FM","value":98.2},{"area":"Nierstein","type":"FM","value":98.4},{"area":"Scharteberg (Eifel)","type":"FM","value":98.5},{"area":"Bleialf","type":"FM","value":98.9},{"area":"Altenahr ","type":"FM","value":99.4},{"area":"Donnersberg","type":"FM","value":101.1},{"area":"Kettrichhof","type":"FM","value":107.2}],"rank":168,"shortDescription":"SWR3 plays the best pop songs, radio comics and live concerts around the clock.","enabled":true,"seoRelevantIn":["sv_SE","it_IT","pt_BR","es_CO","es_ES","en_US","fr_FR","nl_NL","da_DK","en_NZ","de_DE","de_AT","en_GB","es_MX","en_IE","en_CA","pt_PT","pl_PL"],"aliases":[],"blockingInformation":{"isBlocked":false,"isBlockedIn":[]}}]
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
    
    
    def _test_get_topics(self, data):
        api_result = self.radio.get_shortlist_topics()
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_menu(api_result, 'get_stations_by_topic')
        self._handle_result('menu_list', result)
    
    
    def _test_get_stations_by_topic(self, data):
        topic = 'news'
        api_result = self.radio.get_stations_by_topic(topic, count=20, offset=0)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        result = self._unify_stations(api_result)
        self._handle_result('stations_list', result)
    
    
    def _test_get_tags(self, data):
        api_result = self.radio.get_tags()
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        

    def _test_get_podcast_details(self, data):
        podcast_ids = 'zwei-seiten-der-podcast-uber-bucher'
        api_result = self.radio.get_podcast_details(podcast_ids)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
    
    def _test_get_podast_episodes(self, data):
        podcast_ids = 'zwei-seiten-der-podcast-uber-bucher'
        api_result = self.radio.get_podcast_episodes(podcast_ids, count=20, offset=0)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
    
    def _test_get_podcasts_by_author(self, data):
        author = 'Christine Westermann & Mona Ameziane, Podstars by OMR'
        api_result = self.radio.get_podcasts_by_author(author, count=20, offset=0)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
    
    def _test_get_podcasts_by_category(self, data):
        #category = 'arts'   # this is a main category
        category = 'books'  # this is a subcategory of "arts"
        api_result = self.radio.get_podcasts_by_category(category, count=20, offset=0)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
    
    def _test_get_podcast_categories(self, data):
        api_result = self.radio.get_podcast_categories()
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
        result = []
        for main_item in api_result['categories']:
            # add main category
            record = {'data': {}, 'mode': ''}
            record['data']['count'] = 20
            record['data']['offset'] = 0
            record['data']['name'] = main_item['name']
            record['data']['slug'] = main_item['slug']
            record['mode'] = 'get_podcasts_by_category'
            result.append(record)
            
            sub_category = main_item.get('subCategories', [])
            for item in sub_category:
                # add all sub-categories
                record = {'data': {}, 'mode': ''}
                record['data']['count'] = 20
                record['data']['offset'] = 0
                record['data']['name'] = item['name']
                record['data']['slug'] = item['slug']
                record['mode'] = 'get_podcasts_by_category'
                result.append(record)
                
        result = sorted(result, key=lambda k: k['data']['name'].lower())
        self._handle_result('menu_list', result)
        
    
    def _test_search_podcast(self, data):
        query = 'kalk und welk'
        api_result = self.radio.search_podcast(query, count=20, offset=0)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
    
    def _test_get_podcast_charts(self, data):
        api_result = self.radio.get_podcast_charts(count=20)
        xbmc.log(f'[{self.log_name}] result: {api_result}', xbmc.LOGDEBUG)
        
        
        
        
        
        
