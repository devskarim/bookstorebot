from .connection import get_connect
import os
import uuid

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. PDF generation will not work.")

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    print("pdfkit not installed. Alternative PDF generation not available.")

def add_book(title, description, author, price, genre, quantity, image_path=None):
    """Add a new book to the database"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' in columns:
            cursor.execute("""
                INSERT INTO books (title, description, author, price, genre, quantity, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, author, price, genre, quantity, image_path))
        else:
            cursor.execute("""
                INSERT INTO books (title, description, author, price, genre, quantity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, author, price, genre, quantity))

        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return book_id
    except Exception as e:
        print(f"Error adding book: {e}")
        return None

def get_all_books():
    """Get all books from the database"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' in columns:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity, image_path
                FROM books
                ORDER BY id
            """)
        else:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity
                FROM books
                ORDER BY id
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

        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' in columns:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity, image_path
                FROM books
                WHERE id = ?
            """, (book_id,))
        else:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity
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

def delete_book(book_id):
    """Delete a book from the database"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        print(f"Error deleting book: {e}")
        return False

def update_book(book_id, title=None, description=None, author=None, price=None, genre=None, quantity=None):
   """Update book information"""
   try:
       conn = get_connect()
       cursor = conn.cursor()

       updates = []
       params = []

       if title is not None:
           updates.append("title = ?")
           params.append(title)
       if description is not None:
           updates.append("description = ?")
           params.append(description)
       if author is not None:
           updates.append("author = ?")
           params.append(author)
       if price is not None:
           updates.append("price = ?")
           params.append(price)
       if genre is not None:
           updates.append("genre = ?")
           params.append(genre)
       if quantity is not None:
           updates.append("quantity = ?")
           params.append(quantity)

       if updates:
           params.append(book_id)
           query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
           cursor.execute(query, params)
           conn.commit()
           updated = cursor.rowcount > 0
           conn.close()
           return updated
       return False
   except Exception as e:
       print(f"Error updating book: {e}")
       return False

def search_books(query):
    """Search books by title or author"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        clean_query = query.strip().lower()

        if 'image_path' in columns:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity, image_path
                FROM books
                WHERE LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?) OR LOWER(genre) LIKE LOWER(?)
                ORDER BY id
            """, (f'%{clean_query}%', f'%{clean_query}%', f'%{clean_query}%'))
        else:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity
                FROM books
                WHERE LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?) OR LOWER(genre) LIKE LOWER(?)
                ORDER BY id
            """, (f'%{clean_query}%', f'%{clean_query}%', f'%{clean_query}%'))

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


async def save_image_from_telegram(bot, file_id, destination_dir="imgs/books/"):
    """Download and save image from Telegram to local directory"""
    try:
        os.makedirs(destination_dir, exist_ok=True)

        file_info = await bot.get_file(file_id)

        file_extension = os.path.splitext(file_info.file_path)[1] if '.' in file_info.file_path else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        full_path = os.path.join(destination_dir, unique_filename)

        await bot.download_file(file_info.file_path, full_path)

        return full_path
    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def generate_books_pdf(books, filename="barcha_kitoblar.pdf"):
    """Generate PDF with all books information"""
    if not REPORTLAB_AVAILABLE:
        print("ReportLab not available. Cannot generate PDF.")
        return None

    try:
        pdf_dir = "pdf_reports/"
        os.makedirs(pdf_dir, exist_ok=True)

        pdf_path = os.path.join(pdf_dir, filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = styles['Heading1']
        title = Paragraph("📚 Barcha Kitoblar Ro'yxati", title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        table_data = [["ID", "Nomi", "Muallifi", "Narxi", "Janri", "Miqdori"]]

        for book in books:
            table_data.append([
                str(book['id']),
                book['title'],
                book['author'],
                f"{book['price']} so'm",
                book['genre'],
                str(book['quantity'])
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)

        doc.build(story)

        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def generate_books_pdf_pdfkit(books, filename="barcha_kitoblar.pdf"):
    """Generate PDF with all books information using pdfkit"""
    if not PDFKIT_AVAILABLE:
        print("pdfkit not available. Cannot generate PDF.")
        return None

    try:
        pdf_dir = "pdf_reports/"
        os.makedirs(pdf_dir, exist_ok=True)

        pdf_path = os.path.join(pdf_dir, filename)

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Barcha Kitoblar</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; text-align: center; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                th { background-color: #f2f2f2; font-weight: bold; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .book-id { background-color: #e7f3ff; }
            </style>
        </head>
        <body>
            <h1>📚 Barcha Kitoblar Ro'yxati</h1>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nomi</th>
                        <th>Muallifi</th>
                        <th>Narxi</th>
                        <th>Janri</th>
                        <th>Miqdori</th>
                    </tr>
                </thead>
                <tbody>
        """

        for book in books:
            html_content += f"""
                    <tr>
                        <td class="book-id">{book['id']}</td>
                        <td>{book['title']}</td>
                        <td>{book['author']}</td>
                        <td>{book['price']:,} so'm</td>
                        <td>{book['genre']}</td>
                        <td>{book['quantity']}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        pdfkit.from_string(html_content, pdf_path)

        return pdf_path
    except Exception as e:
        print(f"Error generating PDF with pdfkit: {e}")
        return None


def get_books_paginated(page=1, per_page=10, search_query=None, search_type=None):
    """Get books with pagination and optional search"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' in columns:
            select_query = """
                SELECT id, title, description, author, price, genre, quantity, image_path
                FROM books
            """
        else:
            select_query = """
                SELECT id, title, description, author, price, genre, quantity
                FROM books
            """

        if search_query and search_type:
            clean_query = search_query.strip().lower()

            if search_type == 'title':
                select_query += " WHERE LOWER(title) LIKE LOWER(?)"
                params = (f'%{clean_query}%',)
            elif search_type == 'author':
                select_query += " WHERE LOWER(author) LIKE LOWER(?)"
                params = (f'%{clean_query}%',)
            elif search_type == 'genre':
                select_query += " WHERE LOWER(genre) LIKE LOWER(?)"
                params = (f'%{clean_query}%',)
            else:
                select_query += " WHERE LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?) OR LOWER(genre) LIKE LOWER(?)"
                params = (f'%{clean_query}%', f'%{clean_query}%', f'%{clean_query}%')

            select_query += " ORDER BY id LIMIT ? OFFSET ?"
            params += (per_page, offset)
        else:
            select_query += " ORDER BY id LIMIT ? OFFSET ?"
            params = (per_page, offset)

        cursor.execute(select_query, params)
        books = cursor.fetchall()

        # Get column names from the SELECT query
        columns = [desc[0] for desc in cursor.description]
        books_list = [dict(zip(columns, book)) for book in books]

        if search_query and search_type:
            clean_query = search_query.strip().lower()

            if search_type == 'title':
                count_query = "SELECT COUNT(*) FROM books WHERE LOWER(title) LIKE LOWER(?)"
                count_params = (f'%{clean_query}%',)
            elif search_type == 'author':
                count_query = "SELECT COUNT(*) FROM books WHERE LOWER(author) LIKE LOWER(?)"
                count_params = (f'%{clean_query}%',)
            elif search_type == 'genre':
                count_query = "SELECT COUNT(*) FROM books WHERE LOWER(genre) LIKE LOWER(?)"
                count_params = (f'%{clean_query}%',)
            else:
                count_query = "SELECT COUNT(*) FROM books WHERE LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?) OR LOWER(genre) LIKE LOWER(?)"
                count_params = (f'%{clean_query}%', f'%{clean_query}%', f'%{clean_query}%')
        else:
            count_query = "SELECT COUNT(*) FROM books"
            count_params = ()

        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]

        conn.close()

        if books:
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


def create_pagination_keyboard(current_page, total_pages, search_type=None, search_query=None, books=None):
    """Create inline keyboard for book selection and pagination"""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = []

    # Show book selection numbers (1-10) in 2 rows if we have books
    if books and len(books) > 0:
        # First row: books 1-5
        first_row = []
        for book_num in range(1, min(6, len(books) + 1)):
            first_row.append(InlineKeyboardButton(
                text=str(book_num),
                callback_data=f"select_book_{book_num}_{current_page}_{search_type or 'all'}_{search_query or ''}"
            ))

        if first_row:
            keyboard.append(first_row)

        # Second row: books 6-10 (if they exist)
        second_row = []
        for book_num in range(6, min(11, len(books) + 1)):
            second_row.append(InlineKeyboardButton(
                text=str(book_num),
                callback_data=f"select_book_{book_num}_{current_page}_{search_type or 'all'}_{search_query or ''}"
            ))

        if second_row:
            keyboard.append(second_row)

    # Navigation buttons in third row
    nav_buttons = []

    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Oldingi",
            callback_data=f"prev_{current_page - 1}_{search_type or 'all'}_{search_query or ''}"
        ))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(
            text="Keyingi ➡️",
            callback_data=f"next_{current_page + 1}_{search_type or 'all'}_{search_query or ''}"
        ))

    if nav_buttons:
        keyboard.append(nav_buttons)

    # Back button in fourth row
    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_search")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Order Management Functions

def add_to_cart(user_id, book_id, quantity, price):
    """Add book to user's cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Check if book already exists in cart
        cursor.execute("""
            SELECT id, quantity FROM cart
            WHERE user_id = ? AND book_id = ?
        """, (user_id, book_id))

        existing = cursor.fetchone()

        if existing:
            # Update quantity if already exists
            new_quantity = existing[1] + quantity
            cursor.execute("""
                UPDATE cart SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_quantity, existing[0]))
        else:
            # Insert new cart item
            cursor.execute("""
                INSERT INTO cart (user_id, book_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (user_id, book_id, quantity, price))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return False

def get_user_cart(user_id):
    """Get all items in user's cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.book_id, c.quantity, c.price, c.created_at,
                   b.title, b.author, b.genre, b.image_path
            FROM cart c
            JOIN books b ON c.book_id = b.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        """, (user_id,))

        cart_items = cursor.fetchall()
        conn.close()

        if cart_items:
            columns = [desc[0] for desc in cursor.description]
            cart_list = [dict(zip(columns, item)) for item in cart_items]
            return cart_list
        return []
    except Exception as e:
        print(f"Error getting user cart: {e}")
        return []

def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE id = ?", (cart_item_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return False

def clear_user_cart(user_id):
    """Clear all items from user's cart"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return False

def create_order(user_id, delivery_address, payment_type, total_amount, book_id=None, quantity=None, price=None):
    """Create new order from cart or single book"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO orders (user_id, delivery_address, payment_type, total_amount, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (user_id, delivery_address, payment_type, total_amount))

        order_id = cursor.lastrowid

        if book_id and quantity and price:
            cursor.execute("""
                INSERT INTO order_items (order_id, book_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, book_id, quantity, price))
        else:
            cursor.execute("""
                INSERT INTO order_items (order_id, book_id, quantity, price)
                SELECT ?, book_id, quantity, price FROM cart WHERE user_id = ?
            """, (order_id, user_id))

            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

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

        # Get orders
        cursor.execute("""
            SELECT o.id, o.total_amount, o.status, o.created_at, o.delivery_address
            FROM orders o
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, per_page, offset))

        orders = cursor.fetchall()

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))
        total_count = cursor.fetchone()[0]

        conn.close()

        if orders:
            columns = [desc[0] for desc in cursor.description]
            orders_list = [dict(zip(columns, order)) for order in orders]

            total_pages = (total_count + per_page - 1) // per_page

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

def get_order_details(order_id):
    """Get detailed order information"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT oi.id, oi.book_id, oi.quantity, oi.price,
                   b.title, b.author, b.genre, b.image_path
            FROM order_items oi
            JOIN books b ON oi.book_id = b.id
            WHERE oi.order_id = ?
        """, (order_id,))

        items = cursor.fetchall()
        conn.close()

        if items:
            columns = [desc[0] for desc in cursor.description]
            items_list = [dict(zip(columns, item)) for item in items]
            return items_list
        return []
    except Exception as e:
        print(f"Error getting order details: {e}")
        return []

def get_all_orders(page=1, per_page=10):
    """Get all orders for admin (with pagination)"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        cursor.execute("""
            SELECT o.id, o.user_id, o.total_amount, o.status, o.created_at,
                   o.delivery_address, o.payment_type, u.name, u.phone
            FROM orders o
            JOIN users u ON o.user_id = u.chat_id
            ORDER BY o.created_at DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))

        orders = cursor.fetchall()

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_count = cursor.fetchone()[0]

        conn.close()

        if orders:
            columns = [desc[0] for desc in cursor.description]
            orders_list = [dict(zip(columns, order)) for order in orders]

            total_pages = (total_count + per_page - 1) // per_page

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
        print(f"Error getting all orders: {e}")
        return {
            'orders': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }

def update_order_status(order_id, status):
    """Update order status"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, order_id))
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated
    except Exception as e:
        print(f"Error updating order status: {e}")
        return False