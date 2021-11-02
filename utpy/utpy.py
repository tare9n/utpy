import json
import re
import urllib3
from .exceptions import *
from .decipher import decipher
from pathlib import Path

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
        if self._url_analyze['playlist']['url'] and self.data['playlist']:
            pl_title = self.data['playlist']['title']
            pl_dir_name = re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', pl_title))
            dl_dir_path = path_to_utpy_dir / pl_dir_name
            if not dl_dir_path.is_dir():
                dl_dir_path.mkdir()
        else:
            dl_dir_path = path_to_utpy_dir
        return dl_dir_path

    def _make_file(self, utpy_file_path, open_mode, resp, downloaded, file_size, show_name, file_type, save_to):
        utpy_file_path = utpy_file_path
        open_mode = open_mode
        resp = resp
        downloaded = downloaded
        file_size = file_size
        show_name = show_name
        file_type = file_type
        save_to = save_to
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
        print(f'[+] %s downloaded. [%.2f Mb] \n    -> Saved in: %s' %(show_name, downloaded_mb, save_to))
        utpy_file_path.rename(utpy_file_path.with_suffix(file_type))

    def _downloader(self, url, save_to, file_name, retries):
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
        for i in range(retries + 1):
            if i == retries:
                raise FailedToGetContent()
            if file_size > downloaded:
                self._make_file(utpy_file_path, open_mode, resp, downloaded, file_size, show_name, file_type, save_to)
                break
            else:
                print(f'Content Not found. Trying again ... ({i})')
                resp = http.request('GET', url, preload_content=False, headers=resume_headers)
                file_size = int(resp.headers['Content-Length']) + downloaded


    def download(self, url= None, quality= None, save_to=None, index=None, retries=2):
        if url:
            self.__init__(url)
        if not quality and self._url_analyze['video']['url']:
            quality = self._select_quality
        if not save_to:
            save_to = self._get_dl_dir
        if self._url_analyze['video']['url']:
            url = self.data['video']['formats'][quality]['url']
            video_title = self.data['video']['title']
            if index:
                video_title = f'{index}- ' + video_title
            video_title =re.sub('\s+', ' ', re.sub('[\\\<>\[\]:"/\|?*]', '-', video_title)).strip()
            file_type = self.data['video']['formats'][quality]['type']
            file_name = video_title + file_type
            if Path(save_to / file_name).exists():
                print(f'[+] This one exists in: %s ' %(save_to)) 
            else:
                self._downloader(url, save_to, file_name, retries)

        elif self._url_analyze['playlist']['url']:
            videos = self.data['playlist']['videos']
            dir_path = save_to
            print('[-] Downloading Playlist ... ')
            for vid in videos:
                url = videos[vid]['url']
                self.download(url, index=vid ,save_to=dir_path)
            print('[+] Playlist Downloaded Successfully.')