import re
import json
import aiohttp
from html import unescape
from PIL import Image as IMG
from io import BytesIO

from graia.application.message.elements.internal import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image

from utils import messagechain_to_img


async def get_leetcode_daily_question(language: str = "Zh") -> MessageChain:
    questionSlugData = await get_daily_question_json()
    questionSlug = questionSlugData["data"]["todayRecord"][0]["question"]["questionTitleSlug"]
    content = await get_question_content(questionSlug, language)
    content = await image_in_html2text(content)
    msg_list = []
    count = 0
    for i in content:
        if i.startswith("img["):
            # print(i.replace("img[" + re.findall(r'img\[(.*?)]', i, re.S)[0] + "]:", ""))
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=i.replace("img[" + re.findall(r'img\[(.*?)]', i, re.S)[0] + "]:", ""),
                    headers={"accept-encoding": "gzip, deflate, br"}
                ) as resp:
                    img_content = await resp.read()
                    image = IMG.open(BytesIO(img_content))
                    print(f"./modules/LeetcodeInfoCrawer/temp/tempQuestion{count}.jpg")
                    image.save(f"./modules/LeetcodeInfoCrawer/temp/tempQuestion{count}.jpg")
                    msg_list.append(Image.fromLocalFile(f"./modules/LeetcodeInfoCrawer/temp/tempQuestion{count}.jpg"))
                    count += 1
        else:
            msg_list.append(Plain(text=i))
    print(msg_list)
    return await messagechain_to_img(MessageChain.create(msg_list))


async def get_daily_question_json():
    url = "https://leetcode-cn.com/graphql/"
    headers = {
        "content-type": "application/json",
        "origin": "https://leetcode-cn.com",
        "referer": "https://leetcode-cn.com/problemset/all/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.135 Safari/537.36 "
    }
    payload = {
        "operationName": "questionOfToday",
        "variables": {},
        "query": "query questionOfToday {\n  todayRecord {\n    question {\n      questionFrontendId,"
                 "\n      questionTitleSlug,\n      __typename\n    }\n    lastSubmission {\n      id,"
                 "\n      __typename,\n    }\n    date,\n    userStatus,\n    __typename\n  }\n}\n "
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=json.dumps(payload)) as resp:
            result = await resp.json()
    return result


async def get_question_content(questionTitleSlug, language="Zh"):
    url = "https://leetcode-cn.com/graphql/"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "origin": "https://leetcode-cn.com",
        "referer": "https://leetcode-cn.com/problems/%s/" % questionTitleSlug,
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.135 Safari/537.36",
        "x-definition-name": "question",
        "x-operation-name": "questionData",
        "x-timezone": "Asia/Shanghai"
    }
    payload = {
        "operationName": "questionData",
        "variables": {"titleSlug": "%s" % questionTitleSlug},
        "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    "
                 "questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n  "
                 "  translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    "
                 "similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      "
                 "__typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      "
                 "translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      "
                 "langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n     "
                 " canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    "
                 "judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    envInfo\n    book {\n      "
                 "id\n      bookName\n      pressName\n      source\n      shortDescription\n      fullDescription\n  "
                 "    bookImgUrl\n      pressImgUrl\n      productUrl\n      __typename\n    }\n    isSubscribed\n    "
                 "isDailyQuestion\n    dailyRecordStatus\n    editorType\n    ugcQuestionId\n    style\n    "
                 "__typename\n  }\n}\n "
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=json.dumps(payload)) as resp:
            result = await resp.json()
    if language == "En":
        return result["data"]["question"]["content"]
    elif language == "Zh":
        return result["data"]["question"]["translatedContent"]
    else:
        return None


async def html2plain_text(html):
    text = re.sub('<head.*?>.*?</head>', '', html, flags=re.M | re.S | re.I)
    text = re.sub('<a\s.*?>', ' HYPERLINK ', text, flags=re.M | re.S | re.I)
    text = re.sub('<.*?>', '', text, flags=re.M | re.S)
    text = re.sub(r'(\s*\n)+', '\n', text, flags=re.M | re.S)
    return unescape(text)


async def image_in_html2text(content) -> list:
    images = re.findall(r'<img.*?src="(.*?)".*?>', content, re.S)
    for i in range(len(images)):
        content = content.replace(images[i], "/>ImAgEiMaGe%dImAgE<img" % i)
    transformed = await html2plain_text(content)
    transformed = transformed.split("ImAgE")
    index = 0
    for i in range(len(transformed)):
        if "iMaGe" in transformed[i]:
            transformed[i] = "img[%d]:%s" % (index, images[index])
            index += 1
    return transformed
