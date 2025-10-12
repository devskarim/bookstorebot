from .connection import get_connect
import os
import uuid

# Try to import reportlab for PDF generation
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

        if 'image_path' in columns:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity, image_path
                FROM books
                WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
                ORDER BY id
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            cursor.execute("""
                SELECT id, title, description, author, price, genre, quantity
                FROM books
                WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
                ORDER BY id
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))

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