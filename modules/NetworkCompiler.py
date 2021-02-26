import aiohttp
import re

from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.exceptions import AccountMuted

# 插件信息
__name__ = "NetworkCompiler"
__description__ = "网络编译器（菜鸟教程）"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 super 语言:\\n代码 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch('super .*:[\n\r][\s\S]*')])]
))
async def network_compiler(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    message_text = message.asDisplay()
    language = re.findall(r"super (.*?):", message_text, re.S)[0]
    code = message_text[8 + len(language):]
    result = await network_compile(language, code)
    print(result)
    try:
        if isinstance(result, str):
            await app.sendGroupMessage(group, MessageChain.create([Plain(text=result)]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text=result["output"] if result["output"] else result["errors"])]))
    except AccountMuted:
        pass


legal_language = {
    "R": 80,
    "vb": 84,
    "ts": 1001,
    "kt": 19,
    "pas": 18,
    "lua": 17,
    "node.js": 4,
    "go": 6,
    "swift": 16,
    "rs": 9,
    "sh": 11,
    "pl": 14,
    "erl": 12,
    "scala": 5,
    "cs": 10,
    "rb": 1,
    "cpp": 7,
    "c": 7,
    "java": 8,
    "py3": 15,
    "py": 0,
    "php": 3
}


async def network_compile(language: str, code: str):
    if language not in legal_language:
        return f"支持的语言：{', '.join(list(legal_language.keys()))}"
    url = "https://tool.runoob.com/compile2.php"
    payload = {
        "code": code,
        "token": "4381fe197827ec87cbac9552f14ec62a",
        "stdin": "",
        "language": legal_language[language],
        "fileext": language
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=payload) as resp:
            res = await resp.json()
    return {
        "output": res["output"],
        "errors": res["errors"]
    }
