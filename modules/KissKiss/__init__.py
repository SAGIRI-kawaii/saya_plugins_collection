from PIL import Image as IMG
from PIL import ImageOps
from moviepy.editor import ImageSequenceClip as imageclip
import numpy
import aiohttp
from io import BytesIO
import os

from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At
from graia.application.message.elements.internal import Image
from graia.application.event.messages import Group
from graia.application.exceptions import AccountMuted

# 插件信息
__name__ = "KissKiss"
__description__ = "生成亲吻gif"
__author__ = "Super_Water_God"
__usage__ = "在群内发送 亲@目标 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def petpet_generator(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    if message.has(At) and message.asDisplay().startswith("亲") and message.get(At)[0].target != app.connect_info.account:
        if not os.path.exists("./modules/KissKiss/temp"):
            os.mkdir("./modules/KissKiss/temp")
        AtQQ = message.get(At)[0].target
        if member.id == AtQQ:
            await app.sendGroupMessage(group, MessageChain.create([Plain("请不要自交~😋")]), quote=message[Source][0])
        else:
            SavePic = f"./modules/KissKiss/temp/tempKiss-{member.id}-{AtQQ}.gif"
            await kiss(member.id, AtQQ)
            await app.sendGroupMessage(group, MessageChain.create([Image.fromLocalFile(SavePic)]))


async def save_gif(gif_frames, dest, fps=10):
    clip = imageclip(gif_frames, fps=fps)
    clip.write_gif(dest)
    clip.close()


async def kiss_make_frame(operator, target, i):
    operator_x = [92, 135, 84, 80, 155, 60, 50, 98, 35, 38, 70, 84, 75]
    operator_y = [64, 40, 105, 110, 82, 96, 80, 55, 65, 100, 80, 65, 65]
    target_x = [58, 62, 42, 50, 56, 18, 28, 54, 46, 60, 35, 20, 40]
    target_y = [90, 95, 100, 100, 100, 120, 110, 100, 100, 100, 115, 120, 96]
    bg = Image.open(f"./modules/KissKiss/KissFrames/{i}.png")
    gif_frame = Image.new('RGB', (200, 200), (255, 255, 255))
    gif_frame.paste(bg, (0, 0))
    gif_frame.paste(target, (target_x[i - 1], target_y[i - 1]), target)
    gif_frame.paste(operator, (operator_x[i - 1], operator_y[i - 1]), operator)
    return numpy.array(gif_frame)


async def kiss(operator_id, target_id) -> None:
    operator_url = f'http://q1.qlogo.cn/g?b=qq&nk={str(operator_id)}&s=640'
    target_url = f'http://q1.qlogo.cn/g?b=qq&nk={str(target_id)}&s=640'
    gif_frames = []
    if str(operator_id) != "":  # admin自定义
        async with aiohttp.ClientSession() as session:
            async with session.get(url=operator_url) as resp:
                operator_img = await resp.read()
        operator = Image.open(BytesIO(operator_img))
    else:
        operator = Image.open("./modules/KissKiss/avatar.png")

    if str(target_id) != "":  # admin自定义
        async with aiohttp.ClientSession() as session:
            async with session.get(url=target_url) as resp:
                target_img = await resp.read()
        target = Image.open(BytesIO(target_img))
    else:
        target = Image.open("./modules/KissKiss/avatar.png")

    operator = operator.resize((40, 40), Image.ANTIALIAS)
    size = operator.size
    r2 = min(size[0], size[1])
    circle = Image.new('L', (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = Image.new('L', (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    operator.putalpha(alpha)

    target = target.resize((50, 50), Image.ANTIALIAS)
    size = target.size
    r2 = min(size[0], size[1])
    circle = Image.new('L', (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = Image.new('L', (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    target.putalpha(alpha)

    for i in range(1, 14):
        gif_frames.append(await kiss_make_frame(operator, target, i))
    await save_gif(gif_frames, f'./modules/KissKiss/temp/tempKiss-{operator_id}-{target_id}.gif', fps=25)
