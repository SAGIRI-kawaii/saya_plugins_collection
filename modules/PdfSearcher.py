import aiohttp
from bs4 import BeautifulSoup
import re
import qrcode
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont

from graia.application.message.elements.internal import MessageChain
from graia.application.message.elements.internal import Image
from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import GroupMessage
from graia.application.event.messages import Group
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.exceptions import AccountMuted

# 插件信息
__name__ = "PdfSearcher"
__description__ = "搜索PDF"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 `pdf 关键词` 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('pdf .*')])]))
async def pdf_searcher(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    keyword = message.asDisplay()[4:]
    try:
        await app.sendGroupMessage(group, await search_pdf(keyword))
    except AccountMuted:
        pass


async def search_pdf(keyword: str) -> MessageChain:
    url = f"https://zh.1lib.us/s/?q={keyword}"
    base_url = "https://zh.1lib.us"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            html = await resp.read()
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find("div", {"id": "searchResultBox"}).find_all("div", {"class": "resItemBox resItemBoxBooks exactMatch"})
    count = 0
    books = []
    text = "搜索到以下结果：\n\n"
    for div in divs:
        count += 1
        if count > 5:
            break
        name = div.find("h3").get_text().strip()
        href = div.find("h3").find("a", href=True)["href"]
        first_div = div.find("table").find("table").find("div")
        publisher = first_div.get_text().strip() if re.search('.*?title="Publisher".*?', str(first_div)) else None
        authors = div.find("div", {"class": "authors"}).get_text().strip()

        text += f"{count}.\n"
        text += f"名字：{name}\n"
        text += f"作者：{authors}\n" if authors else ""
        text += f"出版社：{publisher}\n" if publisher else ""
        text += f"页面链接：{base_url + href}\n\n"

        books.append({
            "name": name,
            "href": base_url + href,
            "publisher": publisher,
            "authors": authors,
            # "download_href": base_url + download_href
        })

        print(name, href, publisher, authors, sep="\n", end="\n\n")

    if not books:
        text = "未搜索到结果呢 >A<\n要不要换个关键词试试呢~"
        return MessageChain.create([Plain(text=text)])

    text = text.replace("搜索到以下结果：\n\n", "")
    pics_path = await text2piiic_with_link(text=text)
    msg = [Plain(text="搜索到以下结果：\n\n")]
    for path in pics_path:
        msg.append(Image.fromLocalFile(path))
    return MessageChain.create(msg)


def is_chinese(ch):
    if '\u4e00' <= ch <= '\u9fff':
        return True
    return False


def count_len(string: str) -> int:
    length = 0
    for i in string:
        length += 2 if is_chinese(i) else 1
    return length


async def text2piiic_with_link(text: str, fontsize=40, x=20, y=40, spacing=15):
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    match_res = re.findall(pattern, text, re.S)
    for mres in match_res:
        text = text.replace(mres, "|||\n\n\n|||")
    for i in range(len(match_res)):
        qrcode_img = qrcode.make(match_res[i])
        qrcode_img.save(f"./temp/tempQrcodeWithLink{i + 1}.jpg")
    blocks = text.split("|||\n\n\n|||")
    block_count = 0
    font = ImageFont.truetype('./simhei.ttf', fontsize, encoding="utf-8")
    for block in blocks:
        if not block or not block.strip():
            break
        block_count += 1
        lines = block.strip().split("\n")
        length = max(count_len(line) for line in lines)
        width = x * 4 + int(fontsize * (length + 10) / 2)
        height = y * 4 + (fontsize + spacing) * len(lines) + width
        qr_img = IMG.open(f"./temp/tempQrcodeWithLink{block_count}.jpg")
        qr_img = qr_img.resize((width, width))
        picture = IMG.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(picture)
        for i in range(len(lines)):
            y_pos = y + i * (fontsize + spacing)
            draw.text((x, y_pos), lines[i], font=font, fill=(0, 0, 0))
        y_pos = y + len(lines) * (fontsize + spacing)
        picture.paste(qr_img, (0, y_pos))
        picture.save(f"./temp/tempText2piiicWithLink{block_count}.jpg")

    return [
        f"./temp/tempText2piiicWithLink{i + 1}.jpg" for i in range(block_count)
    ]
