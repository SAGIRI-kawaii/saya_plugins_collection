from .Sqlite3Manager import Sqlite3Manager


class DFAUtils:
    __filter_words_dict = {}
    __skip_char = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', '%', '?', '？', '<', '>', "《", '》', '-', '_']

    def __init__(self):
        keywords = self.__get_words()
        for keyword in keywords:
            self.add_keyword(keyword[0])
        # print(self.__filter_words_dict)

    def filter_judge(self, text: str) -> list:
        words = []
        for i in range(len(text)):
            length = self.check(text, i)
            if length > 0:
                words.append(text[i:i + length])
        return words

    def check(self, text: str, begin_index: int) -> int:
        flag = False
        match_flag_length = 0
        node = self.__filter_words_dict
        tmp_flag = 0
        for i in range(begin_index, len(text)):
            char = text[i]
            if char in self.__skip_char:
                tmp_flag += 1
                continue
            node = node.get(char)
            if node:
                match_flag_length += 1
                tmp_flag += 1
                if node.get("is_end"):
                    flag = True
            else:
                break
        if tmp_flag < 2 or not flag:
            tmp_flag = 0
        return tmp_flag

    def add_keyword(self, keyword: str):
        node = self.__filter_words_dict
        for i in range(len(keyword)):
            char = keyword[i]
            if char in node.keys():
                node = node.get(char)
                node["is_end"] = False
            else:
                node[char] = {"is_end": True if i == len(keyword) - 1 else False}
                node = node[char]

    def replace_filter_word(self, text: str) -> str:
        filter_words = self.filter_judge(text)
        for word in filter_words:
            text = text.replace(word, "*" * len(word))
        return text

    def __get_words(self) -> tuple:
        conn = Sqlite3Manager.get_instance().get_conn()
        cursor = conn.cursor()
        sql = f"SELECT keyword FROM keywords"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
