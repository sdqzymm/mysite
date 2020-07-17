import requests
import datetime
from ..settings import VIDEO_COLLECT_SIZE

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }


def collect_video():
    url = f'https://www.dance365.com/apis/moment/moments/cursor/rec/default?access_token=c494ae44-3adc-48ca-8749-5128a53358d7&pageSize={VIDEO_COLLECT_SIZE}&column=lastest'
    res = requests.get(url, headers=headers)
    video_info_list = res.json().get('content')

    my_video_info_list = []
    for video_info in video_info_list:
        try:
            my_video_info = {}
            my_video_info.setdefault('name', video_info.get('momentClassificationBackup').get('workTitle'))
            my_video_info.setdefault('title', video_info.get('title'))
            my_video_info.setdefault('cover', video_info.get('cover')[0])
            my_video_info.setdefault('mp4', video_info.get('moreBackup').get('videos')[0].get('url'))
            my_video_info.setdefault('m3u8', video_info.get('moreBackup').get('videos')[0].get('hlsUrl'))
            my_video_info.setdefault('author_name', video_info.get('creatorBackup').get('name'))
            my_video_info.setdefault('author_avatar', video_info.get('creatorBackup').get('avatar'))
            my_video_info.setdefault('posted_time', datetime.datetime.fromtimestamp(float(video_info.get('createTime')) / 1000))
            my_video_info.setdefault('posted_by', '中舞网')
            my_video_info.setdefault('tags', [item.get('name') for item in video_info.get('avocationTags')])
            my_video_info_list.append(my_video_info)
        except:
            continue

    return my_video_info_list


def collect_tag():
    tag_list = []
    for i in range(1, 49):
        url = f'https://www.dance365.com/apis/avocation/avocations/rec/user?access_token=c494ae44-3adc-48ca-8749-5128a53358d7&pageNum={i}&PageSize=20'
        res = requests.get(url, headers=headers)
        ret = res.json().get('content')
        [tag_list.append({'title': i.get('name')}) for i in ret]
    return tag_list
