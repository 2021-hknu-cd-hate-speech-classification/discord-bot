import os
import psycopg2 as pg


class EosaDatabase:
    def __init__(self):
        self.__conn = pg.connect(host=os.environ["POSTGRES_HOSTNAME"],
                                 user=os.environ["POSTGRES_USER"],
                                 password=os.environ["POSTGRES_PASSWORD"],
                                 port=os.environ["POSTGRES_PORT"])

        cursor = self.__conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS detect_log ("
                       "    user_id BIGINT,"
                       "    guild_id BIGINT,"
                       "    chat_txt TEXT,"
                       "    score REAL"
                       ")")
        self.__conn.commit()

    def add_detect_log(self, user_id: int, guild_id: int, txt: str, score: float):
        cursor = self.__conn.cursor()
        cursor.execute("INSERT INTO detect_log(user_id, guild_id, chat_txt, score) VALUES (%s, %s, %s, %s)",
                       (user_id, guild_id, txt, score))
        self.__conn.commit()

    def get_guild_detected_log(self, guild_id: int) -> str:
        cursor = self.__conn.cursor()
        cursor.execute("SELECT user_id, chat_txt, score FROM detect_log WHERE guild_id=%s", (guild_id,))
        result = "유저 ID: 텍스트 (점수)\n============================="
        for row in cursor:
            user_id, txt, score = row
            result += f"{user_id}: {txt} ({score})\n"

        return result

    def get_user_detected_count(self, user_id: int, guild_id: int) -> str:
        cursor = self.__conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM detect_log WHERE user_id=%s AND guild_id=%s",
                       (user_id, guild_id))

        return f"{cursor.fetchone()[0]}"
