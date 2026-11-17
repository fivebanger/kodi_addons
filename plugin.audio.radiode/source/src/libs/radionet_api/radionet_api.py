
import json

from logging import getLogger
from urllib.request import urlopen, Request
from urllib.parse import quote


REGIONS = {
    'at': 'de-AT',
    'au': 'en-AU',
    'br': 'pt-BR',
    'ca': 'en-CA',
    'co': 'es-CO',
    'de': 'de-DE',
    'dk': 'da-DK',
    'es': 'es-ES',
    'fr': 'fr-FR',
    'ie': 'en-IE',
    'it': 'it-IT',
    'mx': 'es-MX',
    'nl': 'nl-NL',
    'nz': 'en-NZ',
    'pl': 'pl-PL',
    'pt': 'pt-PT',
    'se': 'sv-SE',
    'uk': 'en-GB',
    'us': 'en-US',
    'za': 'en-ZA',
}


class RadionetApi():
    
    def __init__(self, language='de'):
        self.language = REGIONS[language]
        self.user_agent = 'Radio.net - Web V5'
        self.base_url = 'https://prod.radio-api.net'
        self.logger = getLogger('radio_api')
    
    
    def set_logger(self, logger):
        self.logger = logger
    
    
    def search(self, query, count=20, offset=0):
        query = quote(query)
        url = self.base_url + f'/stations/search?query={query}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_similar(self, station, count=20):
        url = self.base_url + f'/stations/{station}/similar?count={count}' 
        return self._open_url(url)
    
    
    def get_family(self, station, count=20, offset=0):
        url = self.base_url + f'/stations/{station}/family?count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_local_stations(self, count=20, offset=0):
        url = self.base_url + f'/stations/local?count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_tags(self):
        url = self.base_url + f'/stations/tags'
        return self._open_url(url)
    
    
    def get_languages(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'languages', min_count_stations)
    
    
    def get_topics(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'topics', min_count_stations)
    
    
    def get_genres(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'genres', min_count_stations)
    
    
    def get_countries(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'countries', min_count_stations)
    
    
    def get_cities(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'cities', min_count_stations)
    
    
    def get_families(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'families', min_count_stations)
    
    
    def get_parents(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'parents', min_count_stations)
    
    
    def get_regions(self, min_count_stations=0):
        url = self.base_url + f'/stations/tags'
        api_result = self._open_url(url)
        return self._filter_result(api_result, 'regions', min_count_stations)
    
    
    def get_stations_by_language(self, language, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=languages&slug={language}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_topic(self, topic, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=topics&slug={topic}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_genre(self, genre, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=genres&slug={genre}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_country(self, country, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=countries&slug={country}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_city(self, city, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=cities&slug={city}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_family(self, family, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=families&slug={family}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_parents(self, parents, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=parents&slug={parents}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_stations_by_region(self, region, count=20, offset=0):
        url = self.base_url + f'/stations/by-tag?tagType=regions&slug={region}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_shortlist_genres(self):
        url = self.base_url + f'/stations/shortlist?tagType=genre'
        return self._open_url(url)
    
    
    def get_shortlist_topics(self):
        url = self.base_url + f'/stations/shortlist?tagType=topic'
        return self._open_url(url)
    
    
    def get_shortlist_cities(self):
        url = self.base_url + f'/stations/shortlist?tagType=city'
        return self._open_url(url)
    
    
    def get_shortlist_countries(self):
        url = self.base_url + f'/stations/shortlist?tagType=country'
        return self._open_url(url)
    
    
    def get_stations_by_char(self, char, count=20, offset=0):
        url = self.base_url + f'/stations/all?character={char}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_now_playing(self, station):
        url = self.base_url + f'/stations/now-playing?stationIds={station}'
        return self._open_url(url)
    
    
    def get_songs(self, station):
        url = self.base_url + f'/stations/{station}/songs'
        return self._open_url(url)
    
    
    def get_station_details(self, station):
        url = self.base_url + f'/stations/details?stationIds={station}'
        result = self._open_url(url)
        if result:
            return result[0]
        return []
    
    
    def get_stations_details(self, stations):
        return self.base_url + f'/stations/details?stationIds={stations}'
    
    '''
    def get_stations_by_city(self, city, count=20, offset=0):
        url = self.base_url + f'/stations/cities/{city}/frequencies'
        return self._open_url(url)
    '''
    

    def get_podcast_details(self, podcast_ids):
        url = self.base_url + f'/podcasts/details?podcastIds={podcast_ids}'
        return self._open_url(url)


    def get_podcast_episodes(self, podcast_ids, count, offset):
        url = self.base_url + f'/podcasts/episodes/by-podcast-ids?podcastIds={podcast_ids}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_podcasts_by_author(self, author, count, offset):
        author = quote(author)
        url = self.base_url + f'/podcasts/by-author/{author}?count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_podcasts_by_system_name(self, system_name, count, offset):
        url = self.base_url + f'/podcasts/list-by-system-name?systemName={system_name}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_podcasts_by_category(self, category, count, offset):
        url = self.base_url + f'/podcasts/category/{category}/charts?count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_podcast_categories(self):
        url = self.base_url + f'/podcasts/category-list/charts'
        return self._open_url(url)
    
    
    def search_podcast(self, query, count, offset):
        query = quote(query)
        url = self.base_url + f'/podcasts/search?query={query}&count={count}&offset={offset}'
        return self._open_url(url)
    
    
    def get_podcast_charts(self, count):
        url = self.base_url + f'/podcasts/category/podcasts/charts?count={count}'
        return self._open_url(url)


    def resolve_url(self, url):
        resolve = True
        
        while resolve:
            resolve = False
            try:
                req = Request(url)
                req.add_header('accept-language', self.language)
                req.add_header('user-agent', self.user_agent)
                response = urlopen(req)
                new_url = response.geturl()
    
                if '.m3u' in new_url:
                    # m3u or m3u8 playlist
                    req = Request(new_url)
                    req.add_header('accept-language', self.language)
                    req.add_header('user-agent', self.user_agent)
                    response = urlopen(req, timeout=2).read()
                    response = response.decode()
                    
                    if 'http' in response:
                        # try to get a http url from playlist
                        response = response.split('\n')
                        new_url = None
                        
                        for item in response:
                            if item.startswith('http'):
                                url = item
                                resolve = True
                                break
                    else:
                        # no http url found in playlist, return playlist url itself 
                        new_url = url
                        break

            except Exception as err:
                if ('certificate' in str(err).lower()) and url.startswith('https'):
                    # fallback, try to resolve url using http instead of https
                    self.logger.error(f'resolve_url certificate error, fallback to http, url: {url}, error: {err}')
                    url = url.replace('https', 'http', 1)
                    resolve = True
                else:
                    self.logger.error(f'resolve_url error, url: {url}, error: {err}')
                    new_url = None
        
        return new_url


    def _open_url(self, url):
        result = []
        self.logger.debug(f'_open_url: {url}')
        # self.logger.error(f'_open_url: {url}')
        try:
            req = Request(url)
            req.add_header('accept-language', self.language)
            req.add_header('user-agent', self.user_agent)
            response = urlopen(req).read()
        except Exception as err:
            self.logger.error(f'_open_url error: {err}')
            response = b''
            
        try:
            result = json.loads(response)
        except Exception as err:
            self.logger.error(f'_open_url error: {err}')
            
        return result
    
    
    def _filter_result(self, data, tag, min_count_stations):
        api_result = data.get(tag, [])
        
        if api_result and min_count_stations:
            # filter result by minimum count of stations
            result = []
            
            for item in api_result:
                if item['count'] >= min_count_stations:
                    result.append(item)
            
            return result
        
        return api_result



