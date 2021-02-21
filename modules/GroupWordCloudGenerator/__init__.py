from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image as IMG
from wordcloud import WordCloud, ImageColorGenerator
from dateutil.relativedelta import relativedelta
import pkuseg
import re

from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.message.elements.internal import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application.event.messages import GroupMessage
from graia.application import GraiaMiraiApplication
from graia.application.group import Group, Member
from graia.application.exceptions import AccountMuted

from .Sqlite3Manager import execute_sql

# 插件信息
__name__ = "GroupWordCloudGenerator"
__description__ = "记录聊天记录并生成个人/群组词云"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 我的月内总结/我的年内总结/本群月内总结/本群年内总结 即可"

seg = pkuseg.pkuseg()

BASE_PATH = "./modules/GroupWordCloudGenerator/"

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_wordcloud_generator(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    """
    群/个人词云生成器
    使用方法：
        群内发送 我的月内总结/我的年内总结/本群月内总结/本群年内总结 即可
    插件来源：
        SAGIRI-kawaii
    """
    message_text = message.asDisplay()
    member_id = member.id
    group_id = group.id
    await write_chat_record(seg, group_id, member_id, message_text)
    try:
        if message_text == "我的月内总结":
            await app.sendGroupMessage(group, await get_review(group_id, member_id, "month", "member"))
        elif message_text == "我的年内总结":
            await app.sendGroupMessage(group, await get_review(group_id, member_id, "year", "member"))
        elif message_text == "本群月内总结":
            await app.sendGroupMessage(group, await get_review(group_id, member_id, "month", "group"))
        elif message_text == "本群年内总结":
            await app.sendGroupMessage(group, await get_review(group_id, member_id, "year", "group"))
    except AccountMuted:
        pass


async def count_words(sp, n):
    w = {}
    for i in sp:
        if i not in w:
            w[i] = 1
        else:
            w[i] += 1
    top = sorted(w.items(), key=lambda item: (-item[1], item[0]))
    top_n = top[:n]
    return top_n


async def filter_label(label_list: list) -> list:
    """
    Filter labels

    Args:
        label_list: Words to filter

    Examples:
        result = await filter_label(label_list)

    Return:
        list
    """
    not_filter = ["草"]
    image_filter = "mirai:"
    result = []
    for i in label_list:
        if image_filter in i:
            continue
        elif i in not_filter:
            result.append(i)
        elif len(i) != 1 and i.find('nbsp') < 0:
            result.append(i)
    return result


async def write_chat_record(seg, group_id: int, member_id: int, content: str) -> None:
    content = content.replace("\\", "/")
    filter_words = re.findall(r"\[mirai:(.*?)\]", content, re.S)
    for i in filter_words:
        content = content.replace(f"[mirai:{i}]", "")
    content = content.replace("\"", " ")
    seg_result = seg.cut(content)
    seg_result = await filter_label(seg_result)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sql = f"""INSERT INTO chatRecord 
                (`time`, groupId, memberId, content, seg)
                VALUES
                (\"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\", {group_id}, {member_id}, \"{content}\",
                \"{','.join(seg_result)}\") """
    await execute_sql(sql)


async def draw_word_cloud(read_name):
    mask = np.array(IMG.open(f'{BASE_PATH}back.jpg'))
    print(mask.shape)
    wc = WordCloud(
        font_path=f'{BASE_PATH}STKAITI.TTF',
        background_color='white',
        # max_words=500,
        max_font_size=100,
        width=1920,
        height=1080,
        mask=mask
    )
    name = []
    value = []
    for t in read_name:
        name.append(t[0])
        value.append(t[1])
    for i in range(len(name)):
        name[i] = str(name[i])
        # name[i] = name[i].encode('gb2312').decode('gb2312')
    dic = dict(zip(name, value))
    print(dic)
    print(len(dic.keys()))
    wc.generate_from_frequencies(dic)
    image_colors = ImageColorGenerator(mask, default_color=(255, 255, 255))
    print(image_colors.image.shape)
    wc.recolor(color_func=image_colors)
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    # plt.imshow(wc)
    plt.axis("off")
    # plt.show()
    wc.to_file(f'{BASE_PATH}tempWordCloud.png')


async def get_review(group_id: int, member_id: int, review_type: str, target: str) -> MessageChain:
    time = datetime.now()
    year, month, day, hour, minute, second = time.strftime("%Y %m %d %H %M %S").split(" ")
    if review_type == "year":
        yearp, monthp, dayp, hourp, minutep, secondp = (time - relativedelta(years=1)).strftime("%Y %m %d %H %M %S").split(" ")
        tag = "年内"
    elif review_type == "month":
        yearp, monthp, dayp, hourp, minutep, secondp = (time - relativedelta(months=1)).strftime("%Y %m %d %H %M %S").split(" ")
        tag = "月内"
    else:
        return MessageChain.create([
                Plain(text="Error: review_type invalid!")
            ])

    sql = f"""SELECT * FROM chatRecord 
                    WHERE 
                groupId={group_id} {f'AND memberId={member_id}' if target == 'member' else ''} 
                AND time<'{year}-{month}-{day} {hour}:{minute}:{second}'
                AND time>'{yearp}-{monthp}-{dayp} {hourp}:{minutep}:{secondp}'"""
    # print(sql)
    res = await execute_sql(sql)
    texts = []
    for i in res:
        if i[4]:
            texts += i[4].split(",")
        else:
            texts.append(i[3])
    print(texts)
    top_n = await count_words(texts, 20000)
    await draw_word_cloud(top_n)
    sql = f"""SELECT count(*) FROM chatRecord 
                    WHERE 
                groupId={group_id} {f'AND memberId={member_id}' if target == 'member' else ''}  
                AND time<'{year}-{month}-{day} {hour}:{minute}:{second}'
                AND time>'{yearp}-{monthp}-{dayp} {hourp}:{minutep}:{secondp}'"""
    res = await execute_sql(sql)
    times = res[0][0]
    return MessageChain.create([
            Plain(text="记录时间：\n"),
            Plain(text=f"{yearp}-{monthp}-{dayp} {hourp}:{minutep}:{secondp}"),
            Plain(text="\n---------至---------\n"),
            Plain(text=f"{year}-{month}-{day} {hour}:{minute}:{second}"),
            Plain(text=f"\n自有记录以来，{'你' if target == 'member' else '本群'}一共发了{times}条消息\n下面是{'你的' if target == 'member' else '本群的'}{tag}词云:\n"),
            Image.fromLocalFile(f"{BASE_PATH}tempWordCloud.png")
        ])
