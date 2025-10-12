import sqlite3
from .connection import get_connect

def create_table():
    sql = """
		CREATE TABLE IF NOT EXISTS users(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			chat_id INTEGER UNIQUE,
			name TEXT NOT NULL,
			phone TEXT NOT NULL,
			username TEXT DEFAULT 'unknown',
			is_active INTEGER DEFAULT 1,
			is_admin INTEGER DEFAULT 0
	);

		CREATE TABLE IF NOT EXISTS books(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
      description TEXT,
			author TEXT NOT NULL,
			price INTEGER NOT NULL ,
			genre TEXT DEFAULT 'unknown',
			quantity INTEGER NOT NULL DEFAULT 0
	);

		CREATE TABLE IF NOT EXISTS orders(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
			user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
			price INTEGER NOT NULL DEFAULT 0,
			quantity INTEGER NOT NULL DEFAULT 1,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			status TEXT DEFAULT 'new'
	);
"""
    return sql

def init_database():
    """Initialize database tables"""
    try:
        with get_connect() as db:
            db.executescript(create_table())
            db.commit()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")

# Initialize database on import
init_database()

def save_users(chat_id, fullname, phone, username=None):
    try:
        with get_connect() as db:
            db.execute("""
                INSERT OR IGNORE INTO users(chat_id, name, phone, username)
                VALUES (?, ?, ?, ?)
            """, (chat_id, fullname, phone, username))
            db.commit()
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def is_register_byChatId(chat_id):
    try:
        with get_connect() as db:
            cursor = db.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking user: {e}")
        return False


def is_admin(chat_id):
    query = "SELECT is_admin FROM users WHERE chat_id = ?"
    try:
        with get_connect() as db:
            cursor = db.execute(query, (chat_id,))
            result = cursor.fetchone()
            return bool(result and result[0])
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False



def get_userInfo(chat_id):
    query = """SELECT name, phone, username, is_active
            FROM users
            WHERE chat_id = ?"""
    try:
        with get_connect() as db:
            cursor = db.execute(query, (chat_id, ))
            row = cursor.fetchone()
            if row:
                return {
                    "name": row[0],
                    "phone": row[1],
                    "username":row[2],
                    "is_active": row[3]
                }
            return None
    except Exception as e:
        print(f"Error", e)
        return None
    

def update_users(chat_id, name=None, phone=None, username=None):
    query = """
        UPDATE users
        SET name = COALESCE(?, name),
            phone = COALESCE(?, phone),
            username = COALESCE(?, username)
        WHERE chat_id = ?
        """

    try:
        with get_connect() as db:
            cursor = db.execute(query, (name, phone, username, chat_id))
            result = cursor.fetchone()
            db.commit()
            return bool(result)
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    

def user_dell_acc(chat_id):
    query = """
        UPDATE users
        SET is_active = 0
        WHERE chat_id = ?
    """
    try:
        with get_connect() as db:
            db.execute(query, (chat_id,))
            db.commit()
        return True
    except Exception as e:
        print(f"Error deactivating user: {e}")
        return False
    

def get_user_by_chat_id(chat_id):
    query = "SELECT * FROM users WHERE chat_id = ?"
    with get_connect() as db:
        cursor = db.execute(query, (chat_id,))
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        return None


def reActive(chat_id):
    query = "UPDATE users SET is_active = 1 WHERE chat_id = ?"

    try:
        with get_connect() as db:
            db.execute(query, (chat_id, ))
            db.commit()
        return True
    except Exception as e:
        print("Error", e)
        return False
    
        
