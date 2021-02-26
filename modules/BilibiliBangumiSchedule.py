# -*- coding: utf-8 -*-
import aiohttp
import datetime

from graia.application.message.elements.internal import Plain
from graia.application import GraiaMiraiApplication
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application.exceptions import AccountMuted

from utils import messagechain_to_img

# 插件信息
__name__ = "BilibiliBangumiSchedule"
__description__ = "获取一周内B站新番时间表"
__author__ = "SAGIRI-kawaii"
__usage__ = "在群内发送 [1-7]日内新番 即可"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('[1-7]日内新番')])]))
async def bilibili_bangumi_schedule(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    days = message.asDisplay()[0]
    try:
        await app.sendGroupMessage(group, await formatted_output_bangumi(int(days)))
    except AccountMuted:
        pass


async def get_new_bangumi_json() -> dict:
    """
    Get json data from bilibili

    Args:

    Examples:
        data = await get_new_bangumi_json()

    Return:
        dict:data get from bilibili
    """
    url = "https://bangumi.bilibili.com/web_api/timeline_global"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://www.bilibili.com",
        "referer": "https://www.bilibili.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers) as resp:
            result = await resp.json()
    return result


async def get_formatted_new_bangumi_json() -> list:
    """
    Format the json data

    Args:

    Examples:
        data = get_formatted_new_bangumi_json()

    Returns:
        {
            "title": str,
            "cover": str,
            "pub_index": str,
            "pub_time": str,
            "url": str
        }
    """
    all_bangumi_data = await get_new_bangumi_json()
    all_bangumi_data = all_bangumi_data["result"][-7:]
    formatted_bangumi_data = list()

    for bangumi_data in all_bangumi_data:
        temp_bangumi_data_list = list()
        for data in bangumi_data["seasons"]:
            temp_bangumi_data_dict = dict()
            temp_bangumi_data_dict["title"] = data["title"]
            temp_bangumi_data_dict["cover"] = data["cover"]
            temp_bangumi_data_dict["pub_index"] = data["pub_index"]
            temp_bangumi_data_dict["pub_time"] = data["pub_time"]
            temp_bangumi_data_dict["url"] = data["url"]
            temp_bangumi_data_list.append(temp_bangumi_data_dict)
        formatted_bangumi_data.append(temp_bangumi_data_list)

    return formatted_bangumi_data


async def formatted_output_bangumi(days: int) -> MessageChain:
    """
    Formatted output json data

    Args:
        days: The number of days to output(1-7)

    Examples:
        data_str = formatted_output_bangumi(7)

    Return:
        MessageChain
    """
    formatted_bangumi_data = await get_formatted_new_bangumi_json()
    temp_output_substring = ["------BANGUMI------\n\n"]
    now = datetime.datetime.now()
    for index in range(days):
        temp_output_substring.append(now.strftime("%m-%d"))
        temp_output_substring.append("即将播出：")
        for data in formatted_bangumi_data[index]:
            temp_output_substring.append("\n%s %s %s\n" % (data["pub_time"], data["title"], data["pub_index"]))
            # temp_output_substring.append("url:%s\n" % (data["url"]))
        temp_output_substring.append("\n\n----------------\n\n")
        now += datetime.timedelta(days=1)

    content = "".join(temp_output_substring)
    return await messagechain_to_img(MessageChain.create([Plain(text=content)]))
