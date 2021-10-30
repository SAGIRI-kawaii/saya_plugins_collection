import json

import aiohttp
from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graiax import silkcoder


async def get_song_ordered(keyword: str, app: GraiaMiraiApplication) -> MessageChain:
    """
    Search song from CloudMusic

    Args:
        keyword: Keyword to search

    Examples:
        message = await get_song_ordered("lemon")

    Return:
        MessageChain: Message to be send
    """
    song_search_url = "http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={" \
                      "%s}&type=1&offset=0&total=true&limit=1" % keyword

    async with aiohttp.ClientSession() as session:
        async with session.get(url=song_search_url) as resp:
            data_json = await resp.read()
    data_json = json.loads(data_json)

    if data_json["code"] != 200:
        return MessageChain.create(
            [Plain(text=f"服务器返回错误：{data_json['message']}")])

    if data_json["result"]["songCount"] == 0:
        return MessageChain.create([Plain(text="没有搜索到呐~换一首歌试试吧！")])

    song_id = data_json["result"]["songs"][0]["id"]

    music_url = f"http://music.163.com/song/media/outer/url?id={song_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=music_url) as resp:
            music_bytes = await resp.read()

    music_bytes = await silkcoder.encode(music_bytes, t=120)

    upload_resp = await app.uploadVoice(music_bytes)

    return MessageChain.create([upload_resp])
