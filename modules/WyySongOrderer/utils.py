import aiofiles
import asyncio
import traceback
import aiohttp
import json
from pydub import AudioSegment
import jpype
from jpype import *

from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain


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
        return MessageChain.create([Plain(text=f"服务器返回错误：{data_json['message']}")])

    if data_json["result"]["songCount"] == 0:
        return MessageChain.create([Plain(text="没有搜索到呐~换一首歌试试吧！")])

    song_id = data_json["result"]["songs"][0]["id"]

    music_url = f"http://music.163.com/song/media/outer/url?id={song_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url=music_url) as resp:
            music_bytes = await resp.read()

    music_bytes = await silk(music_bytes, 'b', '-ss 0 -t 120')

    upload_resp = await app.uploadVoice(music_bytes)

    return MessageChain.create([upload_resp])


def silk4j_java():
    jarPath = "./silk4j-1.0.jar"
    jvmPath = jpype.getDefaultJVMPath()
    jpype.startJVM(jvmPath, "-ea", f"-Djava.class.path={jarPath}")
    audio_utils_class = JClass("io.github.mzdluo123.silk4j.AudioUtils")
    util = audio_utils_class()
    util.init()
    file = java.io.File("./cache.mp3")
    silk_file = util.mp3ToSilk(file)
    output_file = java.io.File("./cache.slk")
    file_input_stream = java.io.FileInputStream(silk_file)
    # buffer = jpype.JArray(tp=jpype.JByte)
    # while bytes_read := file_input_stream.read(buffer, 0, 1024):
    #     print(bytes_read)
    #     output_file.write(buffer, 0, bytes_read)

    util.streamToTempFile(file_input_stream, output_file)

    output_file.close()
    file_input_stream.close()

    jpype.shutdownJVM()


async def silk(data, mtype='b', options=''):
    try:
        cache_files = ['./modules/WyySongOrderer/cache.wav']

        if mtype == 'f':
            file = data
        elif mtype == 'b':
            async with aiofiles.open('./modules/WyySongOrderer/music_cache', 'wb') as f:
                await f.write(data)
            file = './modules/WyySongOrderer/music_cache'
            cache_files.append(file)
        else:
            raise ValueError("Not fit music_type. only 'f' and 'b'")

        cmd = [
            f'ffmpeg -i "{file}" {options} -af aresample=resampler=soxr -ar 24000 -ac 1 -y -loglevel error "./modules/WyySongOrderer/cache.wav"',
            f'"./modules/WyySongOrderer/silk_v3_encoder.exe" "./modules/WyySongOrderer/cache.wav" "./modules/WyySongOrderer/cache.slk" -quiet -tencent'
        ]

        for p in cmd:
            shell = await asyncio.create_subprocess_shell(p)
            await shell.wait()

        async with aiofiles.open(f'./modules/WyySongOrderer/cache.slk', 'rb') as f:
            b = await f.read()
        return b
    except Exception:
        traceback.print_exc()

silk4j_java()