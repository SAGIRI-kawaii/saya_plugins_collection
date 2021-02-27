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
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter

from .Sqlite3Manager import execute_sql

# 插件信息
__name__ = "KeywordReply"
__description__ = "一个关键词回复插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "发送关键词即可，若要设置关键词则发送 添加关键词#关键词/图片#回复文本/图片 即可"

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


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
            content_type = result[i][1]
            content = result[i][2]
            replies.append([content_type, content])
        # print(replies)
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
    member: Member,
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
        if keyword == "" or content == "":
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="怎么是空的啊！爬！")]))
            except AccountMuted:
                pass
            return None
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
        sql = f"SELECT * FROM keywordReply WHERE keyword=? AND `type`=? AND `content`=?"
        cursor.execute(sql, (keyword, content_type, content))
        if cursor.fetchall():
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="存在相同数据！进程退出")]))
                cursor.close()
                return None
            except AccountMuted:
                cursor.close()
                return None
        sql = f"INSERT INTO keywordReply (`keyword`, `type`, `content`) VALUES (?,?,?)"
        cursor.execute(sql, (keyword, content_type, content))

        conn.commit()
        cursor.close()
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="添加成功！")]))
        except AccountMuted:
            pass
    elif re.match(r"删除关键词#[\s\S]*", message_serialization):
        try:
            _, keyword = message_serialization.split("#")
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

        if re.match(r"\[mirai:image:{.*}\..*]", keyword):
            keyword = re.findall(r"\[mirai:image:{(.*?)}\..*]", keyword, re.S)[0]

        sql = f"SELECT * FROM keywordReply WHERE keyword='{keyword}'"
        if result := await execute_sql(sql):
            replies = []
            for i in range(len(result)):
                content_type = result[i][1]
                content = result[i][2]
                replies.append([content_type, content])
            msg = [Plain(text=f"关键词{keyword}目前有以下数据：\n")]
            for i in range(len(replies)):
                msg.append(Plain(text=f"{i + 1}. "))
                msg.append(Plain(text=replies[i][1]) if replies[i][0] == "text" else Image.fromUnsafeBytes(base64.b64decode(replies[i][1])))
                msg.append(Plain(text="\n"))
            msg.append(Plain(text="请发送你要删除的回复编号"))

            try:
                await app.sendGroupMessage(group, MessageChain.create(msg))
            except AccountMuted:
                return None

            number = 0

            @Waiter.create_using_function([GroupMessage])
            def number_waiter(
                    event: GroupMessage, waiter_group: Group,
                    waiter_member: Member, waiter_message: MessageChain
            ):
                nonlocal number
                if all([
                    waiter_group.id == group.id,
                    waiter_member.id == member.id,
                    waiter_message.asDisplay().isnumeric() and 0 < int(waiter_message.asDisplay()) <= len(replies)
                ]):
                    number = int(waiter_message.asDisplay())
                    return event
                elif all([
                    waiter_group.id == group.id,
                    waiter_member.id == member.id
                ]):
                    number = None
                    return event

            await inc.wait(number_waiter)

            if number is None:
                try:
                    await app.sendGroupMessage(group, MessageChain.create([Plain(text="非预期回复，进程退出")]))
                except AccountMuted:
                    pass
            elif 1 <= number <= len(replies):
                try:
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([
                            Plain(text="你确定要删除下列回复吗(是/否)：\n"),
                            Plain(text=keyword),
                            Plain(text="\n->\n"),
                            Plain(text=replies[number - 1][1]) if replies[number - 1][0] == "text" else Image.fromUnsafeBytes(base64.b64decode(replies[number - 1][1]))
                        ])
                    )
                except AccountMuted:
                    return None

                result = "否"

                @Waiter.create_using_function([GroupMessage])
                def confirm_waiter(
                        event: GroupMessage, waiter_group: Group,
                        waiter_member: Member, waiter_message: MessageChain
                ):
                    nonlocal result
                    if all([
                        waiter_group.id == group.id,
                        waiter_member.id == member.id
                    ]):
                        if re.match(r"[是否]", waiter_message.asDisplay()):
                            result = waiter_message.asDisplay()
                            return event

                await inc.wait(confirm_waiter)

                if result == "是":
                    sql = f"DELETE FROM keywordReply WHERE keyword=? AND `type`=? AND `content`=?"
                    conn = Sqlite3Manager.Sqlite3Manager.get_instance().get_conn()
                    cursor = conn.cursor()
                    cursor.execute(sql, (keyword, replies[number - 1][0], replies[number - 1][1]))
                    conn.commit()
                    cursor.close()
                    await app.sendGroupMessage(group, MessageChain.create([Plain(text="删除成功！")]))

                else:
                    try:
                        await app.sendGroupMessage(group, MessageChain.create([Plain(text="进程退出")]))
                    except AccountMuted:
                        pass
            else:
                try:
                    await app.sendGroupMessage(group, MessageChain.create([Plain(text="进程退出")]))
                except AccountMuted:
                    pass

        else:
            try:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="未检测到此关键词数据！")]))
            except AccountMuted:
                pass
