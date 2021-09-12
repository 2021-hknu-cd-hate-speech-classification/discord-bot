import os
import psycopg2 as pg


class EosaDatabase:
    def __init__(self):
        self.__conn = pg.connect(host=os.environ["POSTGRES_HOSTNAME"],
                                 user=os.environ["POSTGRES_USER"],
                                 password=os.environ["POSTGRES_PASSWORD"],
                                 port=os.environ["POSTGRES_PORT"],
                                 database="eosa")

    def user_append(self, guild_id: int, user_id: int):
        raise NotImplementedError
