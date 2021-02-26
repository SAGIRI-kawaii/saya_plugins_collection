from PIL import Image as IMG, ImageDraw, ImageFont
import os

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
    inline_dispatchers=[Kanata([RegexMatch('ph .* .*')])]
))
async def pornhub_style_logo_generator(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    try:
        _, left_text, right_text = message.asDisplay().split(" ")
        try:
            await app.sendGroupMessage(group, await make_ph_style_logo(left_text, right_text))
        except AccountMuted:
            pass
    except ValueError:
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="参数非法！使用格式：ph text1 text2")]))
        except AccountMuted:
            pass


LEFT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT = 2
LEFT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH = 1 / 4
RIGHT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT = 1
RIGHT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH = 1 / 4
RIGHT_PART_RADII = 10
BG_COLOR = '#000000'
BOX_COLOR = '#F7971D'
LEFT_TEXT_COLOR = '#FFFFFF'
RIGHT_TEXT_COLOR = '#000000'
FONT_SIZE = 50


async def create_left_part_img(text: str, font_size: int):
    font = ImageFont.truetype('./modules/PornhubStyleLogoGenerator/ttf/ArialEnUnicodeBold.ttf', font_size)
    font_width, font_height = font.getsize(text)
    offset_y = font.font.getsize(text)[1][1]
    blank_height = font_height * LEFT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT
    right_blank = int(font_width / len(text) * LEFT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH)
    img_height = font_height + offset_y + blank_height * 2
    image_width = font_width + right_blank
    image_size = image_width, img_height
    image = IMG.new('RGBA', image_size, BG_COLOR)
    draw = ImageDraw.Draw(image)
    draw.text((0, blank_height), text, fill=LEFT_TEXT_COLOR, font=font)
    return image


async def create_right_part_img(text: str, font_size: int):
    radii = RIGHT_PART_RADII
    font = ImageFont.truetype('./modules/PornhubStyleLogoGenerator/ttf/ArialEnUnicodeBold.ttf', font_size)
    font_width, font_height = font.getsize(text)
    offset_y = font.font.getsize(text)[1][1]
    blank_height = font_height * RIGHT_PART_VERTICAL_BLANK_MULTIPLY_FONT_HEIGHT
    left_blank = int(font_width / len(text) * RIGHT_PART_HORIZONTAL_BLANK_MULTIPLY_FONT_WIDTH)
    image_width = font_width + 2 * left_blank
    image_height = font_height + offset_y + blank_height * 2
    image = IMG.new('RGBA', (image_width, image_height), BOX_COLOR)
    draw = ImageDraw.Draw(image)
    draw.text((left_blank, blank_height), text, fill=RIGHT_TEXT_COLOR, font=font)

    # 圆
    magnify_time = 10
    magnified_radii = radii * magnify_time
    circle = IMG.new('L', (magnified_radii * 2, magnified_radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, magnified_radii * 2, magnified_radii * 2), fill=255)  # 画白色圆形

    # 画4个角（将整圆分离为4个部分）
    magnified_alpha_width = image_width * magnify_time
    magnified_alpha_height = image_height * magnify_time
    alpha = IMG.new('L', (magnified_alpha_width, magnified_alpha_height), 255)
    alpha.paste(circle.crop((0, 0, magnified_radii, magnified_radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((magnified_radii, 0, magnified_radii * 2, magnified_radii)),
                (magnified_alpha_width - magnified_radii, 0))  # 右上角
    alpha.paste(circle.crop((magnified_radii, magnified_radii, magnified_radii * 2, magnified_radii * 2)),
                (magnified_alpha_width - magnified_radii, magnified_alpha_height - magnified_radii))  # 右下角
    alpha.paste(circle.crop((0, magnified_radii, magnified_radii, magnified_radii * 2)),
                (0, magnified_alpha_height - magnified_radii))  # 左下角
    alpha = alpha.resize((image_width, image_height), IMG.ANTIALIAS)
    image.putalpha(alpha)
    return image


async def combine_img(left_text: str, right_text, font_size: int, out_put_path: str):
    left_img = await create_left_part_img(left_text, font_size)
    right_img = await create_right_part_img(right_text, font_size)
    blank = 30
    bg_img_width = left_img.width + right_img.width + blank * 2
    bg_img_height = left_img.height
    bg_img = IMG.new('RGBA', (bg_img_width, bg_img_height), BG_COLOR)
    bg_img.paste(left_img, (blank, 0))
    bg_img.paste(right_img, (blank + left_img.width, int((bg_img_height - right_img.height) / 2)), mask=right_img)
    bg_img.save(out_put_path)


async def make_ph_style_logo(left_text: str, right_text: str) -> MessageChain:
    img_name = f'ph_{left_text}_{right_text}.png'
    out_put_path = f"./modules/PornhubStyleLogoGenerator/temp/{img_name}"
    if not os.path.exists("./modules/PornhubStyleLogoGenerator/temp"):
        os.mkdir("./modules/PornhubStyleLogoGenerator/temp")
    await combine_img(left_text, right_text, FONT_SIZE, out_put_path)
    return MessageChain.create([Image.fromLocalFile(out_put_path)])
