
import xbmcvfs
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import json
import inspect
import os
import sys

try:
    # Python 3
    from urllib.parse import urlencode, parse_qsl
except ImportError:
    # Python 2
    from urllib import urlencode
    from urlparse import parse_qsl
 
    

log_level = xbmc.LOGDEBUG


# icon: https://kodi.wiki/view/Default_Icons
# content: https://alwinesch.github.io/group__python__xbmcplugin.html#gaa30572d1e5d9d589e1cd3bfc1e2318d6
item_types = {'folder': {'icon': 'DefaultFolder.png', 'content': 'files',   'info_type': ''},
              'artist': {'icon': 'DefaultArtist.png', 'content': 'artists', 'info_type': ''},
              'music':  {'icon': 'DefaultFolder.png', 'content': 'songs',   'info_type': 'music'},
              'video':  {'icon': 'DefaultVideo.png',  'content': 'videos',  'info_type': 'video'}}


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
LOG_TAG = ADDON_NAME.replace(' ', '_')





def sys_path_insert(path):
    addon_path = ADDON.getAddonInfo('path')
    
    path = path.split('/')
    for item in path:
        if '' != item:
            addon_path = os.path.join(addon_path, item)
    
    sys.path.insert(0, addon_path)

    
def get_text_from_keyboard(heading="", text="", hidden=False):
    string = ""
    keyboard = xbmc.Keyboard(text, heading)
    keyboard.setHiddenInput(hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        string = keyboard.getText()
    if "" == string:
        exit(0)
    return string


class AddonLogger():
    
    def __init__(self, tag, level=xbmc.LOGINFO):
        self.tag = tag
        self.loglevel = level
    
    
    def debug(self, text):
        # xbmc.LOGDEBUG = 0
        self._log(text, xbmc.LOGDEBUG)
    
    
    def info(self, text):
        # xbmc.LOGINFO = 1
        self._log(text, xbmc.LOGINFO)
    
    
    def warning(self, text):
        # xbmc.LOGWARNING = 3
        self._log(text, xbmc.LOGWARNING)
    
    
    def error(self, text):
        # xbmc.LOGERROR = 4
        self._log(text, xbmc.LOGERROR)


    def _log(self, text, level):
        if self.loglevel <= level:
            xbmc.log(u'{}: {}'.format(self.tag, text), level)


class Dispatcher():
    
    def __init__(self, sys_args, appl):        
        self.addon_path = sys_args[0]
        self.addon_handle = int(sys_args[1])
        addon_args = parse_qsl(sys_args[2][1:])
        self.addon_args = dict(addon_args)
        self.appl = appl
        
    
    def get_addon_path(self):
        return self.addon_path
        
    
    def get_addon_handle(self):
        return self.addon_handle
        
    
    def get_addon_args(self):
        return self.addon_args

        
    def route(self):
        xbmc.log('[{}]: Dispatcher AddOn args: {}'.format(LOG_TAG, self.addon_args), log_level)
        handle_err = True
        
        if {} == self.addon_args:
            mode = 'root'
            data = {}
        else:
            mode = self.addon_args['mode']
            data = self.addon_args['data']
            data = json.loads(data)
        
        result = inspect.getmembers(self.appl, predicate=inspect.ismethod)
        
        for item in result:
            name = item[0]
            funtion = item[1]
            
            if name == mode:
                self.appl.set_addon_data(self.addon_path, self.addon_handle)
                funtion(data)
                handle_err = False
                break
        
        if handle_err:
            xbmc.log('[{}]: Dispatcher mode error: {}'.format(LOG_TAG, mode), xbmc.LOGERROR)
            

class ListItem():

    def __init__(self, addon_path, addon_handle, default_icon='', default_fanart=''):
        self.addon_handle = addon_handle
        self.addon_path = addon_path
        self.cm_items = []
        self.default_icon = default_icon
        self.default_fanart = default_fanart
        self.li = None


    def add_item(self, name, mode, data, icon='', fanart='', item_type=''):
        if '' == item_type:
            item_type = 'folder'
        
        self.li = xbmcgui.ListItem(name)        
        self._add(mode, data, item_type, icon, fanart, True)
    
    
    def add_music_item(self, name, mode, data, icon='', fanart='', duration=0):
        item_type = 'music'
        
        self.li = xbmcgui.ListItem(name)
        try:
            # Kodi >= v20.x
            info_tag = self.li.getMusicInfoTag()
            info_tag.setDuration(duration or 0)
        except:
            # Kodi <= 19.x
            info_labels = {'duration': duration, "title": name}
            self.li.setInfo(item_type, info_labels)
        #hmk TODO: check self.li.setProperty('IsPlayable', 'true')
        self.li.setProperty('IsPlayable', 'true')
        self._add(mode, data, item_type, icon, fanart, False)


    def add_video_item(self, name, mode, data, icon='', fanart='', duration=0, plot=''):
        item_type = 'video'
        
        self.li = xbmcgui.ListItem(name)
        try:
            # Kodi >= v20.x
            info_tag = self.li.getVideoInfoTag()
            info_tag.setDuration(duration or 0)
            info_tag.setPlot(plot)
        except:
            # Kodi <= 19.x
            info_labels = {'duration': duration, "plot": plot}
            self.li.setInfo(item_type, info_labels)
        #hmk TODO: check self.li.setProperty('IsPlayable', 'true')
        self.li.setProperty('IsPlayable', 'true')
        self._add(mode, data, item_type, icon, fanart, False)


    def end_of_directory(self, update_listing=False):
        xbmcplugin.endOfDirectory(self.addon_handle, updateListing=update_listing)
        
        
    def add_context_menu_item(self, name, mode, data, action="RunPlugin"):
        '''
            action: see https://alwinesch.github.io/page__list_of_built_in_functions.html
                    Container.Refresh
                    RunPlugin
        '''
        path = self._build_path(mode, data)
        self.cm_items.append((name, '{}({})'.format(action, path)))
    
    
    def clear_context_menu(self):
        self.cm_items = []
        
        
    def _add(self, mode, data, item_type, icon, fanart, is_folder):
        path = self._build_path(mode, data)
        content = self._get_content(item_type)

        icon = self._get_icon(icon, item_type)
        fanart = self._get_fanart(fanart)
        
        self.li.setArt({'thumb': icon, 'icon': icon, 'fanart': fanart})
        self.li.addContextMenuItems(self.cm_items)
        
        xbmcplugin.addDirectoryItem(self.addon_handle, path, self.li, is_folder)
        xbmcplugin.setContent(self.addon_handle, content)
        
        self.cm_items = []
    
    
    def _build_path(self, mode, data):
        data = json.dumps(data)
        query = {'mode': mode, 'data': data}
        encoded = urlencode(query)
        return '{}?{}'.format(self.addon_path, encoded)
    
    
    def _get_icon(self, icon, item_type):
        if '' == icon:
            if item_types.get(item_type):
                return item_types[item_type]['icon']
        elif 'default' == icon:
            icon = self.default_icon
        return icon
    
    
    def _get_fanart(self, fanart):
        if 'default' == fanart:
            fanart = self.default_fanart
        return fanart
    
    
    def _get_content(self, item_type):
        if item_types.get(item_type):
            return item_types[item_type]['content']
        return ''
    
    
class DataHandler():
    
    def __init__(self):
        self.paths = {}
    
    
    def register_path(self, item_name, path='', use_custom_folder_tag='', custom_folder_tag=''):
        result = False
        data_dir = self._check_path(path, use_custom_folder_tag, custom_folder_tag)
        
        if data_dir:
            new_path = {item_name: data_dir}
            self.paths.update(new_path)
            result = True

        return result
    
        
    def load_list(self, list_name, defaultList=[]):
        result = defaultList
        file_name = list_name + '.jsn'
        
        self._check_list_path(list_name, file_name)
        data = self.load_file(file_name)
        
        if data:
            try:
                result = json.loads(data)
            except:
                xbmc.log( ('[{}]: Error loading list {}'.format(LOG_TAG, file_name)), xbmc.LOGERROR)
        else:
            xbmc.log( ('[{}]: Cannot load list {}'.format(LOG_TAG, file_name)), xbmc.LOGERROR)
            self.save_list(list_name, defaultList, False)
        
        return result
    
    
    def save_list(self, list_name, list_data, list_backup=False):
        file_name_bak = list_name + '_bak.jsn'
        file_name = list_name + '.jsn'
        
        self._check_list_path(list_name, file_name_bak)
        self._check_list_path(list_name, file_name)
        
        if list_backup:
            result = self.load_file(file_name)
            if result:
                try:
                    # try to load json data
                    tmp = json.loads(result)
                    result = json.dumps(tmp)
                    # save old list data to backup file
                    self.save_file(file_name_bak, result)
                except:
                    xbmc.log( ('[{}]: Error loading list {}'.format(LOG_TAG, file_name)), xbmc.LOGERROR)
        
        list_data = json.dumps(list_data)
        self.save_file(file_name, list_data)
            
    
    def load_file(self, file_name):
        result = None
        
        self._check_file_path(file_name)
        filePath = self._get_path(file_name)
        file = filePath + file_name

        if xbmcvfs.exists(file):
            fh = xbmcvfs.File(file, 'r')
            result = fh.read()
            fh.close()
        else:
            xbmc.log( ('[{}]: Cannot load file {}'.format(LOG_TAG, file)), xbmc.LOGERROR)
        
        return result
            

    def save_file(self, file_name, data):
        result = False
        
        self._check_file_path(file_name)
        filePath = self._get_path(file_name)
        file = filePath + file_name
        
        try:
            fh = xbmcvfs.File(file, 'w')
            fh.write(data)
            fh.close()
            result = True
        except:
            xbmc.log( ('[{}]: Cannot save {}'.format(LOG_TAG, file)), xbmc.LOGERROR)
            
        return result
            

    def delete_file(self, file_name, path='data'):
        pass
            

    def rename_file(self, old_filename, new_filename, backup=True, path='data'):
        pass
    
    
    def _get_path(self, item_name):
        if self.paths.get(item_name):
            return self.paths[item_name]

    
    def _check_list_path(self, list_name, file_name):
        if not self._get_path(list_name):
            self.register_path(list_name, '', '', '')
            
        if not self._get_path(file_name):
            # register a path for the list's filename
            list_path = self._get_path(list_name)
            new_path = {file_name: list_path}
            self.paths.update(new_path)
    
    
    def _check_file_path(self, file_name):
        if not self._get_path(file_name):
            self.register_path(file_name, '', '', '')
           
    
    def _check_path(self, path, use_custom_folder_tag, custom_folder_tag):
        data_dir = 'special://profile/addon_data/' + ADDON_ID + '/'
            
        if '' != use_custom_folder_tag:
            use_xchange_folder = ADDON.getSetting(use_custom_folder_tag)
            
            if 'true' == use_xchange_folder:
                if '' != data_dir:
                    data_dir = ADDON.getSetting(custom_folder_tag)
                else:
                    data_dir = None

        if data_dir:
            path = path.split('/')
            for item in path:
                if '' != item:
                    data_dir = data_dir + item + '/'
            
            if not xbmcvfs.exists(data_dir):
                if not xbmcvfs.exists(data_dir):
                    xbmc.log('[{}]: Create data folder {}'.format(LOG_TAG, data_dir), log_level)
                    res = xbmcvfs.mkdir(data_dir)
                    
                    if False == res:
                        data_dir = None
        
        return data_dir
    
     
            