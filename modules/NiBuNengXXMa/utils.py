import uuid

from PIL import Image, ImageDraw, ImageFont

font_size = 15


def create_img(text2: str, text1: str):
    font = ImageFont.truetype('./modules/NiBuNengXXMa/ArialEnUnicodeBold.ttf', font_size)
    font_width_text1, font_height_text1 = font.getsize(text1)
    font_width_text2, font_height_text2 = font.getsize(text2)
    font_width_text1 = font_width_text1 / 2
    font_height_text1 = font_height_text1 / 2
    font_height_text2 = font_height_text2 / 2
    font_width_text2 = font_width_text2 / 2
    img = Image.open('./modules/NiBuNengXXMa/BasicImage.jpg')
    draw = ImageDraw.Draw(img)
    draw.text((225 - font_width_text2, 75 - font_height_text2), text=text2, fill=(0, 0, 0), font=font)
    draw.text((350 - font_width_text1, 260 - font_height_text1), text=text1, fill=(0, 0, 0), font=font)
    img_name = str(uuid.uuid4()) + '.jpg'
    img.save(f'./modules/NiBuNengXXMa/temp/{img_name}')
    return './modules/NiBuNengXXMa/temp/' + img_name
