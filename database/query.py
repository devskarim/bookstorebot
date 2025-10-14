from .connection import get_connect
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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
            is_admin BOOLEAN DEFAULT 0,
            admin_level VARCHAR(20) DEFAULT 'user' CHECK (admin_level IN ('user', 'admin', 'super_admin'))
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


def add_admin(chat_id):
    """Add admin privileges to a user"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return False, "Foydalanuvchi topilmadi. Avval ro'yxatdan o'tishi kerak."

        cursor.execute("UPDATE users SET is_admin = 1 WHERE chat_id = ?", (chat_id,))
        conn.commit()

        success = cursor.rowcount > 0
        conn.close()

        if success:
            return True, "✅ Admin muvaffaqiyatli qo'shildi!"
        else:
            return False, "❌ Admin qo'shishda xatolik yuz berdi."

    except Exception as e:
        print(f"Error adding admin: {e}")
        return False, f"❌ Xatolik: {e}"


def get_all_users(page=1, per_page=10):
    """Get all users with pagination"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()
        column_names = [column[1] for column in columns_info]

        # Check what columns actually exist in the users table
        print(f"Debug: Available columns in users table: {column_names}")

        # Select all available columns - be more flexible with column names
        select_columns = ['id', 'chat_id']

        # Try different possible name column variations
        if 'name' in column_names:
            select_columns.append('name')
        elif 'fullname' in column_names:
            select_columns.append('fullname as name')
        else:
            select_columns.append("'Noma\'lum' as name")  # Default value if no name column

        select_columns.extend(['phone', 'username', 'is_active', 'is_admin'])

        if 'admin_level' in column_names:
            select_columns.append('admin_level')

        columns_sql = ', '.join(select_columns)
        print(f"Debug: SQL query: SELECT {columns_sql} FROM users")

        cursor.execute(f"""
            SELECT {columns_sql}
            FROM users
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))

        print(f"Debug: Available columns in users table: {column_names}")  # Debug line

        users = cursor.fetchall()

        # Debug: print actual data from database
        print(f"Debug: Raw users data: {users[:3] if users else 'No users'}")

        cursor.execute("SELECT COUNT(*) FROM users")
        total_count = cursor.fetchone()[0]

        conn.close()

        if users:
            columns = [desc[0] for desc in cursor.description]
            print(f"Debug: Column names: {columns}")
            print(f"Debug: First user data: {users[0]}")
            users_list = [dict(zip(columns, user)) for user in users]
            print(f"Debug: First user dict: {users_list[0]}")

            total_pages = (total_count + per_page - 1) // per_page

            return {
                'users': users_list,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        return {
            'users': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error getting all users: {e}")
        return {
            'users': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page,
            'per_page': per_page
        }


def get_user_by_chat_id_or_phone(chat_id=None, phone=None, username=None):
    """Get user by chat_id, phone number, or username"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        if chat_id:
            cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        elif phone:
            cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
        elif username:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        else:
            conn.close()
            return None

        result = cursor.fetchone()
        conn.close()

        if result:
            columns = [desc[0] for desc in cursor.description]
            user_dict = dict(zip(columns, result))
            return user_dict
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_username(username):
    """Get user by username"""
    try:
        conn = get_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            columns = [desc[0] for desc in cursor.description]
            user_dict = dict(zip(columns, result))
            return user_dict
        return None
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return None


def is_super_admin(chat_id):
    """Check if user is super admin"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'admin_level' in columns:
            cursor.execute("SELECT admin_level FROM users WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            return bool(result and result[0] == 'super_admin')
        else:
            # Fallback: check if chat_id matches .env ADMIN_CHATID
            env_chat_id = os.environ.get('ADMIN_CHATID', '').strip()
            if str(chat_id) == env_chat_id:
                return True
            # Also check if user is admin (for backward compatibility)
            cursor.execute("SELECT is_admin FROM users WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            return bool(result and result[0] == 1)

    except Exception as e:
        print(f"Error checking super admin status: {e}")
        return False
    finally:
        conn.close()


def is_regular_admin(chat_id):
    """Check if user is regular admin"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'admin_level' in columns:
            cursor.execute("SELECT admin_level FROM users WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            return bool(result and result[0] == 'admin')
        else:
            env_chat_id = os.environ.get('ADMIN_CHATID', '').strip()
            if str(chat_id) == env_chat_id:
                return False  # Super admin is not regular admin
            cursor.execute("SELECT is_admin FROM users WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            return bool(result and result[0] == 1)

    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False
    finally:
        conn.close()


def add_admin_with_level(chat_id, level='admin'):
    """Add admin privileges to a user with specific level"""
    try:
        # First ensure the admin_level column exists
        add_admin_level_column()

        conn = get_connect()
        cursor = conn.cursor()

        # First check if user exists
        cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return False, "Foydalanuvchi topilmadi. Avval ro'yxatdan o'tishi kerak."

        # Add admin privileges with level
        cursor.execute("UPDATE users SET is_admin = 1, admin_level = ? WHERE chat_id = ?", (level, chat_id))
        conn.commit()

        success = cursor.rowcount > 0
        conn.close()

        if success:
            level_text = "Super Admin" if level == 'super_admin' else "Admin"
            return True, f"✅ {level_text} muvaffaqiyatli qo'shildi!"
        else:
            return False, "❌ Admin qo'shishda xatolik yuz berdi."

    except Exception as e:
        print(f"Error adding admin with level: {e}")
        return False, f"❌ Xatolik: {e}"


def remove_admin(chat_id):
    """Remove admin privileges from a user"""
    try:
        # First ensure the admin_level column exists
        add_admin_level_column()

        conn = get_connect()
        cursor = conn.cursor()

        # Check if admin_level column exists before using it
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'admin_level' in columns:
            cursor.execute("UPDATE users SET is_admin = 0, admin_level = 'user' WHERE chat_id = ?", (chat_id,))
        else:
            cursor.execute("UPDATE users SET is_admin = 0 WHERE chat_id = ?", (chat_id,))

        conn.commit()

        success = cursor.rowcount > 0
        conn.close()

        if success:
            return True, "✅ Admin huquqlari olib tashlandi!"
        else:
            return False, "❌ Admin huquqlarini olib tashlashda xatolik yuz berdi."

    except Exception as e:
        print(f"Error removing admin: {e}")
        return False, f"❌ Xatolik: {e}"


def get_all_admins():
    """Get all admins (both super and regular)"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        # Check if admin_level column exists
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()
        column_names = [column[1] for column in columns_info]

        if 'admin_level' in column_names:
            cursor.execute("""
                SELECT chat_id, name, phone, username, admin_level, id
                FROM users
                WHERE is_admin = 1
                ORDER BY
                    CASE admin_level
                        WHEN 'super_admin' THEN 1
                        WHEN 'admin' THEN 2
                    END, id
            """)
        else:
            cursor.execute("""
                SELECT chat_id, name, phone, username, 'admin' as admin_level, id
                FROM users
                WHERE is_admin = 1
                ORDER BY id
            """)

        admins = cursor.fetchall()
        conn.close()

        if admins:
            columns = [desc[0] for desc in cursor.description]
            admins_list = [dict(zip(columns, admin)) for admin in admins]
            return admins_list
        return []
    except Exception as e:
        print(f"Error getting all admins: {e}")
        return []


def get_monthly_stats(month=None, year=None):
    """Get monthly statistics for orders and users"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        if month and year:
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT o.id) as total_orders,
                    COUNT(DISTINCT o.user_id) as unique_customers,
                    SUM(o.total_amount) as total_revenue,
                    COUNT(oi.id) as total_items_sold
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE strftime('%m', o.created_at) = ? AND strftime('%Y', o.created_at) = ?
            """, (f"{month:02d}", str(year)))
        else:
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT o.id) as total_orders,
                    COUNT(DISTINCT o.user_id) as unique_customers,
                    SUM(o.total_amount) as total_revenue,
                    COUNT(oi.id) as total_items_sold
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE strftime('%m', o.created_at) = strftime('%m', 'now')
                AND strftime('%Y', o.created_at) = strftime('%Y', 'now')
            """)

        stats = cursor.fetchone()
        conn.close()

        if stats:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, stats))
        return None
    except Exception as e:
        print(f"Error getting monthly stats: {e}")
        return None


def add_admin_level_column():
    """Add admin_level column to existing users table"""
    try:
        conn = get_connect()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'admin_level' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN admin_level VARCHAR(20) DEFAULT 'user'")
            conn.commit()
            print("✅ admin_level column added to users table successfully!")
        else:
            print("ℹ️ admin_level column already exists in users table")

        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error adding admin_level column: {e}")
        return False


def setup_super_admin(super_admin_chat_id):
    """Set up the first super admin based on environment variable"""
    try:
        # Ensure admin_level column exists
        add_admin_level_column()

        conn = get_connect()
        cursor = conn.cursor()

        # Check if super admin already exists
        cursor.execute("SELECT chat_id FROM users WHERE admin_level = 'super_admin'")
        existing_super_admin = cursor.fetchone()

        if existing_super_admin:
            print(f"✅ Super admin already exists: {existing_super_admin[0]}")
            conn.close()
            return True

        # Check if the user exists in database
        cursor.execute("SELECT id, name FROM users WHERE chat_id = ?", (super_admin_chat_id,))
        user = cursor.fetchone()

        if user:
            user_id, user_name = user
            cursor.execute(
                "UPDATE users SET is_admin = 1, admin_level = 'super_admin' WHERE chat_id = ?",
                (super_admin_chat_id,)
            )
            print(f"✅ User {user_name} ({super_admin_chat_id}) promoted to Super Admin")
        else:
            print(f"⚠️ User {super_admin_chat_id} not found in database.")
            print("📝 Please register this user first by sending a message to the bot.")
            print("🔄 Then restart the bot to complete super admin setup.")

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error setting up super admin: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_users_pdf(users, filename="barcha_foydalanuvchilar.pdf"):
    """Generate PDF with all users information"""
    try:
        # Check if ReportLab is actually available at runtime
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            print("✅ ReportLab imports successful")
        except ImportError as e:
            print(f"❌ ReportLab import failed: {e}")
            print("💡 Try: pip install reportlab==4.4.4")
            return None

        pdf_dir = "pdf_reports/"
        os.makedirs(pdf_dir, exist_ok=True)

        pdf_path = os.path.join(pdf_dir, filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = styles['Heading1']
        title = Paragraph("Barcha Foydalanuvchilar Ro'yxati", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # Handle empty users list
        if not users:
            no_data_style = styles['Heading3']
            no_data_text = Paragraph("Hozircha foydalanuvchilar yo'q.", no_data_style)
            story.append(no_data_text)
        else:
            # Add subtitle with user count and date
            subtitle_style = styles['Heading3']
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            subtitle = Paragraph(f"Jami: {len(users)} ta foydalanuvchi | {current_date}", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 15))

            table_data = [["Ism", "Username", "Telefon", "Holati", "Admin"]]

            for i, user in enumerate(users):
                print(f"Debug PDF user {i}: {user}")  # Debug line
    
                # Handle active status - use plain text for PDF compatibility
                try:
                    is_active = user.get('is_active', 0)
                    if isinstance(is_active, str):
                        is_active = 1 if is_active.lower() in ['1', 'true', 'yes'] else 0
                    status_text = "Faol" if is_active == 1 else "Nofaol"
                except:
                    status_text = "Nofaol"
    
                # Handle admin status - use plain text for PDF compatibility
                try:
                    is_admin = user.get('is_admin', 0)
                    if isinstance(is_admin, str):
                        is_admin = 1 if is_admin.lower() in ['1', 'true', 'yes'] else 0
                    admin_text = "Ha" if is_admin == 1 else "Yo'q"
                except:
                    admin_text = "Yo'q"
    
                # Handle username - use plain text for PDF compatibility
                username = user.get('username', '')
                if username and username != 'unknown' and username != 'None':
                    username_text = f"@{username}"
                else:
                    username_text = "Yo'q"
    
                # Get name with multiple fallbacks
                name = (user.get('name') or
                       user.get('fullname') or
                       user.get('user_name') or
                       f"User {user.get('id', 'Unknown')}")
    
                # Handle phone with fallback
                phone = user.get('phone') or "Noma'lum"
    
                table_data.append([
                    str(name),
                    username_text,
                    str(phone),
                    status_text,
                    admin_text
                ])

            # Create table only if we have data
            table = Table(table_data)

            # Improved table styling for better readability
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

                # Data styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

                # Grid lines
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black)
            ]))

            story.append(table)

        doc.build(story)

        return pdf_path
    except Exception as e:
        print(f"Error generating users PDF: {e}")
        import traceback
        traceback.print_exc()
        return None
    
