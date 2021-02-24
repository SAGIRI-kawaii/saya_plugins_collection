import json
import random
import os
from itertools import chain

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image

from .Sqlite3Manager import execute_sql
from .exceptions import *


def load_config(config_file: str = "./modules/ImageSender/config.json") -> dict:
    with open(config_file, 'r', encoding='utf-8') as f:  # 从json读配置
        config = json.loads(f.read())
    return config


configs = load_config()


async def get_setting(group_id: int, setting_name: str) -> int:
    """
    Return setting from database

    Args:
        group_id: group id
        setting_name: setting name

    Examples:
        setting = get_setting(12345678, "repeat")

    Return:
        Operation result
    """
    sql = f"SELECT {setting_name} from setting WHERE groupId={group_id}"
    data = await execute_sql(sql)
    return data[0][0]


async def random_pic(base_path: str) -> str:
    """
    Return random pic path in base_dir

    Args:
        base_path: Target library path

    Examples:
        pic_path = random_pic(wallpaper_path)

    Return:
        str: Target pic path
    """
    path_dir = os.listdir(base_path)
    if not path_dir:
        raise ImagePathEmpty()
    path = random.sample(path_dir, 1)[0]
    return base_path + path


async def get_pic(image_type: str) -> MessageChain:
    """
    Return random pics message

    Args:
        image_type: The type of picture to return

    Examples:
        assist_process = await get_pic("setu")[0]
        message = await get_pic("real")[1]

    Return:
        [
            str: Auxiliary treatment to be done(Such as add statement),
            MessageChain: Message to be send(MessageChain)
        ]
    """
    async def color() -> str:
        if "setuPath" in configs.keys():
            base_path = configs["setuPath"]
        else:
            raise ConfigurationNotFound()
        pic_path = await random_pic(base_path)
        return pic_path

    async def color18() -> str:
        if "setu18Path" in configs.keys():
            base_path = configs["setu18Path"]
        else:
            raise ConfigurationNotFound()
        pic_path = await random_pic(base_path)
        return pic_path

    async def real() -> str:
        if "realPath" in configs.keys():
            base_path = configs["realPath"]
        else:
            raise ConfigurationNotFound()
        pic_path = await random_pic(base_path)
        return pic_path

    async def real_highq() -> str:
        if "realHighqPath" in configs.keys():
            base_path = configs["realHighqPath"]
        else:
            raise ConfigurationNotFound()
        pic_path = await random_pic(base_path)
        return pic_path

    async def wallpaper() -> str:
        if "wallpaperPath" in configs.keys():
            base_path = configs["wallpaperPath"]
        else:
            raise ConfigurationNotFound()
        pic_path = await random_pic(base_path)
        return pic_path

    async def sketch() -> str:
        if "sketchPath" in configs.keys():
            base_path = configs["sketchPath"]
        else:
            raise ConfigurationNotFound()
        pic_path = await random_pic(base_path)
        return pic_path

    switch = {
        "setu": color,
        "setu18": color18,
        "real": real,
        "realHighq": real_highq,
        "bizhi": wallpaper,
        "sketch": sketch
    }

    try:
        target_pic_path = await switch[image_type]()
    except ConfigurationNotFound:
        return MessageChain.create([Plain(f"{image_type}Path参数未配置!请检查配置文件！")])
    except ImagePathEmpty:
        return MessageChain.create([Plain(f"{image_type}文件夹为空!请添加图片！")])
    message = MessageChain.create([
        Image.fromLocalFile(target_pic_path)
    ])
    return message


async def check_group_data_init(group_list: list) -> None:
    sql = "select groupId from setting"
    data = await execute_sql(sql)
    group_id = list(chain.from_iterable(data))
    for i in group_list:
        # print(i.id, ':', i.name)
        if i.id not in group_id:
            sql = f"INSERT INTO setting (groupId) VALUES ({i.id})"
            await execute_sql(sql)
            sql = f"INSERT INTO admin (groupId, adminId) VALUES ({i.id}, {configs['hostQQ']})"
            await execute_sql(sql)


async def get_admin(group_id: int) -> list:
    sql = f"SELECT adminId from admin WHERE groupId={group_id}"
    data = await execute_sql(sql)
    admins = list(chain.from_iterable(data))
    return admins


async def update_setting(group_id: int, setting_name: str, new_setting_value) -> None:
    """
    Update setting to database

    Args:
        group_id: Group id
        setting_name: Setting name
        new_setting_value: New setting value

    Examples:
        await update_setting(12345678, "setu", True)

    Return:
        None
    """
    sql = f"UPDATE setting SET {setting_name}={new_setting_value} WHERE groupId={group_id}"
    await execute_sql(sql)


async def admin_management(group_id: int, member_id: int, operation: str) -> MessageChain:
    """
    Update setting to database

    Args:
        group_id: Group id
        member_id: Member id
        operation: add/delete

    Examples:
        await admin_manage(12345678, 12345678, "delete")

    Return:
        None
    """
    sql = f"SELECT * FROM admin WHERE groupId={group_id} and adminId={member_id}"
    exist = True if await execute_sql(sql) else False
    if operation == "add":
        if exist:
            return MessageChain.create([Plain(text=f"{member_id}已经是群{group_id}的管理员啦！")])
        else:
            sql = f"INSERT INTO admin (groupId, adminId) VALUES ({group_id}, {member_id})"
            await execute_sql(sql)
            return MessageChain.create([Plain(text=f"{member_id}被设置为群{group_id}的管理员啦！")])
    elif operation == "delete":
        if exist:
            sql = f"DELETE FROM admin WHERE groupId={group_id} AND adminId={member_id}"
            await execute_sql(sql)
            return MessageChain.create([Plain(text=f"{member_id}现在不是群{group_id}的管理员啦！")])
        else:
            return MessageChain.create([Plain(text=f"{member_id}本来就不是群{group_id}的管理员哦！")])
    else:
        return MessageChain.create([Plain(text=f"operation error: {operation}")])


async def add_group(group_id: int):
    sql = f"SELECT * FROM setting WHERE groupId={group_id}"
    if await execute_sql(sql):
        return None
    else:
        sql = f"INSERT INTO setting (groupId) VALUES ({group_id})"
        await execute_sql(sql)
        sql = f"INSERT INTO admin (groupId, adminId) VALUES ({group_id}, {configs['hostQQ']})"
        await execute_sql(sql)
