from .connection import get_connect

# Book CRUD Operations

def add_book(title, author, price, description=None, genre=None, quantity=0):
    """Add a new book to the database"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO books (title, author, price, description, genre, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, author, price, description, genre, quantity))
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return book_id
    except Exception as e:
        print(f"Error adding book: {e}")
        return None

def get_all_books():
    """Get all books from database"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, author, price, description, genre, quantity
            FROM books
            ORDER BY id DESC
        """)
        books = cursor.fetchall()
        conn.close()

        if books:
            columns = [desc[0] for desc in cursor.description]
            books_list = [dict(zip(columns, book)) for book in books]
            return books_list
        return []
    except Exception as e:
        print(f"Error getting books: {e}")
        return []

def get_book_by_id(book_id):
    """Get a specific book by ID"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, author, price, description, genre, quantity
            FROM books
            WHERE id = ?
        """, (book_id,))
        book = cursor.fetchone()
        conn.close()

        if book:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, book))
        return None
    except Exception as e:
        print(f"Error getting book by ID: {e}")
        return None

def update_book(book_id, title=None, author=None, price=None, description=None, genre=None, quantity=None):
    """Update book information"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Build dynamic update query
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if author is not None:
            updates.append("author = ?")
            params.append(author)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if genre is not None:
            updates.append("genre = ?")
            params.append(genre)
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)

        if not updates:
            return False

        params.append(book_id)
        query = f"""
            UPDATE books
            SET {', '.join(updates)}
            WHERE id = ?
        """

        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error updating book: {e}")
        return False

def delete_book(book_id):
    """Delete a book from database"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error deleting book: {e}")
        return False

def search_books(search_term):
    """Search books by title or author"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, author, price, description, genre, quantity
            FROM books
            WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
            ORDER BY id DESC
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        books = cursor.fetchall()
        conn.close()

        if books:
            columns = [desc[0] for desc in cursor.description]
            books_list = [dict(zip(columns, book)) for book in books]
            return books_list
        return []
    except Exception as e:
        print(f"Error searching books: {e}")
        return []

def get_books_by_genre(genre):
    """Get books by genre"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, author, price, description, genre, quantity
            FROM books
            WHERE genre = ?
            ORDER BY id DESC
        """, (genre,))
        books = cursor.fetchall()
        conn.close()

        if books:
            columns = [desc[0] for desc in cursor.description]
            books_list = [dict(zip(columns, book)) for book in books]
            return books_list
        return []
    except Exception as e:
        print(f"Error getting books by genre: {e}")
        return []

def get_book_stats():
    """Get book statistics for admin dashboard"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Total books
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]

        # Total quantity
        cursor.execute("SELECT SUM(quantity) FROM books")
        total_quantity = cursor.fetchone()[0] or 0

        # Average price
        cursor.execute("SELECT AVG(price) FROM books")
        avg_price = cursor.fetchone()[0] or 0

        # Unique genres
        cursor.execute("SELECT COUNT(DISTINCT genre) FROM books WHERE genre != 'unknown'")
        unique_genres = cursor.fetchone()[0]

        conn.close()

        return {
            'total_books': total_books,
            'total_quantity': total_quantity,
            'average_price': round(avg_price, 2),
            'unique_genres': unique_genres
        }
    except Exception as e:
        print(f"Error getting book stats: {e}")
        return None

def update_book_quantity(book_id, new_quantity):
    """Update book quantity (for inventory management)"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE books
            SET quantity = ?
            WHERE id = ?
        """, (new_quantity, book_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error updating book quantity: {e}")
        return False