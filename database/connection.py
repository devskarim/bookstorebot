import sqlite3
import os
from environs import Env

env = Env()
env.read_env()


def get_connect():
   os.makedirs('data', exist_ok=True)

   db_path = env.str("DATABASE_PATH", "data/app.sqlite3")

   return sqlite3.connect(db_path)

