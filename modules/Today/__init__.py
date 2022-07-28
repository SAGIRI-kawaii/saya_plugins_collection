from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, ElementMatch, ElementResult,WildcardMatch, RegexResult, RegexMatch
from graia.ariadne.model import Group, Member
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.element import At, Plain, Image, Forward, ForwardNode
import aiohttp
from bilibili_api import article, sync

from sagiri_bot.control import FrequencyLimit, Function, BlackListControl, UserCalledCountControl, Interval
from sagiri_bot.core.app_core import AppCore
from sagiri_bot.orm.async_orm import Setting
from sagiri_bot.utils import group_setting

saya = Saya.current()
channel = Channel.current()

channel.name("today")
channel.description("日报")
channel.author("Hiy0ri")

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                FullMatch("日报")
            )
        ],
    decorators=[
        FrequencyLimit.require("today", 1),
        Function.require(channel.module, notice=True),
        BlackListControl.enable(),
        UserCalledCountControl.add(UserCalledCountControl.FUNCTIONS)
    ]
    )
)
async def today(app: Ariadne, group: Group, message: MessageChain):
    ero_url = "https://test.tianque.top/destiny2/today/"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json()
        pic_url = ret["img_url"]
        async with session.get(pic_url) as r:
            pic = await r.read()
        await app.sendMessage(group, MessageChain.create(Image(data_bytes=pic)))

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                FullMatch("周报")
            )
        ],
    decorators=[
        FrequencyLimit.require("week", 1),
        Function.require(channel.module, notice=True),
        BlackListControl.enable(),
        UserCalledCountControl.add(UserCalledCountControl.FUNCTIONS)
    ]
    )
)
async def week(app: Ariadne, group: Group, message: MessageChain):
        ar = await article.get_article_list(rlid=175327)
        ar_id=ar["articles"][-1]["id"]
        ar_text=article.Article(ar_id)
        await ar_text.fetch_content()
        img_url=ar_text.json()["children"][2]["url"]
        async with aiohttp.ClientSession() as session:
           async with session.get(img_url) as r:
              pic = await r.read()
        await app.sendMessage(group, MessageChain.create(Image(data_bytes=pic)))

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                FullMatch("复读"), WildcardMatch() @ "content"
            )
        ],
    decorators=[
        FrequencyLimit.require("fudu", 1),
        Function.require(channel.module, notice=True),
        BlackListControl.enable(),
        UserCalledCountControl.add(UserCalledCountControl.FUNCTIONS)
    ]
    )
)
async def fudu(app: Ariadne, group: Group, message: MessageChain, content: RegexResult):
        content = content.result.asDisplay().strip()
        count=int(content[content.index(" "):])
        for i in range(count):
              await app.sendGroupMessage(group, MessageChain(content[:content.index(" ")]))
