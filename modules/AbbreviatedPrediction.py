import aiohttp

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage, Group
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.exceptions import AccountMuted

# 插件信息
__name__ = "AbbreviatedPrediction"
__description__ = "一个可以获取字母缩写内容的插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 `缩 缩写` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('缩 .*')])]))
async def abbreviated_prediction(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    if abbreviation := message.asDisplay()[2:]:
        try:
            if abbreviation.isalnum():
                await app.sendGroupMessage(group, await get_abbreviation_explain(abbreviation))
            else:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="缩写部分只能为英文/数字！")]))
        except AccountMuted:
            pass


async def get_abbreviation_explain(abbreviation: str) -> MessageChain:
    url = "https://lab.magiconch.com/api/nbnhhsh/guess"
    headers = {
        "referer": "https://lab.magiconch.com/nbnhhsh/"
    }
    data = {
        "text": abbreviation
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=data) as resp:
            res = await resp.json()
    # print(res)
    result = "可能的结果:\n\n"
    has_result = False
    for i in res:
        if "trans" in i:
            if i["trans"]:
                has_result = True
                result += f"{i['name']} => {'，'.join(i['trans'])}\n\n"
            else:
                result += f"{i['name']} => 没找到结果！\n\n"
        else:
            if i["inputting"]:
                has_result = True
                result += f"{i['name']} => {'，'.join(i['inputting'])}\n\n"
            else:
                result += f"{i['name']} => 没找到结果！\n\n"

    if has_result:
        return MessageChain.create([Plain(text=result)])
    else:
        return MessageChain.create([Plain(text="没有找到结果哦~")])
