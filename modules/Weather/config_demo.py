from string import Template

# 和风天气配置
# https://dev.qweather.com/


KEY = "1324567890abcdefg"
CITY_URL = "https://geoapi.qweather.com/v2/city/lookup"
WEATHER_URL = "https://devapi.qweather.com/v7/weather/"
TIME = {
    "当前": "now",
    "现在": "now",
    "24小时": "24h",
    "今天": "24h",
    "明天": "3d",
    "后天": "3d",
    "近三天": "3d",
    "近七天": "7d"
}
MSG_TEMPLATE = {
    "now": {
        "text": Template(
            "当前$city的天气为：\n"
            "天气状况:$text\n"
            "温度:$temp°C, 相对湿度:$humidity%, 体感温度:$feelsLike°C\n"
            "风向:$windDir, 风力:$windScale级, 风速:$windSpeed km/h\n"
            "当前小时累计降水量:$precip mm\n"
            "气压:$pressure 百帕\n"
            "能见度:$vis km\n"
            "云量:$cloud%\n"
            "观测时间:$obsTime\n"
            "数据来源:$sources\n"
            "版权:$license"
        ),
        "textcard": Template(
            "暂不支持卡片消息"
        )
    },
    "24h": {
        "text": Template(
            "未来24小时内$city的天气情况为(时间倒序):\n"
            "$hourly_data\n"
            "数据来源:$sources\n"
            "版权:$license"
        ),
        "textcard": Template(
            "暂不支持卡片消息"
        )
    },
    "3d": {
        "text": Template(
            "$time$city的天气情况为:\n"
            "$daily_data\n"
            "数据来源:$sources\n"
            "版权:$license"
        ),
        "textcard": Template(
            "暂不支持卡片消息"
        )
    },
    "7d": {
        "text": Template(
            "$time$city的天气情况为(时间倒序):\n"
            "$daily_data\n"
            "数据来源:$sources\n"
            "版权:$license"
        ),
        "textcard": Template(
            "暂不支持卡片消息"
        )
    }
}
HOURLY_DATA_TEMPLATE = Template(
    "\n"
    "时间: $fxTime\n"
    "天气状况:$text\n"
    "温度:$temp°C, 相对湿度:$humidity%\n"
    "风向:$windDir, 风力:$windScale级, 风速:$windSpeed km/h\n"
    "降水概率:$pop, 累计降水量:$precip mm\n"
    "气压:$pressure 百帕\n"
    "云量:$cloud%\n"
)
DAILY_DATA_TEMPLATE = Template(
    "\n"
    "时间: $fxDate\n"
    "温度:$tempMax°C/$tempMin°C, 相对湿度:$humidity%\n"
    "天气状况:白天$textDay, 夜间$textNight\n"
    "风向:白天$windDirDay, 夜间$windDirNight\n"
    "风力:白天$windScaleDay级, 夜间$windScaleNight级\n"
    "风速:白天$windSpeedDay km/h, 夜间$windSpeedNight km/h\n"
    "累计降水量:$precip mm\n"
    "气压:$pressure 百帕\n"
    "紫外线强度指数:$uvIndex\n"
    "能见度:$vis\n"
    "云量:$cloud%\n"
    "日出:$sunrise, 日落:$sunset\n"
    "月升:$moonrise, 月落:$moonset, 月相:$moonPhase\n"
)
SIMPLE_MSG_TEMPLATE = {
    "now": {
        "text": Template(
            "$city: $text, 温度:$temp°C, 相对湿度:$humidity%, 体感温度:$feelsLike°C\n"
            "数据来源:$sources, 版权:$license\n"
            "发送地区+时间+\"详细天气\"查看详细天气，如：北京24小时详细天气预报"
        ),
        "textcard": Template(
            "暂不支持卡片消息"
        )
    },
    "24h": {
        "text": Template(
            "未来24小时内$city的天气情况为:\n"
            "$hourly_data"
            "数据来源:$sources, 版权:$license\n"
            "发送地区+时间+\"详细天气\"查看详细天气，如：北京24小时详细天气预报"
        ),
        "textcard": Template("暂不支持卡片消息")
    },
    "3d": {
        "text": Template(
            "$time$city的天气情况为:\n"
            "$daily_data"
            "数据来源:$sources, 版权:$license\n"
            "发送地区+时间+\"详细天气\"查看详细天气，如：北京24小时详细天气预报"
        ),
        "textcard": Template("暂不支持卡片消息")
    },
    "7d": {
        "text": Template(
            "$time$city的天气情况为:\n"
            "$daily_data"
            "数据来源:$sources, 版权:$license\n"
            "发送地区+时间+\"详细天气\"查看详细天气，如：北京24小时详细天气预报"
        ),
        "textcard": Template("暂不支持卡片消息")
    }
}
SIMPLE_HOURLY_DATA_TEMPLATE = Template(
    "$fxTime: $text, 温度:$temp°C, 相对湿度:$humidity%\n"
)
SIMPLE_DAILY_DATA_TEMPLATE = Template(
    "$fxDate: 白天$textDay, 夜间$textNight, 温度:$tempMax°C/$tempMin°C, 相对湿度:$humidity%\n"
)
