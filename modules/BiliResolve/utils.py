import os
import json
import re
import requests
from lxml import etree
from bilibili_api.video import get_video_info
from bilibili_api.utils import aid2bvid


def get_config():
    pwd = os.getcwd().replace('\\', '/')
    with open(pwd+'/modules/BiliResolve/config.json', 'r', encoding='utf-8') as j:
        config = json.load(j)
        return config
    return None


def get_bvid(url: str):
    b23_pattern = re.compile(r"https://b23.tv/[A-Za-z0-9]+")
    bv_pattern = re.compile(r"[Bb][Vv][A-Za-z0-9]+")
    av_pattern = re.compile(r"[Aa][Vv][0-9]+")
    bvid = ''
    # print(url)
    if result := bv_pattern.search(url):
        # print('bv')
        bvid = result.group()
    elif result := av_pattern.search(url):
        bvid = aid2bvid(int(re.sub('[Aa][Vv]', '', result.group())))
    elif result := b23_pattern.search(url):
        # print('b23')
        b23_url = result.group()
        try:
            resp = requests.get(b23_url, allow_redirects=False)
        except:
            pass
        else:
            if result := bv_pattern.search(resp.text):
                bvid = result.group()
    # print(bvid)
    return bvid


def gen_video_info_dict(url: str):
    if (bvid := get_bvid(url)) == '':
        return None
    # print('bvid=', bvid)
    info = get_video_info(bvid=bvid)
    return {
        'image': info['pic'],
        'plain': '标题：{title}\nUP主：{author}\nAV号：{aid}  BV号：{bvid}\n\n简介：\n{intro}\n\n播放：{play}\n弹幕：{danmaku}\n回复：{reply}\n获赞：{like}\n投币：{coin}\n收藏：{favorite}\n分享：{share}\n\n视频链接：{link}'
        .format(
            title=info['title'],
            author=info['owner']['name'],
            aid=info['aid'],
            bvid=info['bvid'],
            intro=info['desc'],
            play=info['stat']['view'],
            danmaku=info['stat']['view'],
            reply=info['stat']['reply'],
            like=info['stat']['like'],
            coin=info['stat']['coin'],
            favorite=info['stat']['favorite'],
            share=info['stat']['share'],
            link='https://www.bilibili.com/video/{}'.format(info['bvid'])
        )
    }
