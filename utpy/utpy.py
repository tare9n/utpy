import json
import re
import urllib3
from .exceptions import *
from .decipher import decipher
from pathlib import Path
import requests
from rich import print


class Load:
    def __init__(self, url):
        self.url = url

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
                'name': channel_name,
            }
            playlist_info = None
        elif self._url_analyze['playlist']['url']:
            playlist_html = response.data.decode('utf-8')
            data = re.findall('ytInitialData\s*=\s*({.+?})\s*;\s*(?:var\s+meta|<\/script|\n)', playlist_html)
            json_data = json.loads(data[0])
            data_of_videos = json_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
            videos = dict()
            for i in data_of_videos:
                index = i['playlistVideoRenderer']['index']['simpleText']
                video_id = i['playlistVideoRenderer']['videoId']
                video_url = 'https://www.youtube.com/watch?v=' + video_id
                videos.update({
                    f'{index}': {
                        'index': index,
                        'title': i['playlistVideoRenderer']['title']['runs'][0]['text'],
                        'id': video_id,
                        'url': video_url,
                    }
                })
            playlist_title = json_data['metadata']['playlistMetadataRenderer']['title']
            playlist_info = {
                'id': self._url_analyze['playlist']['id'], 
                'title': playlist_title,
                'url': self._url_analyze['playlist']['url'],
                'videos': videos,
            }
            video_info = None
            channel_info = None
        result = {
            'video': video_info,
            'playlist': playlist_info,
            'channel': channel_info,
        }
        return result

    @property
    def _select_quality(self):
        quality_list = list(self.data['video']['formats'].keys())
        quality_list.sort()
        selected = quality_list[-1]
        return selected

    @property
    def _get_dl_dir(self):
        path_to_utpy_dir = Path.home() / 'Downloads' / 'utpy'
        if not path_to_utpy_dir.is_dir():
            path_to_utpy_dir.mkdir()
        if self._url_analyze['playlist']['url']:
            pl_title = self.data['playlist']['title']
            pl_dir_name = re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', pl_title))
            dl_dir_path = path_to_utpy_dir / pl_dir_name
            if not dl_dir_path.is_dir():
                dl_dir_path.mkdir()
        else:
            dl_dir_path = path_to_utpy_dir
        return dl_dir_path

    def download(self, url= None, quality= None, save_to=None):
        if url:
            self.__init__(url)
        if not quality and self._url_analyze['video']['url']:
            quality = self._select_quality
        if not save_to:
            save_to = self._get_dl_dir
        if self._url_analyze['video']['url']:
            url = self.data['video']['formats'][quality]['url']
            video_title = self.data['video']['title'] + f' - {quality}'
            video_title =re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', video_title))
            file_name = video_title + '.utpy'
            file_name = re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', file_name))
            file_type = self.data['video']['formats'][quality]['type']
            file_full_name = video_title + file_type
            resume_hearder = ({'Range': f'bytes=0-'})
            file_path = Path(save_to / file_name)
            open_mode = 'wb'
            if len(file_name) > 30:
                show_name = file_name[:30] + '...'
            else:
                show_name = file_name
            if Path(save_to / file_full_name).exists():
                file_path = Path(save_to / file_full_name)
                downloaded_size = file_path.stat().st_size / (1024 * 1024)
                print(f'[green][+] %s completely downloaded. [%.2f Mb][/green]' %(show_name, downloaded_size)) 
            else:
                try:
                    path = Path(file_path)
                    resume_hearder = ({'Range': f'bytes={path.stat().st_size}-'})
                    open_mode = 'ab'
                except:
                    pass
                r = requests.get(url, stream=True, headers=resume_hearder)
                file_size = float(r.headers.get('content-length', 0)) / (1024 * 1024)
                with open(file_path, open_mode) as file:
                    for chunk in r.iter_content(32 * 1024):
                        file_size -= 0.03125
                        print(f'[yellow][-] Downloading %s [%.2f Mb][/yellow]    ' %(show_name, file_size), end='\r')
                        file.write(chunk)
                downloaded_size = file_path.stat().st_size / (1024 * 1024)
                print(f'[green][+] %s completely downloaded. [%.2f Mb][/green]' %(show_name, downloaded_size))
                file_path.rename(file_path.with_suffix(file_type))
        elif self._url_analyze['playlist']['url']:
            videos = self.data['playlist']['videos']
            dir_path = save_to
            print('[yellow][-] Downloading Playlist ... [/yellow]')
            for vid in videos:
                url = videos[vid]['url']
                self.download(url, save_to=dir_path)
            print('[green][+] Playlist Downloaded Successfully.[/green]')