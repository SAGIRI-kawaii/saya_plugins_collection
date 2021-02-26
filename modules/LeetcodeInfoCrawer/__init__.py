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
from graia.application.message.parser.signature import FullMatch

from .leetcode_user_info_crawer import get_leetcode_user_statics
from .leetcode_daily_question_crawer import get_leetcode_daily_question

# 插件信息
__name__ = "LeetcodeInfoCrawer"
__description__ = "一个可以获取leetcode信息的插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "查询用户信息：发送 leetcode userSlug (userSlug为个人唯一标识 个人主页地址 -> https://leetcode-cn.com/u/userSlug/)" \
            "\n查询每日一题：发送 leetcode每日一题 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch("leetcode .*")])]
))
async def leetcode_user_info_crawer(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    try:
        if userSlug := message.asDisplay()[9:]:
            await app.sendGroupMessage(group, await get_leetcode_user_statics(userSlug))
        else:
            await app.sendGroupMessage(
                group,
                MessageChain.create([
                    Plain(text="请输入userSlug！\nuserSlug为个人主页地址的标识（https://leetcode-cn.com/u/userSlug/）")
                ])
            )
    except AccountMuted:
        pass


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch("leetcode每日一题.*")])]
))
async def leetcode_daily_question(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    try:
        await app.sendGroupMessage(group, await get_leetcode_daily_question())
    except AccountMuted:
        pass
