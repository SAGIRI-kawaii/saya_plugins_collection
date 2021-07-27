import requests
import json
import re
from .config import *

# 和风天气

def get_city_id(city: str):
    id = '0'
    params = {
        "key": KEY,
        "location": city
    }
    response = requests.get(CITY_URL, params=params)
    if response.status_code == 200:
        results = json.loads(response.text)
        if results['code'] == '200':
            # print(results['location'])
            id = results['location'][0]['id']
            city = results['location'][0]['country'] + \
                results['location'][0]['adm1']
            if not results['location'][0]['adm1'].startswith(results['location'][0]['adm2']):
                city += results['location'][0]['adm2'] + '市'
                if not results['location'][0]['adm2'].startswith(results['location'][0]['name']):
                    city += results['location'][0]['name'] + '区'
    # print(city, id)
    return city, id


def get_weather(city, time, simple_flag=1, msg_type='text'):
    if simple_flag:
        msg_template = SIMPLE_MSG_TEMPLATE
        hourly_data_template = SIMPLE_HOURLY_DATA_TEMPLATE
        daily_data_template = SIMPLE_DAILY_DATA_TEMPLATE
    else:
        msg_template = MSG_TEMPLATE
        hourly_data_template = HOURLY_DATA_TEMPLATE
        daily_data_template = DAILY_DATA_TEMPLATE
    # 检查并标准化参数
    city, city_id = get_city_id(city)
    time_s = time
    if time in TIME.keys():
        time = TIME[time]
    elif time in TIME.values():
        pass
    else:
        return f"支持的时间：{ ','.join([*TIME.keys(), *set(TIME.values())]) }, 试试换一种说法~"
    if city_id == '0':
        return f"找不到城市{ city }，换一种说法试试呢~"
    params = {
        "key": KEY,
        "location": city_id
    }

    response = requests.get(WEATHER_URL + time, params=params)
    if response.status_code == 200:
        results = json.loads(response.text)
        # print(results)
        if results['code'] == '200':
            # 根据查询天气的不同构建不同的数据结构
            if time == 'now':  # 当前天气
                results['now']['obsTime'] = results['now']['obsTime'][11:16]
                data = {
                    "city": city,
                    **results['now']
                }
                # print(data)
            elif time in ["24h"]:  # 逐小时天气， 72h, 168h 需要商业版
                data = {
                    "city": city,
                    "hourly_data": ""
                }
                for d in results['hourly']:
                    d['fxTime'] = d['fxTime'][11:16]
                    d['pop'] = d['pop'] + "%" if d['pop'] else "不详"
                    if simple_flag:
                        data['hourly_data'] += hourly_data_template.substitute(d)
                    else:
                        data['hourly_data'] = hourly_data_template.substitute(d) + data['hourly_data']
                # print(data)
            elif time in ["3d", "7d"]:
                data = {
                    "city": city,
                    "time": time_s,
                    "daily_data": ""
                }
                time2index = {
                    "今天": 0,
                    "明天": 1,
                    "后天": 2
                }
                if time_s in time2index.keys():
                    d = results['daily'][time2index[time_s]]
                    d['fxDate'] = d['fxDate'][5:10]
                    if simple_flag:
                        data['daily_data'] += daily_data_template.substitute(d)
                    else:
                        data['daily_data'] = daily_data_template.substitute(d) + data['daily_data']
                else:
                    for d in results['daily']:
                        d['fxDate'] = d['fxDate'][5:10]
                        if simple_flag:
                            data['daily_data'] += daily_data_template.substitute(d)
                        else:
                            data['daily_data'] = daily_data_template.substitute(d) + data['daily_data']
                # print(data)
            else:  # 不支持的查询
                return 'time error'

            # 添加来源和版权
            if len(results['refer']['sources']) > 0:
                data["sources"] = ','.join(results['refer']['sources'])
            else:
                data['sources'] = '未知来源'
            if len(results['refer']['license']) > 0:
                data["license"] = ','.join(results['refer']['license'])
            else:
                data['license'] = '未知版权'

            # 生成msg文本
            if time in msg_template.keys():
                if msg_type in msg_template[time].keys():
                    msg = msg_template[time][msg_type].substitute(data)
                else:
                    msg = 'msg_type error'
            else:
                msg = 'time error'
            return msg
        else:
            return "请求错误" + results['code']
    else:
        return "网络错误"


def text2params(text:str):
    city, time, flag = ('', '', 1)
    if '详细' in text:
        flag = 0
    res = re.match(f"(.*?)({ '|'.join([*TIME.keys(), *set(TIME.values())]) })(详细|)天气预报", text, re.I)
    if res:
        city = res.group(1)
        time = res.group(2)
    print(city, time, flag)
    return city, time, flag


if __name__ == "__main__":
    city, time, flag = text2params("北京近七天天气预报")
    print(get_weather(city, time, flag))