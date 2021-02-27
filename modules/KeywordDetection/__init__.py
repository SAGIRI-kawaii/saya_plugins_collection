from aiohttp.client_exceptions import ClientResponseError

from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.exceptions import AccountMuted
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch

from .DFA import DFAUtils
from .utils import *

# 插件信息
__name__ = "KeywordDetection"
__description__ = "一个敏感词检测插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "控制插件开关：打开/关闭敏感词过滤"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

DFA = DFAUtils()
HostQQ = 1900384123


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def keyword_detection(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    message_text = message.asDisplay()
    if await get_group_switch(group.id):
        if DFA.filter_judge(message_text):
            try:
                try:
                    await app.revokeMessage(message[Source][0])
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([
                            Plain(text="检测到敏感词，自动撤回\n"),
                            Plain(text="过滤后：\n"),
                            Plain(text=DFA.replace_filter_word(message_text))
                        ]))
                except (ClientResponseError, PermissionError):
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([
                            Plain(text="检测到敏感词，发生错误: 无权限"),
                            Plain(text="\n过滤后：\n"),
                            Plain(text=DFA.replace_filter_word(message_text))
                        ]),
                        quote=message[Source][0]
                    )
            except AccountMuted:
                pass


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch("(打开|关闭)敏感词过滤")])]
))
async def switch_modify(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group,
    member: Member
):
    if member.id == HostQQ:
        switch = 1 if message.asDisplay()[:2] == "开启" else 0
        await set_group_switch(group.id, switch)
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text=f"敏感词过滤已{message.asDisplay()[:2]}")]))
        except AccountMuted:
            pass
    else:
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="你没有权限，爬！")]))
        except AccountMuted:
            pass
