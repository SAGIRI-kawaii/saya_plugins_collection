# -*- encoding=utf-8 -*-z`
from cnocr import CnOcr
from cnstd import CnStd
from PIL import Image as IMG
from io import BytesIO
import aiohttp
import numpy

from graia.application.message.elements.internal import Image

from .DFA import DFAUtils

DFA = DFAUtils()


async def word_valid(word: str) -> list:
    return DFA.filter_judge(word)


async def flat(lst: list) -> list:
    result = []
    for i in lst:
        if isinstance(i, list):
            result += await flat(i)
        else:
            result.append(i)
    return result


async def Img2Text(img: Image, ocr_model: CnOcr, std: CnStd) -> str:
    url = img.url
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()
    img = IMG.open(BytesIO(img_content)).convert("RGB")
    img = numpy.array(img)
    box_info_list = std.detect(img)
    res = []
    for box_info in box_info_list:
        cropped_img = box_info['cropped_img']  # 检测出的文本框
        ocr_res = ocr_model.ocr_for_single_line(cropped_img)
        res.append([ocr_res])
    print(res)
    return "".join(await flat(res))
