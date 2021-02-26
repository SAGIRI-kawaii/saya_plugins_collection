import re

from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.exceptions import AccountMuted
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage, Group, Member
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.event.lifecycle import ApplicationLaunched
from graia.application.event.mirai import BotJoinGroupEvent
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter

from .Sqlite3Manager import execute_sql
from .utils import *

# 插件信息
__name__ = "ImageSender"
__description__ = "一个图片(setu)发送插件"
__author__ = "SAGIRI-kawaii"
__usage__ = "获取图片：在群内发送设置好的关键词即可\n" \
            "关键词管理：在群内发送 `(添加/删除)关键词(文字/图片)` 即可（需要管理）\n" \
            "管理员管理：在群内发送 `(添加/删除)管理员(At/QQ号)` 即可（需要hostQQ）"

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def data_init(app: GraiaMiraiApplication):
    group_list = await app.groupList()
    await check_group_data_init(group_list)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def image_sender(app: GraiaMiraiApplication, message: MessageChain, group: Group):
    message_serialization = message.asSerializationString()
    message_serialization = message_serialization.replace(
        "[mirai:source:" + re.findall(r'\[mirai:source:(.*?)]', message_serialization, re.S)[0] + "]",
        ""
    )
    if re.match(r"\[mirai:image:{.*}\..*]", message_serialization):
        message_serialization = re.findall(r"\[mirai:image:{(.*?)}\..*]", message_serialization, re.S)[0]
    sql = f"SELECT * FROM keywords WHERE keyword='{message_serialization}'"
    if result := await execute_sql(sql):
        function = result[0][1]
        if function == "setu":
            sql = f"SELECT setu, setu18 FROM setting WHERE groupId='{group.id}'"
            result = (await execute_sql(sql))[0]
            if result[0] and result[1]:
                await app.sendGroupMessage(group, await get_pic("setu18"))
            elif result[0] and not result[1]:
                await app.sendGroupMessage(group, await get_pic(function))
            else:
                await app.sendGroupMessage(group, MessageChain.create([Plain(text="烧鹅图功能尚未开启~")]))
        elif function in ["real", "realHighq"]:
            sql = f"SELECT real, realHighq FROM setting WHERE groupId='{group.id}'"
            result = (await execute_sql(sql))[0]
            if result[0] and result[1]:
                await app.sendGroupMessage(group, await get_pic(function))
            elif result[0] and not result[1] and function == "real":
                await app.sendGroupMessage(group, await get_pic(function))
            else:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create([Plain(text=f"{function}图功能尚未开启~")])
                )
        else:
            sql = f"SELECT {function} FROM setting WHERE groupId='{group.id}'"
            if (await execute_sql(sql))[0][0]:
                await app.sendGroupMessage(group, await get_pic(function))
            else:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create([Plain(text=f"{function}图功能尚未开启~")])
                )


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch("(打开|关闭).*功能")])]))
async def switch_control(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    legal_config = ("setu", "setu18", "real", "realHighq", "bizhi", "sketch")
    config = re.findall(r"(.*?)功能", message.asDisplay()[2:], re.S)[0]
    if message.asDisplay().startswith("打开"):
        new_setting_value = 1
    else:
        new_setting_value = 0
    try:
        if config in legal_config:
            admins = await get_admin(group.id)
            if member.id in admins:
                await update_setting(group.id, config, new_setting_value)
                await app.sendGroupMessage(group, MessageChain.create([Plain(f"本群{config}已{message.asDisplay()[:2]}")]))
            else:
                await app.sendGroupMessage(group, MessageChain.create([Plain("不是管理员！给爷爬!")]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain("错误的选项!")]))
    except AccountMuted:
        pass


@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        # inline_dispatchers=[Kanata([RegexMatch("(添加|删除)管理员.*")])]
    )
)
async def admin_manage(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    message_serialization = message.asSerializationString()
    message_serialization = message_serialization.replace(
        "[mirai:source:" + re.findall(r'\[mirai:source:(.*?)]', message_serialization, re.S)[0] + "]",
        ""
    )
    if re.match(r"(添加|删除)管理员.*", message_serialization):
        if member.id == configs["hostQQ"]:
            print("command get:", message_serialization)
            if re.match(r"(添加|删除)管理员(\[mirai:at:[0-9]*,]|[0-9]*)", message_serialization):
                if result := re.findall(r"管理员\[mirai:at:(.*?),]", message_serialization, re.S):
                    target = int(result[0])
                elif message_serialization[5:].isdigit():
                    target = int(message_serialization[5:])
                else:
                    try:
                        await app.sendGroupMessage(group, MessageChain.create([Plain(text="未获取到成员！检查参数！")]))
                        return None
                    except AccountMuted:
                        return None
                print(message_serialization)
                if target_member := await app.getMember(group, target):
                    try:
                        await app.sendGroupMessage(
                            group,
                            MessageChain.create([
                                Plain(text="获取到以下信息：\n"),
                                Plain(text=f"成员ID：{target_member.id}\n"),
                                Plain(text=f"成员昵称：{target_member.name}\n"),
                                Plain(text=f"成员本群权限（QQ）：{target_member.permission}\n"),
                                Plain(text=f"亲爱的你确定要{'设置他为管理员' if message_serialization[:2] == '添加' else '撤回他的管理员权限'}嘛？（是/否）")
                            ])
                        )
                    except AccountMuted:
                        return None

                    result = "否"

                    @Waiter.create_using_function([GroupMessage])
                    def waiter(
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

                    await inc.wait(waiter)

                    if result == "是":
                        try:
                            await app.sendGroupMessage(
                                group,
                                await admin_management(
                                    group.id,
                                    target,
                                    "add" if message_serialization[:2] == "添加" else "delete"
                                )
                            )
                        except AccountMuted:
                            pass
                    else:
                        try:
                            await app.sendGroupMessage(group, MessageChain.create([Plain(text="进程关闭")]))
                        except AccountMuted:
                            pass
                else:
                    try:
                        await app.sendGroupMessage(group, MessageChain.create([Plain(text=f"未在本群找到成员{target}！进程关闭")]))
                    except AccountMuted:
                        pass
        else:
            try:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create([
                        Plain(text="你不是我的主人！只有主人才可以添删管理员，难道你想篡位？！来人啊！快护驾！")
                    ])
                )
            except AccountMuted:
                pass


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Kanata([RegexMatch("(添加|删除).*关键词.*")])]))
async def keyword_manage(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    legal_config = ("setu", "real", "realHighq", "bizhi", "sketch")
    message_serialization = message.asSerializationString()
    message_serialization = message_serialization.replace(
        "[mirai:source:" + re.findall(r'\[mirai:source:(.*?)]', message_serialization, re.S)[0] + "]",
        ""
    )
    function, keyword = message_serialization[2:].split("关键词")
    function = function.strip()
    keyword = keyword.strip()
    if not function: return None
    if member.id in await get_admin(group.id):
        if function in legal_config:
            if re.match(r"\[mirai:image:{.*}\..*]", keyword):
                keyword = re.findall(r"\[mirai:image:{(.*?)}\..*]", keyword, re.S)[0]
                print(keyword)
            sql = f"SELECT function FROM keywords WHERE keyword='{keyword}'"
            if result := await execute_sql(sql):
                try:
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([
                            Plain(text=f"关键词{keyword}已被占用，具体信息：\n"),
                            Plain(text=f"{keyword} -> {result[0][0]}")
                        ])
                    )
                except AccountMuted:
                    return None
            else:
                sql = f"INSERT OR IGNORE INTO keywords (keyword, function) VALUES ('{keyword}', '{function}')"
                await execute_sql(sql)
                try:
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create([
                            Plain(text=f"关键词{keyword}添加成功！\n"),
                            Plain(text=f"{keyword} -> {function}")
                        ])
                    )
                except AccountMuted:
                    pass
        else:
            try:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create([
                        Plain(text=f"没有{function}功能哦~\n"),
                        Plain(text="目前的功能：\n"),
                        Plain(text="\n".join(legal_config))
                    ])
                )
            except AccountMuted:
                pass
    else:
        try:
            await app.sendGroupMessage(group, MessageChain.create([Plain(text="哼，你又不是管理员，我才不听你的！")]))
        except AccountMuted:
            pass


@channel.use(ListenerSchema(listening_events=[BotJoinGroupEvent]))
async def join_group_init(event: BotJoinGroupEvent):
    group_id = event.group.id
    await add_group(group_id)
