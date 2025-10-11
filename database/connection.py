import sqlite3
import os
from environs import Env

env = Env()
env.read_env()


def get_connect():
   # Create data directory if it doesn't exist
   os.makedirs('data', exist_ok=True)

   # Use environment variable for database path, default to data/app.db
   db_path = env.str("DATABASE_PATH", "data/app.db")

   return sqlite3.connect(db_path)

