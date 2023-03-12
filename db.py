import sqlite3

conn = sqlite3.connect('habits.db')
c = conn.cursor()

# Define constants for table name and column names
TABLE_NAME = "habits"
COLUMN_ID = "id"
COLUMN_NAME = "name"
COLUMN_DESCRIPTION = "description"
COLUMN_DAYS = "days"
COLUMN_USER_ID = "user_id"
COLUMN_DIFFICULTY = "difficulty"

c.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {COLUMN_ID} INTEGER PRIMARY KEY,
        {COLUMN_NAME} TEXT NOT NULL,
        {COLUMN_DESCRIPTION} TEXT NOT NULL,
        {COLUMN_DAYS} INTEGER NOT NULL,
        {COLUMN_DIFFICULTY} TEXT NOT NULL,
        {COLUMN_USER_ID} INTEGER NOT NULL
    )
''')

conn.commit()
conn.close()
