import asyncio
from .Sqlite3Manager import execute_sql

FILE_PATH = ""


class KeywordAppender:
    """
    注意文件格式应为用 \n 分隔的关键词
    如：
        测试1
        测试2
        测试3
    """
    @staticmethod
    async def append(file_path: str):
        with open(file_path, "r") as r:
            keywords = r.read().split("\n")
        for keyword in keywords:
            sql = f"INSERT INTO filterKeywords (`keyword`) VALUES ('{keyword}')"
            await execute_sql(sql)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(KeywordAppender.append(FILE_PATH))
