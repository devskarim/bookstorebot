from .connection import get_connect

def create_table():
    sql = """
		CREATE TABLE IF NOT EXISTS users(
			id BIGSERIAL PRIMARY KEY, 
			chat_id BIGINT UNIQUE, 
			name VARCHAR(100) NOT NULL, 
			phone VARCHAR(100) NOT NULL, 
			username VARCHAR(60) DEFAULT 'unknown',
			is_active BOOLEAN DEFAULT TRUE, 
			is_admin BOOLEAN DEFAULT FALSE
	);

		CREATE TABLE IF NOT EXISTS books(
			id BIGSERIAL PRIMARY KEY, 
			title VARCHAR(100) NOT NULL,
      description TEXT,
			author VARCHAR(100) NOT NULL, 
			price BIGINT NOT NULL ,
			genre VARCHAR(50) DEFAULT 'unknown', 
			quantity BIGINT NOT NULL DEFAULT 0
	);

		CREATE TABLE IF NOT EXISTS orders(
			id BIGSERIAL PRIMARY KEY, 
			book_id BIGINT REFERENCES books(id) ON DELETE CASCADE, 
			user_id BIGINT REFERENCES users(id) ON DELETE CASCADE, 
			price BIGINT NOT NULL DEFAULT 0, 
			quantity BIGINT NOT NULL DEFAULT 1, 
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
			status VARCHAR(60) DEFAULT 'new'
	);


"""
    return sql


with get_connect() as db: 
    with db.cursor() as dbc: 
        dbc.execute(create_table()) 
    db.commit()
create_table()

def save_users(chat_id, fullname, phone, username=None): 
    try:
        with get_connect() as db:
            with db.cursor() as dbc:
                dbc.execute("""
                    INSERT INTO users(chat_id, name, phone, username) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (chat_id) DO NOTHING
                """, (chat_id, fullname, phone, username))
            db.commit()  
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def is_register_byChatId(chat_id): 
    try: 
        with get_connect() as db:
            with db.cursor() as dbc:
                dbc.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
                return dbc.fetchone() is not None  
    except Exception as e: 
        print(f"Error checking user: {e}")
        return False


def is_admin(chat_id):
    query = "SELECT is_admin FROM users WHERE chat_id = %s"
    try:
        with get_connect() as db:
            with db.cursor() as dbc:
                dbc.execute(query, (chat_id,))
                result = dbc.fetchone()
                return bool(result and result[0])  
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False



def get_userInfo(chat_id): 
    query = """SELECT name, phone, username, is_active 
            FROM users
            WHERE chat_id = %s"""
    try: 
        with get_connect() as db: 
            with db.cursor() as dbc:
                dbc.execute(query, (chat_id, ))
                row = dbc.fetchone()
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
        SET name = COALESCE(%s, name),
            phone = COALESCE(%s, phone),
            username = COALESCE(%s, username)
        WHERE chat_id = %s
        RETURNING id

        """
    
    try: 
        with get_connect() as db:
            with db.cursor() as dbc:
                dbc.execute(query, (name, phone, username, chat_id))
                result = dbc.fetchone()
                db.commit()
                return bool(result)   
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    

def user_dell_acc(chat_id): 
    query = """
        UPDATE users
        SET is_active = false   
        WHERE chat_id = %s
    """
    try: 
        with get_connect() as db: 
            with db.cursor() as dbc: 
                dbc.execute(query, (chat_id,))
            db.commit()
        return True
    except Exception as e:
        print(f"Error deactivating user: {e}")
        return False
    

def get_user_by_chat_id(chat_id):
    query = "SELECT * FROM users WHERE chat_id = %s"
    with get_connect() as db:
        with db.cursor() as dbc:
            dbc.execute(query, (chat_id,))
            result = dbc.fetchone()
            if result:
                columns = [desc[0] for desc in dbc.description]
                return dict(zip(columns, result))
            return None


def reActive(chat_id): 
    query = " UPDATE users SET is_active = true where chat_id = %s"

    try: 
        with get_connect() as db: 
            with db.cursor() as dbc: 
                dbc.execute(query, (chat_id, ))
            db.commit()
        return True
    except Exception as e: 
        print("Error", e)
        return False 
    
        