# 一个Graia-Saya的插件仓库

这是一个存储基于 [Graia-Saya](https://github.com/GraiaProject/Saya) 的插件的仓库

如果您有这类项目，欢迎提交 Pull request 将您的项目添加到这里(注意，本仓库仅接受开源项目的仓库地址)

```diff
注意：本仓库仅提供插件存储，对插件内容并没有具体审查，请自行甄别
```

## 如何使用

本仓库中所有自带插件都在modules中

若您想单独使用，可以将其下载并放入自己的module文件夹中

若您想开箱即用，您可以直接clone整个仓库并使用 `python main.py` 命令执行本仓库自带的启动程序

注意，若使用本仓库自带启动程序，您需要先将 `configdemo.json` 文件改名为 `config.json` 并填入其中的必要信息

## 插件列表
插件名|作者|功能描述|注意事项
:--:|:--:|:--|:--
[MessagePrinter](modules/MessagePrinter.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个示例插件，输出所有收到的消息|
[WeiboHotSearch](modules/WeiboHotSearch.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|获取当前微博热搜50条|本插件依赖于本仓库下 `utils.py` 中的 `messagechain_to_img` 函数
[ZhihuHotSearch](modules/ZhihuHotSearch.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|获取当前知乎热搜50条|本插件依赖于本仓库下 `utils.py` 中的 `messagechain_to_img` 函数
[GithubHotSearch](modules/GithubHotSearch.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|获取当前github热搜25条|本插件依赖于本仓库下 `utils.py` 中的 `messagechain_to_img` 函数
[Repeater](modules/Repeater.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个复读插件|
[PetPet](modules/PetPet)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|生成摸头gif|
[PixivImageSearcher](modules/PixivImageSearcher)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个链接saucenao的以图搜图插件|请自行配置 saucenao cookie
[PdfSearcher](modules/PdfSearcher.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以搜索pdf的插件|
[NetworkCompiler](modules/NetworkCompiler.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|网络编译器（菜鸟教程）|
[Text2QrcodeGenerator](modules/Text2QrcodeGenerator.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以将文字转为二维码的插件|
[GroupWordCloudGenerator](modules/GroupWordCloudGenerator)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以记录聊天记录并生成个人/群组词云的插件|
[BilibiliBangumiSchedule](modules/BilibiliBangumiSchedule.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以获取一周内B站新番时间表的插件|
[KeywordReply](modules/KeywordReply)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个支持自定义回复的插件|
[SteamGameSearcher](modules/SteamGameSearcher)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以搜索steam游戏的插件|
[BangumiInfoSearcher](modules/BangumiInfoSearcher)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以搜索番剧信息的插件|
[PornhubStyleLogoGenerator](modules/PornhubStyleLogoGenerator)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以生成 pornhub style logo 的插件|
[AbbreviatedPrediction](modules/AbbreviatedPrediction.py)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以获取字母缩写内容的插件|
[LeetcodeInfoCrawer](modules/LeetcodeInfoCrawer)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个可以获取leetcode信息的插件|
[ImageSender](modules/ImageSender)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个图片~~(setu)~~发送插件|
[HeadSplicer](modules/HeadSplicer)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个接头霸王插件|
[WyySongOrderer](modules/WyySongOrderer)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个(全损音质x)网易云源的点歌插件|
[5000Zhao](modules/5000zhao)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个 5000兆円欲しい! style的图片生成器|
[KeywordDetection](modules/KeywordDetection)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个敏感词过滤插件（自带数据库）|
[PhantomTank](modules/PhantomTank)|[SAGIRI-kawaii](https://github.com/SAGIRI-kawaii)|一个幻影坦克生成器|
[NiBuNengXXMa](modules/NiBuNengXXMa)| [eeehhheee]([eeehhheee (github.com)](https://github.com/eeehhheee)) |生成“你能不能xxx  xx人”的表情图|安装Pillow
[BiliResolve](modules/BiliResolve)|[EnkanSakura](https://github.com/EnkanSakura)|B站视频分享解析|
[ChatBot](modules/ChatBot)|[Roc136](https://github.com/Roc136)|聊天机器人|需要自行配置所用的机器人及所需的key
[GarbageClassification](modules/GarbageClassification)|[Roc136](https://github.com/Roc136)|获取垃圾分类信息|
[KissKiss](modules/KissKiss)|[SuperWaterGod](https://github.com/SuperWaterGod)|生成头像互亲的gif|
[Weather](modules/Weather)|[Roc136](https://github.com/Roc136)|天气预报|需要自行配置`KEY`

## 其他

目前正在进行 SAGIRI-BOT 的重构工作，暂时无法更新插件，若您有好的插件或有好的想法，欢迎 Pr 或提 ISSUE
