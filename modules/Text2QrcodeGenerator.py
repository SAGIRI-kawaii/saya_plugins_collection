import qrcode

from graia.application import GraiaMiraiApplication
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.exceptions import AccountMuted

# 插件信息
__name__ = "Text2QrcodeGenerator"
__description__ = "一个简易的文字转二维码的插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 `qrcode 内容` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def make_qrcode(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    if message.asDisplay().startswith("qrcode "):
        content = "".join([plain.text for plain in message[Plain]])[7:]
        try:
            if content:
                img = qrcode.make(content)
                img.save("./temp/tempQrcodeMaked.jpg")
                await app.sendGroupMessage(
                    group,
                    MessageChain.create([Image.fromLocalFile("./temp/tempQrcodeMaked.jpg")]),
                    quote=message[Source][0]
                )
            else:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="无效内容！")]))
        except AccountMuted:
            pass
