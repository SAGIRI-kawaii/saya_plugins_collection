import aiohttp
from bs4 import BeautifulSoup

from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.exceptions import AccountMuted

from utils import messagechain_to_img

# 插件信息
__name__ = "GithubHotSearch"
__description__ = "获取当前github热搜(trend)"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 github热搜 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([FullMatch('github热搜')])]))
async def group_message_listener(app: GraiaMiraiApplication, group: Group):
    try:
        await app.sendGroupMessage(
            group,
            await get_github_hot()
        )
    except AccountMuted:
        pass


async def get_github_hot() -> MessageChain:
    url = "https://github.com/trending"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            html = await resp.read()
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("article", {"class": "Box-row"})

    text_list = ["github实时热榜:\n"]
    index = 0
    for i in articles:
        try:
            index += 1
            text_list.append("\n%d. %s\n" % (index, i.find("h1").get_text().replace("\n", "").replace(" ", "").replace("\\", " \\ ")))
            text_list.append("\n    %s\n" % i.find("p").get_text().strip())
        except:
            pass

    text = "".join(text_list).replace("#", "")
    return await messagechain_to_img(MessageChain.create([Plain(text=text)]), max_width=2000)
