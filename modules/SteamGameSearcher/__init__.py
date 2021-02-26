import os
import aiohttp
from PIL import Image as IMG
from io import BytesIO
import re

from graia.application.message.chain import MessageChain
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.exceptions import AccountMuted
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage, Group
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch

from utils import messagechain_to_img

# 插件信息
__name__ = "SteamGameSearcher"
__description__ = "一个通过关键词搜索steam游戏的插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 `steam 游戏名` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch('steam .*')])]
))
async def steam_game_searcher(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    keyword = message.asDisplay()[6:]
    try:
        if keyword:
            await app.sendGroupMessage(group, await get_steam_game_search(keyword))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="请输入你要搜索的关键词（英文更管用哦~）")]))
    except AccountMuted:
        pass


async def get_steam_game_description(game_id: int) -> str:
    """
    Return game description on steam

    Args:
        game_id: Steam shop id of target game

    Examples:
        get_steam_game_description(502010)

    Return:
        str
    """
    url = "https://store.steampowered.com/app/%s/" % game_id
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            html = await resp.text()
    description = re.findall(r'<div class="game_description_snippet">(.*?)</div>', html, re.S)
    if len(description) == 0:
        return "none"
    return description[0].lstrip().rstrip()


async def get_steam_game_search(keyword: str, msg_type: str = "text") -> MessageChain:
    """
    Return search result

    Args:
        keyword: Keyword to search(game name)
        msg_type: Type of MessageChain

    Examples:
        await get_steam_game_search("Monster Hunter")

    Return:
        MessageChain
    """

    base_path = "./modules/SteamGameSearcher/game_cover_cache/"
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    url = "https://steamstats.cn/api/steam/search?q=%s&page=1&format=json&lang=zh-hans" % keyword
    headers = {
        "referer": "https://steamstats.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36 "
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            result = await resp.json()

    if len(result["data"]["results"]) == 0:
        return MessageChain.create([Plain(text=f"搜索不到{keyword}呢~检查下有没有吧~偷偷告诉你，搜英文名的效果可能会更好哟~")])
    else:
        result = result["data"]["results"][0]
        path = f"{base_path}{result['app_id']}.png"
        print(f"cache: {os.path.exists(path)}")
        if not os.path.exists(path):
            async with aiohttp.ClientSession() as session:
                async with session.get(url=result["avatar"]) as resp:
                    img_content = await resp.read()
            image = IMG.open(BytesIO(img_content))
            image.save(path)
        description = await get_steam_game_description(result["app_id"])
        msg = MessageChain.create([
                Plain(text="\n搜索到以下信息：\n"),
                Plain(text="游戏：%s (%s)\n" % (result["name"], result["name_cn"])),
                Plain(text="游戏id：%s\n" % result["app_id"]),
                Image.fromLocalFile(path),
                Plain(text="游戏描述：%s\n" % description),
                Plain(text="\nsteamUrl:https://store.steampowered.com/app/%s/" % result["app_id"])
            ])
        return await messagechain_to_img(msg) if msg_type == "img" else msg
