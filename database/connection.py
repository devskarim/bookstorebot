import sqlite3
import os
from environs import Env

env = Env()
env.read_env()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'app.db')
DB_PATH = os.path.abspath(DB_PATH) 

if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connect():
    return sqlite3.connect(DB_PATH)
