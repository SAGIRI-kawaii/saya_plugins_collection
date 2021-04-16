import json
from lxml import etree

from graia.application import GraiaMiraiApplication
from graia.application.event.messages import GroupMessage, Group
from graia.application.exceptions import AccountMuted
from graia.application.message.chain import MessageChain
from graia.application.message.elements import internal as Msg_element
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema

from .utils import get_config, gen_video_info_dict


# 插件信息
__name__ = "BiliResolve"
__description__ = "解析B站视频分享链接"
__author__ = "EnkanSakura"
__usage__ = "在群内分享B站视频即可"


saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}\n使用方法：{__usage__}")
channel.author(__author__)

config = get_config()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def bili_resolve(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group
):
    # print(config)
    if group.id not in config['group'] or not config:
        return None
    url = ''
    # print(group.id)
    if Msg_element.App in message:
        json_msg = json.loads(message.get(Msg_element.App)[0].content)
        try:
            desc = json_msg['desc']
        except KeyError:
            pass
        else:
            if desc == '哔哩哔哩':
                url = json_msg['meta']['detail_1']['qqdocurl']
            elif desc == '新闻':
                try:
                    tag = json_msg['meta']['news']['tag']
                except KeyError:
                    pass
                else:
                    url = json_msg['meta']['news']['jumpUrl']
                    # print('receive App\turl=', url)
    elif Msg_element.Xml in message:
        xml_msg = etree.fromstring(
            message.get(Msg_element.Xml)[0].xml.encode('utf-8')
        )
        try:
            url = xml_msg.xpath('/msg/@url')[0]
        except IndexError:
            pass
        else:
            pass
            # print('receive Xml\turl=', url)
    else:
        try:
            url = message.get(Msg_element.Plain)[0]
        except IndexError:
            pass
        else:
            url = url.to_string()
        # print(message)
    if url.find('https://') != -1:
        if video_info := gen_video_info_dict(url):
            await app.sendGroupMessage(
                group=group,
                message=MessageChain.create([
                    Msg_element.Image.fromNetworkAddress(video_info['image']),
                    Msg_element.Plain(video_info['plain'])
                ])
            )
