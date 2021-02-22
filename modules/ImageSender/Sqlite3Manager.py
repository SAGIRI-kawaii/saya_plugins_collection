import sqlite3
import os


keywords_init_sql = [
    "INSERT OR IGNORE INTO keywords (keyword, function) VALUES ('setu', 'setu')",
    "INSERT OR IGNORE INTO keywords (keyword, function) VALUES ('real', 'real')",
    "INSERT OR IGNORE INTO keywords (keyword, function) VALUES ('rhq', 'realHighq')",
    "INSERT OR IGNORE INTO keywords (keyword, function) VALUES ('bizhi', 'bizhi')",
    "INSERT OR IGNORE INTO keywords (keyword, function) VALUES ('sketch', 'sketch')",
]


class Sqlite3Manager:
    __instance = None
    __first_init: bool = False
    path: str = None
    __conn = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__first_init:
            self.path = os.getcwd()
            self.__conn = sqlite3.connect(self.path + './modules/ImageSender/imageSenderInfo.db')
            cur = self.__conn.cursor()
            cur.execute(
                """CREATE TABLE IF NOT EXISTS `setting` (
                      `groupId` INT NOT NULL,
                      `setu` INT NOT NULL DEFAULT 0,
                      `setu18` INT NOT NULL DEFAULT 0,
                      `real` INT NOT NULL DEFAULT 0,
                      `realHighq` INT NOT NULL DEFAULT 0,
                      `bizhi` INT NOT NULL DEFAULT 0,
                      `sketch` INT NOT NULL DEFAULT 0
                    )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS `keywords` (
                      `keyword` TEXT PRIMARY KEY,
                      `function` TEXT NOT NULL
                    )"""
            )
            for sql in keywords_init_sql:
                cur.execute(sql)
            cur.execute(
                """CREATE TABLE IF NOT EXISTS `admin` (
                      `groupId` INT NOT NULL,
                      `adminId` INT NOT NULL
                    )"""
            )
            self.__conn.commit()

            Sqlite3Manager.__first_init = True
        else:
            raise ValueError("Sqlite3Manager already initialized!")

    @classmethod
    def get_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise ValueError("Sqlite3Manager not initialized!")

    @classmethod
    def get_connection(cls):
        if cls.__conn:
            return cls.__conn
        else:
            raise ValueError("Sqlite3Manager not initialized!")

    def get_conn(self):
        if self.__conn:
            return self.__conn
        else:
            raise ValueError("Sqlite3Manager not initialized!")

    def execute(self, sql: str):
        if sql.lower().startswith("select"):
            cur = self.__conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            return result
        else:
            cur = self.__conn.cursor()
            cur.execute(sql)
            self.__conn.commit()
            cur.close()
            return


manager = Sqlite3Manager()


async def execute_sql(sql: str):
    instance = Sqlite3Manager.get_instance()
    return instance.execute(sql)
