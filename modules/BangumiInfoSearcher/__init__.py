import aiohttp
import os
from PIL import Image as IMG
from io import BytesIO
import urllib.parse as parse

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import At
from graia.application.message.elements.internal import Image
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.exceptions import AccountMuted
from graia.application.event.messages import GroupMessage, Group, Member
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch

from utils import messagechain_to_img

# 插件信息
__name__ = "BangumiInfoSearcher"
__description__ = "一个可以搜索番剧信息的插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送 `番剧 番剧名` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch('番剧 .*')])]
))
async def bangumi_info_searcher(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group,
    member: Member
):
    keyword = message.asDisplay()[3:]
    try:
        if keyword:
            await app.sendGroupMessage(group, await get_bangumi_info(keyword, member.id))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="请输入你要搜索的关键词")]))
    except AccountMuted:
        pass


async def get_bangumi_info(keyword: str, sender: int) -> MessageChain:
    headers = {
        "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
    }
    url = "https://api.bgm.tv/search/subject/%s?type=2&responseGroup=Large&max_results=1" % parse.quote(keyword)
    # print(url)
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers) as resp:
            data = await resp.json()

    if "code" in data.keys() and data["code"] == 404 or not data["list"]:
        return MessageChain.create([At(target=sender), Plain(text=f"番剧 {keyword} 未搜索到结果！")])

    bangumi_id = data["list"][0]["id"]
    url = "https://api.bgm.tv/subject/%s?responseGroup=medium" % bangumi_id
    # print(url)

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers) as resp:
            data = await resp.json()
    # print(data)
    name = data["name"]
    cn_name = data["name_cn"]
    summary = data["summary"]
    img_url = data["images"]["large"]
    score = data["rating"]["score"]
    rank = data["rank"] if "rank" in data.keys() else None
    rating_total = data["rating"]["total"]
    path = f"./modules/BangumiInfoSearcher/bangumi_cover_cache/{name}.jpg"
    if not os.path.exists("./modules/BangumiInfoSearcher/bangumi_cover_cache"):
        os.mkdir("./modules/BangumiInfoSearcher/bangumi_cover_cache")
    if not os.path.exists(path):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=img_url) as resp:
                img_content = await resp.read()
        image = IMG.open(BytesIO(img_content))
        image.save(path)
    message = MessageChain.create([
            Plain(text="查询到以下信息：\n"),
            Image.fromLocalFile(path),
            Plain(text=f"名字:{name}\n\n中文名字:{cn_name}\n\n"),
            Plain(text=f"简介:{summary}\n\n"),
            Plain(text=f"bangumi评分:{score}(参与评分{rating_total}人)"),
            Plain(text=f"\n\nbangumi排名:{rank}" if rank else "")
        ])
    return await messagechain_to_img(message=message, max_width=1080, img_fixed=True)
