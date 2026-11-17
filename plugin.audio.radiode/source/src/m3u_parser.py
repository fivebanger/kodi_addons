
import re



class M3UParser():
    
    def __init__(self):
        pass
    
    def parse_file(self, filename):
        fh = open(filename, 'r')
        data = fh.read()
        fh.close()
        return self.parse_data(data)
        
        
    def parse_data(self, data):
        data = data.splitlines()
        next_line_url = False
        result = []
        
        for line in data:
            if line.startswith('#EXTINF:'):
                record = {}
                record['name'] = self._get_name(line)
                record['icon_url'] = self._get_image(line)
                record['is_radio'] = self._is_radio(line)
                next_line_url = True
            elif next_line_url:
                next_line_url = False
                if line.startswith('http'):
                    record['stream_url'] = line
                    result.append(record)
                
        return result
                
                
    def _get_name(self, line):
        name = ''
        lsplit = line.split(',')
        if 2 <= len(lsplit):
            name = lsplit[1]
        return name
                
                
    def _get_image(self, line):
        icon_url = re.findall('"(?<=tvg-logo\=\")(.*?)(?=\")"', line.lower())
        icon_url = icon_url[0] if icon_url else ''
        return icon_url
    
    
    def _is_radio(self, line):
        tvg_radio = re.findall('"(?<=tvg-radio\=\")(.*?)(?=\")"', line.lower())
        radio = re.findall('"(?<=radio\=\")(.*?)(?=\")"', line.lower())
        tvg_radio = tvg_radio[0] if tvg_radio else None
        radio = radio[0] if radio else None
        
        if tvg_radio or radio:
            if ("false" == tvg_radio) or ("false" == radio):
                return False
            elif ("true" == tvg_radio) or ("true" == radio):
                return True

        return None

