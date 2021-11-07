import json
import re
import urllib3
from .exceptions import *
from .decipher import decipher
from .dicts import default_settings
from pathlib import Path


class Load:
    def __init__(self, url: str, settings: dict = default_settings):
        self.url = url
        try:
            self.save_to = settings['save_to']
        except:
            self.save_to = None
        try:
            self.file_name = settings['file_name']
        except:
            self.file_name = None
        try:
            self.quality = settings['quality']
        except:
            self.quality = None
        try:
            self.index = settings['index']
        except:
            self.index = None
        try:
            self.dl_range = settings['dl_range']
        except:
            self.dl_range = ()
        try:
            self.dl_list = settings['dl_list']
        except:
            self.dl_list = []
        try:
            self.retries = settings['retries']
        except:
            self.retries = 2

    @property
    def _url_analyze(self):
        url = self.url
        if 'youtube.com/' in url or 'youtu.be/' in url:
            is_video_url = re.findall(
                '/watch\?v=(.{11})($|&| )', url) or re.findall('youtu\.be/(.{11})', url)
            find_plylist_id = re.findall('list=(.{34})', url)
            find_video_index = re.findall('index=(\d*)', url)
            is_playlist_url = re.findall('/playlist\?list=(.{34})', url)
            if is_video_url:
                if find_plylist_id:
                    playlist_id = find_plylist_id[0]
                    playlist_url = 'https://www.youtube.com/playlist?list=' + playlist_id
                else:
                    playlist_url = None
                    playlist_id = None
                if find_video_index:
                    video_index = int(find_video_index[0])
                else:
                    video_index = None
                video_id = is_video_url[0][0]
                video_url = 'https://www.youtube.com/watch?v=' + video_id
            elif is_playlist_url:
                video_url = None
                video_id = None
                video_index = None
                playlist_id = is_playlist_url[0]
                playlist_url = 'https://www.youtube.com/playlist?list=' + playlist_id
            else:
                raise InvalidUrlException()
        else:
            raise InvalidUrlException()

        video_url_analyze = {
            'index': video_index,
            'id': video_id,
            'url': video_url,
        }
        playlist_url_analyze = {
            'id': playlist_id,
            'url': playlist_url,
        }
        result = {
            'video': video_url_analyze,
            'playlist': playlist_url_analyze,
        }
        return result

    @property
    def data(self):
        http = urllib3.PoolManager()
        url = self._url_analyze['video']['url'] or self._url_analyze['playlist']['url']
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.76 Safari/537.36",
            "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,ar;q=0.6"
            }
        response = http.request('GET', url, headers=headers)
        if self._url_analyze['video']['url']:
            video_html = response.data.decode('utf-8')
            data = re.findall(
                'ytInitialPlayerResponse\s*=\s*({.+?})\s*;\s*(?:var\s+meta|<\/script|\n)', video_html)
            json_data = json.loads(data[0])
            video_title = json_data['videoDetails']['title']
            video_time = json_data['videoDetails']['lengthSeconds']
            video_description = json_data['videoDetails']['shortDescription']
            formats_data = json_data['streamingData']['formats']
            formats = dict()
            for f in formats_data:
                quality = f['qualityLabel']
                format_type = f['mimeType'].split(';')[0].split('/')[-1]
                try:
                    url = f['url']
                except:
                    signature = f['signatureCipher']
                    base_js = re.search(r'\"jsUrl\":\"(.*?base\.js)\"', video_html).groups()[0]
                    base_js = 'https://www.youtube.com/' + base_js
                    url = decipher(signature, base_js)
                formats.update(
                    {f'{quality}': {
                        'type': '.' + format_type,
                        'url': url,
                    }}
                )
            video_info = {
                'title': video_title,
                'id': self._url_analyze['video']['id'],
                'url': self._url_analyze['video']['url'],
                'time': video_time,
                'description': video_description,
                'formats': formats,
            }

            channel_id = json_data['videoDetails']['channelId']
            channel_name = json_data['videoDetails']['author']
            channel_info = {
                'id': channel_id,
                'url': 'https://www.youtube.com/channel/' + channel_id,
                'name': channel_name,
            }
            playlist_info = None
        elif self._url_analyze['playlist']['url']:
            playlist_html = response.data.decode('utf-8')
            data = re.findall(r'(\[{\"playlistVideoRenderer\":.*}]}}}]}}])', playlist_html)
            json_data = json.loads(data[0])
            videos = dict()
            for i in json_data:
                title = i['playlistVideoRenderer']['title']['runs'][0]['text']
                video_id = i['playlistVideoRenderer']['videoId']
                index = i['playlistVideoRenderer']['index']['simpleText']
                video_url = 'https://www.youtube.com/watch?v=' + video_id
                length_text = i['playlistVideoRenderer']['lengthText']['simpleText']
                length = int(i['playlistVideoRenderer']['lengthSeconds'])
                videos.update({
                    f'{index}': {
                        'index': index,
                        'title': title,
                        'id': video_id,
                        'url': video_url,
                        'length': length,
                        'length_text': length_text,
                    }
                })
            playlist_title = re.findall(r'playlistMetadataRenderer\":{\"title\":\"(.*?)\",', playlist_html)[0]
            playlist_info = {
                'videos_count': len(json_data),
                'id': self._url_analyze['playlist']['id'], 
                'title': playlist_title,
                'url': self._url_analyze['playlist']['url'],
                'videos': videos,
            }
            video_info = None
            select_a_video =json_data[0]
            channel_id = re.findall(r"'browseId': *'(.{24})'", str(select_a_video))[0]
            channel_name = select_a_video['playlistVideoRenderer']['shortBylineText']['runs'][0]['text']
            channel_info = {
                'id': channel_id,
                'url': 'https://www.youtube.com/channel/' + channel_id,
                'name': channel_name,
            }
        result = {
            'video': video_info,
            'playlist': playlist_info,
            'channel': channel_info,
        }
        return result

    @property
    def available_qualities(self):
        available_qualities = list(self.data['video']['formats'].keys())
        return available_qualities

    @property
    def _select_quality(self):
        quality_list = self.available_qualities
        quality_list.sort()
        selected = quality_list[-1]
        return selected

    @property
    def get_dl_dir_path(self):
        if self.save_to:
            dl_dir_path = Path(self.save_to)
        else:
            dl_dir_path = Path.home() / 'Downloads' / 'utpy'
            if self._url_analyze['playlist']['url'] and self.data['playlist']:
                pl_title = self.data['playlist']['title']
                pl_dir_name = re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', pl_title))
                dl_dir_path = dl_dir_path / pl_dir_name
        if not dl_dir_path.is_dir():
            dl_dir_path.mkdir()
        return dl_dir_path

    def _downloader(self, url, save_to, file_name):
        file_type = '.' + file_name.split('.')[-1]
        utpy_file_name = re.sub(file_type, '.utpy', file_name)
        utpy_file_path = Path(save_to / utpy_file_name)
        try:
            downloaded = utpy_file_path.stat().st_size
            resume_headers = ({'Range': f'bytes={downloaded}-'})
            open_mode = 'ab'
        except:
            downloaded = 0
            resume_headers = ({'Range': f'bytes=0-'})
            open_mode = 'wb'
            pass
        if len(file_name) > 30:
            show_name = file_name[:27] + '...'
        else:
            show_name = file_name
        http = urllib3.PoolManager()
        resp = http.request('GET', url, preload_content=False, headers=resume_headers)
        file_size = int(resp.headers['Content-Length']) + downloaded
        for t in range(self.retries + 1):
            if t == self.retries:
                print(f'Content Of Video Not found. Check internet connection and try again later.')
            if file_size > downloaded:
                with open(utpy_file_path, open_mode) as file:
                    while True:
                        chunk = resp.read(32 * 1024)
                        if chunk: 
                            file.write(chunk)
                            downloaded += len(chunk)
                            percent = (downloaded / int(file_size)) * 100
                            print('[-] Downloading: %s [%.2f %s / %.2f Mb]     '
                                    % (show_name, percent, '%', (file_size / (1024*1024))), end='\r')
                        else: 
                            break
                resp.release_conn()
                downloaded_mb = file_size  / (1024 * 1024)
                print(f'[+] %s [%.2f Mb] downloaded successfully.    ' 
                        %(show_name, downloaded_mb))
                utpy_file_path.rename(utpy_file_path.with_suffix(file_type))
                try:
                    if is_playlist:
                        print(f'[-] Preparing Next Download.', end='\r')
                except NameError: 
                    print(f'    -> Saved in: %s' % save_to)
                break
            else:
                print(f'Content Not Received. Trying again ... ({t + 1})', end='\r')
                url= self.url
                settings = {
                    'save_to' : save_to,
                    'file_name': file_name,
                    'quality' : self.quality,
                    'index' : self.index,}
                self.__init__(url, settings=settings)
                self.download
    
    @property
    def download(self):
        global is_playlist
        quality = self.quality
        save_to = self.get_dl_dir_path
        if not quality and self._url_analyze['video']['url']:
            quality = self._select_quality
        if self._url_analyze['video']['url']:
            url = self.data['video']['formats'][quality]['url']
            video_title = self.data['video']['title']
            if self.index:
                video_title = f'{self.index}- ' + video_title
            video_title =re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', video_title)).strip()
            file_type = self.data['video']['formats'][quality]['type']
            file_name = self.file_name
            if file_name:
                if not file_name.endswith(file_type):
                    file_name = file_name + file_type
            else:
                file_name = video_title + file_type
            if Path(save_to / file_name).exists():
                print(f'[+] This file exists in: %s ' %(save_to)) 
            else:
                self._downloader(url, save_to, file_name)

        elif self._url_analyze['playlist']['url']:
            is_playlist = True
            videos = self.data['playlist']['videos']
            downloaded_files = [str(x).split('\\')[-1] for x in Path(save_to).glob('*.mp4')]
            print(f'[-] Downloading Playlist ...  \n    -> Save path: %s' % save_to)
            for vid in videos:
                vid_title = videos[vid]['title']
                vid_title = re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', vid_title)).strip()
                file_name = f'{vid}- ' + vid_title + '.mp4'
                if file_name in downloaded_files:
                    print(f'[+] {file_name[:27]}... Downloaded Before.')
                else:
                    print(f'[-] Preparing Download: {file_name[:27]}...', end='\r')
                    url = videos[vid]['url']
                    settings = {
                        'save_to' : save_to,
                        'file_name': file_name,
                        'quality' : quality,
                        'index' : vid,}
                    self.__init__(url, settings=settings)
                    self.download
            print('[+] Playlist Downloaded Successfully.')