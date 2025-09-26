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
      
create_table()