# Radio.de
Add-on to access broadcast streams and podcasts provided by Radio.de and Radio.net.

## Custom stations:
Custom station links can be provided in two ways:
### Edit "stations.jsn":
Open the "stations.jsn" file (default location: userdata/addon_data/plugin.audio.radiode/.radiode) and add a new data set, leaving key "id" blank.

Example:
```
{"data": {"id": "", "name": "my custom station", "icon_url": "http://my_custom_station.url/icon.jpg", "stream_url": "http://my_custom_station.url/stream.mp3"}, "mode": "play_stream"}
```
### Import a m3u file:
Open add-on settings, "Data", "Import stations from m3u file" and follow the instructions.

Example for a valid .m3u file:
```
#EXTM3U
#EXTINF:-1 tvg-logo="http://my_custom_station.url/icon.jpg",my custom station
http://my_custom_station.url/stream.mp3
```
## Exporting stations to IPTV file:
Stations can be added to an already existing IPTV list or to a new IPTV list. Exporting a station to a IPTV file (m3u-format) adds lines using the following scheme:
```
#EXTINF:-1 tvg-name="station name" group-title="Radio-DE" radio="true" tvg-logo="http://station.url/icon.jpg",station name
http://station.url/stream.mp3
```

The scheme fits to IPTV lists provided by https://github.com/jnk22/kodinerds-iptv/tree/master/iptv/kodi which can be used by Kodi's "IPTV Simple Client".

## Calling a station via JSON-rpc:
For convenience, it's possible to call a station from JSON-rpc by just providing the station ID (version >= v1.1.2) without any additional parameters like "name", "icon_url" or "stream_url". A html-quoted string to call the add-on can easily be build like this, using function "play_station":
```
station_id = 'swr3'
addon_call = f'plugin://plugin.audio.radiode/?mode=play_station&data=%7B%22id%22%3A+%22{station_id}%22%7D'
```
The corresponding JSON-rpc call is:
```
{"jsonrpc":"2.0","method":"Player.Open","params": {"item": {"file": addon_call}}, "id": 1}
```

Pls. refer to the "stations.jsn" for a valid station_id or play the station in a browser and check the address bar, where the last parameter represents the station_id, e.g. "https://www.radio.de/s/swr3".
