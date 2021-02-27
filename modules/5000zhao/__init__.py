from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.exceptions import AccountMuted
from graia.application.event.messages import GroupMessage, Group, Member
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch

from .utils import genImage

# 插件信息
__name__ = "PornhubStyleLogoGenerator"
__description__ = "一个可以生成 pornhub style logo 的插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送 `ph text1 text2` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch('5000兆 .* .*')])]
))
async def pornhub_style_logo_generator(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    try:
        _, left_text, right_text = message.asDisplay().split(" ")
        try:
            try:
                genImage(word_a=left_text, word_b=right_text).save("./modules/5000zhao/test.png")
            except TypeError:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="不支持的内容！不要给我一些稀奇古怪的东西！")]))
                return None
            await app.sendGroupMessage(group, MessageChain.create([Image.fromLocalFile("./modules/5000zhao/test.png")]))
        except AccountMuted:
            pass
    except ValueError:
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="参数非法！使用格式：5000兆 text1 text2")]))
        except AccountMuted:
            pass
