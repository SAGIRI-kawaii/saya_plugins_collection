from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import RegexMatch
from graia.application import GraiaMiraiApplication
from graia.application.message.elements.internal import Plain, At, Image, Voice
from graia.application import session
from graia.application.message.elements.internal import MessageChain
import re
import requests
from lxml import etree


# 插件信息
__name__ = "GarbageClassification"
__description__ = "查询某个城市对某种物品的垃圾分类"
__author__ = "Roc"
__usage__ = "发送 \"垃圾分类 物品 城市\"即可"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

headers={
    "User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language" : "en-us",
    "Connection" : "keep-alive",
    "Accept-Charset" : "GB2312,utf-8;q=0.7,*;q=0.7"
}
CITYS = ["北京", "天津", "上海", "重庆", "石家庄", "邯郸", "太原", "呼和浩特", "沈阳",
"大连", "长春", "哈尔滨", "南京", "苏州", "杭州", "宁波", "合肥", "铜陵", "福州",
"厦门", "南昌", "宜春", "郑州", "济南", "泰安", "青岛", "武汉", "长沙", "宜昌",
"广州", "深圳", "南宁", "海口", "成都", "广元", "德阳", "贵阳", "昆明", "拉萨",
"日喀则", "西安", "咸阳", "兰州", "西宁", "银川", "乌鲁木齐"]


def getclassify(thing, city):
    response = ' '
    img_path = None
    if city in CITYS:
        html = requests.get(f"https://lajifenleiapp.com/sk/{ thing }?l={ city }", headers=headers)
        selector = etree.HTML(html.text)
        try:
            kind = selector.xpath("/html/body/div[1]/div[7]/div/div[1]/h1/span[3]")[0]
            response += f"{ thing }在{ city }属于{ kind.text }"
            img_url = selector.xpath("/html/body/div[1]/div[7]/div/div[3]/img/@src")[0]
            try:
                img_res = requests.get(img_url, headers=headers)
                img_path = './modules/GarbageClassification/img.jpg'
                with open(img_path, 'wb') as f:
                    f.write(img_res.content)
            except Exception as e:
                print("img error:", e)
        except:
            response += f"没有找到{ thing }在{ city }的分类信息！"
    else:
        response += f"暂不支持当前城市，支持的城市列表：{ ', '.join(CITYS) }"
    return response, img_path


@channel.use(ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Kanata([RegexMatch('垃圾分类 .*')])]))
async def group_message_listener(app:GraiaMiraiApplication, message: MessageChain, member: Member, group: Group):
    re_res = re.search(r'垃圾分类\ (.+?)[ ,，/|\*&](.+)', message.asDisplay())
    print(re_res)
    if re_res:
        thing = re_res.group(1)
        city = re_res.group(2)
        # print(thing, city)
        reply, img_path = getclassify(thing, city)
        if img_path is not None:
            msg = MessageChain.create([At(member.id), Plain(reply), Image.fromLocalFile(img_path)])
        else:
            msg = MessageChain.create([At(member.id), Plain(reply)])
        try:
            await app.sendGroupMessage(
                group, msg
            )
        except AccountMuted:
            pass
