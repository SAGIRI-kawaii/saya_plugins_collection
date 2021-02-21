import random
import base64
import aiohttp
import re

from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.exceptions import AccountMuted

from .Sqlite3Manager import execute_sql

# 插件信息
__name__ = "KeywordReply"
__description__ = "一个关键词回复插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送关键词即可，若要设置关键词则发送 添加关键词#关键词/图片#回复文本/图片 即可"

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def keyword_reply(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    message_serialization = message.asSerializationString()
    message_serialization = message_serialization.replace(
        "[mirai:source:" + re.findall(r'\[mirai:source:(.*?)]', message_serialization, re.S)[0] + "]",
        ""
    )
    if re.match(r"\[mirai:image:{.*}\..*]", message_serialization):
        message_serialization = re.findall(r"\[mirai:image:{(.*?)}\..*]", message_serialization, re.S)[0]
    sql = f"SELECT * FROM keywordReply WHERE keyword='{message_serialization}'"
    if result := await execute_sql(sql):
        replies = []
        for i in range(len(result)):
            content_type = result[0][1]
            content = result[0][2]
            replies.append([content_type, content])
        final_reply = random.choice(replies)

        content_type = final_reply[0]
        content = final_reply[1]
        try:
            if content_type == "img":
                await app.sendGroupMessage(group, MessageChain.create([Image.fromUnsafeBytes(base64.b64decode(content))]))
            elif content_type == "text":
                await app.sendGroupMessage(group, MessageChain.create([Plain(text=content)]))
            else:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text=f"unknown content_type:{content_type}")]))
        except AccountMuted:
            pass


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def add_keyword(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    message_serialization = message.asSerializationString()
    message_serialization = message_serialization.replace(
        "[mirai:source:" + re.findall(r'\[mirai:source:(.*?)]', message_serialization, re.S)[0] + "]",
        ""
    )
    if re.match(r"添加关键词#[\s\S]*#[\s\S]*", message_serialization):
        try:
            _, keyword, content = message_serialization.split("#")
        except ValueError:
            await app.sendGroupMessage(
                group,
                MessageChain.create([
                    Plain(text="设置格式：\n添加关键词#关键词/图片#回复文本/图片\n"),
                    Plain(text="注：目前不支持文本中含有#！")
                ])
            )
            return None
        keyword = keyword.strip()
        content = content.strip()
        content_type = "text"
        keyword_type = "text"
        if re.match(r"\[mirai:image:{.*}\..*]", keyword):
            keyword = re.findall(r"\[mirai:image:{(.*?)}\..*]", keyword, re.S)[0]
            keyword_type = "img"
        if re.match(r"\[mirai:image:{.*}\..*]", content):
            content_type = "img"
            image: Image = message[Image][0] if keyword_type == "text" else message[Image][1]
            async with aiohttp.ClientSession() as session:
                async with session.get(url=image.url) as resp:
                    content = await resp.read()
            content = base64.b64encode(content)

        conn = Sqlite3Manager.Sqlite3Manager.get_instance().get_conn()
        cursor = conn.cursor()
        sql = f"INSERT INTO keywordReply (`keyword`, `type`, `content`) VALUES (?,?,?)"
        cursor.execute(sql, (keyword, content_type, content))
        conn.commit()
        cursor.close()
        await app.sendGroupMessage(group, MessageChain.create([Plain(text="添加成功！")]))
