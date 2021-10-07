import json
import re
import urllib3
from exceptions import *

class Load:
    def __init__(self, url):
        self.url = url

    @property
    def url_analyze(self):
        url = self.url
        if 'youtube.com/' in url or 'youtu.be/' in url:
            is_video_url = re.findall('/watch\?v=(.{11})($|&| )', url) or re.findall('youtu\.be/(.{11})', url)
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
        url = self.url_analyze['video']['url'] or self.url_analyze['playlist']['url']
        response = http.request('GET', url)
        if self.url_analyze['video']['url']:
            video_html = response.data.decode('utf-8')
            data = re.findall('ytInitialPlayerResponse\s*=\s*({.+?})\s*;\s*(?:var\s+meta|<\/script|\n)', video_html)
            json_data = json.loads(data[0])
            video_title = json_data['videoDetails']['title']
            video_time = json_data['videoDetails']['lengthSeconds']
            video_description = json_data['videoDetails']['shortDescription']
            formats_data = json_data['streamingData']['formats']
            formats = dict()
            for f in formats_data:
                quality = f['qualityLabel']
                format_type = f['mimeType'].split(';')[0].split('/')[-1]
                formats.update(
                    {f'{quality}': {
                        'type': '.' + format_type,
                        'url': f['url']  
                    }}
                )
            video_info = {
                'title': video_title,
                'id': self.url_analyze['video']['id'],
                'url': self.url_analyze['video']['url'],
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
        elif self.url_analyze['playlist']['url']:
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
            playlist_title = json_data['j']
            playlist_info = {
                'title': playlist_title,
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

    def download(self):
        pass
