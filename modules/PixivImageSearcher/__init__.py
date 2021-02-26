import aiohttp
from io import BytesIO
from PIL import Image as IMG
import time

from graia.application import GraiaMiraiApplication
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Source
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import At
from graia.application.message.elements.internal import Image
from graia.application.event.messages import GroupMessage
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.application.exceptions import AccountMuted
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.mirai import *

# 插件信息
__name__ = "PixivImageSearcher"
__description__ = "SauceNao以图搜图"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送搜图后发送图片即可"

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

# 填入你的saucenao_cookie
saucenao_cookie = ""


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([FullMatch('搜图')])]))
async def pixiv_image_searcher(app: GraiaMiraiApplication, member: Member, group: Group):
    image_get: bool = False
    message_received = None

    try:
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id), Plain("请在30秒内发送要搜索的图片呐~(仅支持pixiv图片搜索呐！)")
        ]))
    except AccountMuted:
        return None

    @Waiter.create_using_function([GroupMessage])
    def waiter(
            event: GroupMessage, waiter_group: Group,
            waiter_member: Member, waiter_message: MessageChain
    ):
        nonlocal image_get
        nonlocal message_received
        if time.time() - start_time < 30:
            if all([
                waiter_group.id == group.id,
                waiter_member.id == member.id,
                len(waiter_message[Image]) == len(waiter_message.__root__) - 1
            ]):
                image_get = True
                message_received = waiter_message
                return event
        else:
            print("等待用户发送图片超时！")
            return event

    start_time = time.time()
    await inc.wait(waiter)
    if image_get:
        try:
            await app.sendGroupMessage(
                group,
                await search_image(message_received[Image][0]),
                quote=message_received[Source][0]
            )
        except AccountMuted:
            pass


async def search_image(img: Image) -> MessageChain:
    path = "./modules/PixivImageSearcher/tempSavedImage.png"
    thumbnail_path = "./modules/PixivImageSearcher/tempThumbnail.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=img.url) as resp:
            img_content = await resp.read()
    image = IMG.open(BytesIO(img_content))
    image.save(path)

    # url for headers
    url = "https://saucenao.com/search.php"

    # picture url
    pic_url = img.url

    # json requesting url
    url2 = f"https://saucenao.com/search.php?db=999&output_type=2&testmode=1&numres=1&url={pic_url}"

    # data for posting.
    payload = {
        "url": pic_url,
        "numres": 1,
        "testmode": 1,
        "db": 999,
        "output_type": 2,
    }

    # header to fool the website.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Referer": url,
        "Origin": "https://saucenao.com",
        "Host": "saucenao.com",
        "cookie": saucenao_cookie
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=payload) as resp:
            json_data = await resp.json()

    if json_data["header"]["status"] == -1:
        return MessageChain.create([
            Plain(text=f"错误：{json_data['header']['message']}")
        ])
    print(json_data)

    if not json_data["results"]:
        return MessageChain.create([
            Plain(text="没有搜索到结果呐~")
        ])

    result = json_data["results"][0]
    header = result["header"]
    data = result["data"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url=header["thumbnail"]) as resp:
            img_content = await resp.read()

    image = IMG.open(BytesIO(img_content))
    image.save(thumbnail_path)
    similarity = header["similarity"]
    data_str = f"搜索到如下结果：\n\n相似度：{similarity}%\n"
    for key in data.keys():
        if isinstance(data[key], list):
            data_str += (f"\n{key}:\n    " + "\n".join(data[key]) + "\n")
        else:
            data_str += f"\n{key}:\n    {data[key]}\n"
    return MessageChain.create([
        Image.fromLocalFile(thumbnail_path),
        Plain(text=f"\n{data_str}")
    ])
