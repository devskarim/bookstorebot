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
            quantity INTEGER NOT NULL DEFAULT 0,
            image_path VARCHAR(255) DEFAULT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS cart(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL DEFAULT 1,
            price INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount INTEGER NOT NULL,
            delivery_address TEXT NOT NULL,
            payment_type VARCHAR(50) NOT NULL,
            status VARCHAR(60) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    return tables

def add_image_path_column():
    """Add image_path column to existing books table"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN image_path VARCHAR(255) DEFAULT NULL")
            conn.commit()
            print("✅ image_path column added to books table successfully!")
        else:
            print("ℹ️ image_path column already exists in books table")

        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error adding image_path column: {e}")
        return False

try:
    conn = get_connect()
    cursor = conn.cursor()
    for table_sql in create_tables():
        cursor.execute(table_sql)
    conn.commit()
    conn.close()
    print("Tables created successfully!")

    add_image_path_column()

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
        result = cursor.rowcount > 0  
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
    
