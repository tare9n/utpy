import re

def url_analyze(url):
    if 'youtube.com/' in url or 'youtu.be/' in url:
        is_video_url = re.findall('/watch\?v=(.{11})', url) or re.findall('youtu\.be/(.{11})', url)
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
            video_id = is_video_url[0]
            video_url = 'https://www.youtube.com/watch?v=' + video_id
        elif is_playlist_url:
            video_url = None
            video_id = None
            video_index = None
            playlist_id = is_playlist_url[0]
            playlist_url = 'https://www.youtube.com/playlist?list=' + playlist_id
        else:
            print('Maby your link is invalid.')
    else:
        print('Invalid Youtube Link.')

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