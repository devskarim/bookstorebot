# Book Store Bot

A Telegram bot for bookstore management built with Python, aiogram, and SQLite3.

## Features

- User registration and management
- Book catalog management
- Order processing
- Admin panel
- SQLite3 database (file-based, perfect for deployments)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
TOKEN=your_telegram_bot_token
DATABASE_PATH=data/app.db
ADMIN_CHATID=your_admin_chat_id
```

3. Run the bot:
```bash
python main.py
```

## Railway Deployment

This project is optimized for Railway deployment:

1. **Connect your repository** to Railway
2. **Add environment variables** in Railway dashboard:
   - `TOKEN`: Your Telegram bot token
   - `DATABASE_PATH`: Database file path (default: `data/app.db`)
   - `ADMIN_CHATID`: Your admin chat ID

3. **Deploy** - Railway will automatically:
   - Install Python dependencies
   - Create the SQLite database file
   - Start your application

## Database

The application uses SQLite3 with the following tables:
- `users`: User information and registration
- `books`: Book catalog
- `orders`: Order management

The database file is automatically created in the `data/` directory.

## Project Structure

```
├── main.py              # Main application entry point
├── database/
│   ├── connection.py    # Database connection (SQLite3)
│   └── query.py         # Database queries and operations
├── handler/             # Telegram message handlers
├── buttons/             # Inline keyboard buttons
├── states/              # Conversation states
└── requirements.txt     # Python dependencies