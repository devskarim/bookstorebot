from environs import Env
from psycopg2 import connect

env = Env()
env.read_env()


def get_connect():
    return connect(
        user=env.str("DB_USER"),
        password=env.str("DB_PASSWORD"),
        database=env.str("DATABASE"),
        host=env.str("DB_HOST"),
        port=env.str("DB_PORT"),
    )

