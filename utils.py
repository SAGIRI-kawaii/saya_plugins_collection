import json
import math
import os
from io import BytesIO
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont

from graia.application.message.elements.internal import MessageChain
from graia.application.message.elements.internal import Image_LocalFile
from graia.application.message.elements.internal import Image_UnsafeBytes
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application.message.elements import Element


def load_config(config_file: str = "config.json") -> dict:
    necessary_parameters = ["miraiHost", "authKey", "BotQQ"]
    with open(config_file, 'r', encoding='utf-8') as f:  # 从json读配置
        config = json.loads(f.read())
    for key in config.keys():
        config[key] = config[key].strip() if isinstance(config[key], str) else config[key]
    if any(parameter not in config for parameter in necessary_parameters):
        raise ValueError(f"{config_file} Missing necessary parameters! (miraiHost, authKey, BotQQ)")
    else:
        return config


async def get_final_text_lines(text: str, text_width: int, font: ImageFont.FreeTypeFont) -> int:
    lines = text.split("\n")
    line_count = 0
    for line in lines:
        if not line:
            line_count += 1
            continue
        line_count += int(math.ceil(float(font.getsize(line)[0]) / float(text_width)))
    # print("lines: ", line_count + 1)
    return line_count + 1


async def messagechain_to_img(
        message: MessageChain,
        max_width: int = 1080,
        font_size: int = 40,
        spacing: int = 15,
        padding_x: int = 20,
        padding_y: int = 15,
        img_fixed: bool = False,
        font_path: str = "./simhei.ttf",
        save_path: str = "./temp/tempMessageChainToImg.png"
) -> MessageChain:
    """
    将 MessageChain 转换为图片，仅支持只含有本地图片/文本的 MessageChain

    Args:
        message: 要转换的MessageChain
        max_width: 最大长度
        font_size: 字体尺寸
        spacing: 行间距
        padding_x: x轴距离边框大小
        padding_y: y轴距离边框大小
        img_fixed: 图片是否适应大小（仅适用于图片小于最大长度时）
        font_path: 字体文件路径
        save_path: 图片存储路径

    Examples:
        msg = await messagechain_to_img(message=message)

    Returns:
        MessageChain （内含图片Image类）
    """
    if not os.path.exists("temp"):
        os.mkdir("temp")
    font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
    message = message.asMerged()
    elements = message.__root__

    plains = message.get(Plain)
    text_gather = "\n".join([plain.text for plain in plains])
    # print(max(font.getsize(text)[0] for text in text_gather.split("\n")) + 2 * padding_x)
    final_width = min(max(font.getsize(text)[0] for text in text_gather.split("\n")) + 2 * padding_x, max_width)
    text_width = final_width - 2 * padding_x
    text_height = (font_size + spacing) * await get_final_text_lines(text_gather, text_width, font)

    img_height_sum = 0
    temp_img_list = []
    images = message.get(Image_LocalFile)
    for image in images:
        if isinstance(image, Image_LocalFile):
            temp_img = IMG.open(image.filepath)
            img_width, img_height = temp_img.size
            temp_img_list.append(
                temp_img := temp_img.resize(
                    (
                        int(final_width - 2 * spacing),
                        int(float(img_height * (final_width - 2 * spacing)) / float(img_width))
                    )
                ) if img_width > final_width - 2 * spacing or (img_fixed and img_width < final_width - 2 * spacing)
                else temp_img
            )
            img_height_sum = img_height_sum + temp_img.size[1]
        # elif isinstance(image, Image_UnsafeBytes):
        #     temp_img = IMG.open(BytesIO(image.image_bytes))
        else:
            raise Exception("messagechain_to_img：仅支持本地图片即Image_LocalFile类的处理！")
    final_height = 2 * padding_y + text_height + img_height_sum
    picture = IMG.new('RGB', (final_width, final_height), (255, 255, 255))
    draw = ImageDraw.Draw(picture)
    present_x = padding_x
    present_y = padding_y
    image_index = 0
    for element in elements:
        if isinstance(element, Image_LocalFile):
            # print(f"adding img {image_index}")
            picture.paste(temp_img_list[image_index], (present_x, present_y))
            present_y += (spacing + temp_img_list[image_index].size[1])
            image_index += 1
        elif isinstance(element, Plain):
            # print(f"adding text '{element.text}'")
            for char in element.text:
                if char == "\n":
                    present_y += (font_size + spacing)
                    present_x = padding_x
                    continue
                if char == "\r":
                    continue
                if present_x + font.getsize(char)[0] > text_width:
                    present_y += (font_size + spacing)
                    present_x = padding_x
                draw.text((present_x, present_y), char, font=font, fill=(0, 0, 0))
                present_x += font.getsize(char)[0]
            present_y += (font_size + spacing)
            present_x = padding_x

    picture.save(save_path)
    print(f"process finished! Image saved at {save_path}")
    return MessageChain.create([
        Image.fromLocalFile(save_path)
    ])


class MessageChainTools:
    @staticmethod
    def element_only(message: MessageChain, element_class: Element) -> bool:
        return all(type(element) is element_class for element in message.__root__)