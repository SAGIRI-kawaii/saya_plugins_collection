import sqlite3
import os


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
            self.__conn = sqlite3.connect(self.path + './modules/KeywordDetection/keywordDetection.db')
            cur = self.__conn.cursor()
            cur.execute(
                """CREATE TABLE IF NOT EXISTS `keywords` (
                      `keyword` TEXT PRIMARY KEY
                    )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS `setting` (
                      `groupId` INT PRIMARY KEY,
                      `switch` INT NOT NULL DEFAULT 0
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


manager = Sqlite3Manager()