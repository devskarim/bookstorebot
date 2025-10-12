from .connection import get_connect

def create_tables():
    """Create all necessary tables for the bookstore application"""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(100) NOT NULL,
            username VARCHAR(60) DEFAULT 'unknown',
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            author VARCHAR(100) NOT NULL,
            price INTEGER NOT NULL,
            genre VARCHAR(50) DEFAULT 'unknown',
            quantity INTEGER NOT NULL DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            price INTEGER NOT NULL DEFAULT 0,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(60) DEFAULT 'new'
        )
        """
    ]
    return tables

# Create tables on import
try:
    conn = get_connect()
    cursor = conn.cursor()
    for table_sql in create_tables():
        cursor.execute(table_sql)
    conn.commit()
    conn.close()
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")

def save_users(chat_id, fullname, phone, username=None):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users(chat_id, name, phone, username)
            VALUES (?, ?, ?, ?)
        """, (chat_id, fullname, phone, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def is_register_byChatId(chat_id):
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error checking user: {e}")
        return False


def is_admin(chat_id):
    query = "SELECT is_admin FROM users WHERE chat_id = ?"
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(query, (chat_id,))
        result = cursor.fetchone()
        conn.close()
        return bool(result and result[0])
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False



def get_userInfo(chat_id):
    query = """SELECT name, phone, username, is_active
            FROM users
            WHERE chat_id = ?"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(query, (chat_id, ))
        row = cursor.fetchone()
        conn.close()
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
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(query, (name, phone, username, chat_id))
        conn.commit()
        result = cursor.rowcount > 0  # SQLite3 doesn't have RETURNING, so check rowcount
        conn.close()
        return bool(result)
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    

def user_dell_acc(chat_id):
    """Soft delete - deactivate user account"""
    query = """
        UPDATE users
        SET is_active = 0
        WHERE chat_id = ?
    """
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(query, (chat_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deactivating user: {e}")
        return False


    

def get_user_by_chat_id(chat_id):
    query = "SELECT * FROM users WHERE chat_id = ?"
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(query, (chat_id,))
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            user_dict = dict(zip(columns, result))
            conn.close()
            return user_dict
        conn.close()
        return None
    except Exception as e:
        print(f"Error getting user by chat_id: {e}")
        return None


def reActive(chat_id):
    query = "UPDATE users SET is_active = 1 WHERE chat_id = ?"

    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute(query, (chat_id, ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Error", e)
        return False
    
