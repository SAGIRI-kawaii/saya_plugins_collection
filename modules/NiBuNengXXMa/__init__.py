import logging
import os

from graia.application import GraiaMiraiApplication
from graia.application.exceptions import AccountMuted
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Image, Source
from graia.application.event.messages import GroupMessage
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.mirai import *

from PIL import ImageDraw, ImageFont

from PIL import Image as IMG

__name__ = "NiBuNengXXMa"
__description__ = "生成示例的这种图片"
__author__ = "eeehhheee"
__usage__ = "发送nbnxxm 文本1 文本2 即可"

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

saya.module_context()


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('nbnxxm .* .*')])]))
async def send_img(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain, source: Source):
    _, text1, text2 = message.asDisplay().split(" ")
    if os.path.exists(f'./modules/NiBuNengXXMa/temp/{text1} {text2}.jpg'):
        try:
            await app.sendGroupMessage(group, MessageChain.create(
                [At(member.id), Image.fromLocalFile(f'./modules/NiBuNengXXMa/temp/{text1} {text2}.jpg')]),
                                       quote=source.id)
        except AccountMuted:
            logging.warning('账户被禁言!')
    else:
        try:
            res = await create_img(text1=text1, text2=text2)
            await app.sendGroupMessage(group, MessageChain.create(
                [At(member.id), Image.fromLocalFile(res)]), quote=source.id)
        except AccountMuted:
            logging.warning('账户被禁言!')


font_size = 15


async def create_img(text1: str, text2: str):
    font = ImageFont.truetype('./modules/NiBuNengXXMa/ArialEnUnicodeBold.ttf', font_size)
    font_width_text1, font_height_text1 = font.getsize(text1)
    font_width_text2, font_height_text2 = font.getsize(text2)
    font_width_text1 = font_width_text1 / 2
    font_height_text1 = font_height_text1 / 2
    font_height_text2 = font_height_text2 / 2
    font_width_text2 = font_width_text2 / 2
    img = IMG.open('./modules/NiBuNengXXMa/BasicImage.jpg')
    draw = ImageDraw.Draw(img)
    draw.text((225 - font_width_text1, 75 - font_height_text1), text=text1, fill=(0, 0, 0), font=font)
    draw.text((350 - font_width_text2, 260 - font_height_text2), text=text2, fill=(0, 0, 0), font=font)
    img_name = f'{text1} {text2}.jpg'
    img.save(f'./modules/NiBuNengXXMa/temp/{img_name}')
    return f'./modules/NiBuNengXXMa/temp/{img_name}'
