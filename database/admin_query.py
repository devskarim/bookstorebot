from .connection import get_connect

# Book CRUD Operations

def get_books_paginated(page=1, per_page=10, search_query=None, search_type='title'):
    """Get books with pagination and optional search"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        # Build WHERE clause based on search
        where_conditions = []
        params = []

        if search_query and search_type:
            if search_type == 'title':
                where_conditions.append("title LIKE ?")
                params.append(f'%{search_query}%')
            elif search_type == 'author':
                where_conditions.append("author LIKE ?")
                params.append(f'%{search_query}%')
            elif search_type == 'genre':
                where_conditions.append("genre LIKE ?")
                params.append(f'%{search_query}%')
            else:  # Search in all fields
                where_conditions.append("(title LIKE ? OR author LIKE ? OR genre LIKE ?)")
                params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])

        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # Get total count
        count_query = f"SELECT COUNT(*) FROM books{where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Get paginated results
        data_query = f"""
            SELECT id, title, author, price, description, genre, quantity, image_path
            FROM books
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(data_query, params + [per_page, offset])

        books = cursor.fetchall()
        conn.close()

        if books:
            columns = [desc[0] for desc in cursor.description]
            books_list = [dict(zip(columns, book)) for book in books]

            total_pages = (total_count + per_page - 1) // per_page

            return {
                'books': books_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        return {
            'books': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error getting paginated books: {e}")
        return {
            'books': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }


def create_pagination_keyboard(current_page, total_pages, search_type, search_query, books):
    """Create pagination inline keyboard for Telegram"""
    try:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = []

        # Add book selection buttons (first 10 books)
        for i, book in enumerate(books[:10], 1):
            keyboard.append([InlineKeyboardButton(
                text=f"{i}. {book['title'][:30]}...",
                callback_data=f"select_book_{i}_{current_page}_{search_type}_{search_query}"
            )])

        # Add pagination controls
        nav_buttons = []

        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"prev_{current_page - 1}_{search_type}_{search_query}"
            ))

        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"next_{current_page + 1}_{search_type}_{search_query}"
            ))

        if nav_buttons:
            keyboard.append(nav_buttons)

        # Add back to search button
        keyboard.append([InlineKeyboardButton(
            text="🔍 Qidirishga qaytish",
            callback_data="back_to_search"
        )])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    except Exception as e:
        print(f"Error creating pagination keyboard: {e}")
        return None


# Cart Management Functions

def add_to_cart(user_id, book_id, quantity, price):
    """Add book to user's cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Check if item already exists in cart
        cursor.execute("""
            SELECT id, quantity FROM cart
            WHERE user_id = ? AND book_id = ?
        """, (user_id, book_id))

        existing_item = cursor.fetchone()

        if existing_item:
            item_id, existing_quantity = existing_item
            new_quantity = existing_quantity + quantity
            cursor.execute("""
                UPDATE cart
                SET quantity = ?, price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_quantity, price, item_id))
        else:
            cursor.execute("""
                INSERT INTO cart (user_id, book_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (user_id, book_id, quantity, price))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return False


def get_user_cart(user_id):
    """Get all items in user's cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.quantity, c.price, c.created_at,
                   b.id as book_id, b.title, b.author, b.genre, b.image_path
            FROM cart c
            JOIN books b ON c.book_id = b.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        """, (user_id,))

        cart_items = cursor.fetchall()
        conn.close()

        if cart_items:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, item)) for item in cart_items]
        return []
    except Exception as e:
        print(f"Error getting user cart: {e}")
        return []


def remove_from_cart(user_id, book_id=None, cart_item_id=None):
    """Remove item from cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        if cart_item_id:
            cursor.execute("DELETE FROM cart WHERE id = ?", (cart_item_id,))
        elif book_id:
            cursor.execute("DELETE FROM cart WHERE user_id = ? AND book_id = ?", (user_id, book_id))
        else:
            # Remove all items for user
            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return False


def clear_user_cart(user_id):
    """Clear all items from user's cart"""
    return remove_from_cart(user_id)


# Order Management Functions

def create_order(user_id, delivery_address, payment_type, total_amount, book_id=None, quantity=None, price=None):
    """Create a new order"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Insert order
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, delivery_address, payment_type)
            VALUES (?, ?, ?, ?)
        """, (user_id, total_amount, delivery_address, payment_type))

        order_id = cursor.lastrowid

        if book_id and quantity and price:
            # Add single book order item
            cursor.execute("""
                INSERT INTO order_items (order_id, book_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, book_id, quantity, price))

        conn.commit()
        conn.close()
        return order_id
    except Exception as e:
        print(f"Error creating order: {e}")
        return None


def get_user_orders(user_id, page=1, per_page=5):
    """Get user's orders with pagination"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))
        total_count = cursor.fetchone()[0]

        # Get paginated orders
        cursor.execute("""
            SELECT id, total_amount, delivery_address, payment_type, status, created_at
            FROM orders
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, per_page, offset))

        orders = cursor.fetchall()

        total_pages = (total_count + per_page - 1) // per_page

        if orders:
            columns = [desc[0] for desc in cursor.description]
            orders_list = [dict(zip(columns, order)) for order in orders]

            return {
                'orders': orders_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        return {
            'orders': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error getting user orders: {e}")
        return {
            'orders': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }
    finally:
        conn.close()


def get_order_details(order_id):
    """Get detailed information about an order"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Get order info
        cursor.execute("""
            SELECT o.id, o.total_amount, o.delivery_address, o.payment_type, o.status, o.created_at,
                   u.name, u.phone
            FROM orders o
            JOIN users u ON o.user_id = u.chat_id
            WHERE o.id = ?
        """, (order_id,))

        order = cursor.fetchone()

        if not order:
            conn.close()
            return None

        order_columns = [desc[0] for desc in cursor.description]
        order_info = dict(zip(order_columns, order))

        # Get order items
        cursor.execute("""
            SELECT oi.quantity, oi.price, b.title, b.author, b.genre
            FROM order_items oi
            JOIN books b ON oi.book_id = b.id
            WHERE oi.order_id = ?
        """, (order_id,))

        items = cursor.fetchall()
        conn.close()

        if items:
            item_columns = [desc[0] for desc in cursor.description]
            order_info['items'] = [dict(zip(item_columns, item)) for item in items]
        else:
            order_info['items'] = []

        return order_info
    except Exception as e:
        print(f"Error getting order details: {e}")
        return None


def add_order_items(order_id, cart_items):
    """Add multiple items to order from cart data"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, book_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item.get('book_id') or item.get('id'), item.get('quantity', 1), item.get('price', 0)))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Error adding order items: {e}")
        return False

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