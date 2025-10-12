import sqlite3
import os
from environs import Env

env = Env()
env.read_env()

DB_PATH = "bookstore.db"

def get_connect():
   """Create and return SQLite3 database connection"""
   # Create database directory if it doesn't exist
   os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else '.', exist_ok=True)

   return sqlite3.connect(DB_PATH)

