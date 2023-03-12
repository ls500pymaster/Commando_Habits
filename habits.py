import sqlite3
from sqlite3 import Error
from models import Habit


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('habits.db')
        return conn
    except Error as e:
        print(e)

    return conn


def add_habit(name: str, description: str, difficulty: str, days: int, user_id: int):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        habit = Habit(name=name, description=description, difficulty=difficulty, days=days, user_id=user_id)
        cursor.execute('''INSERT INTO habits (name, description, difficulty, days, user_id) 
                          VALUES (?, ?, ?, ?, ?)''', (habit.name, habit.description, habit.difficulty, habit.days, habit.user_id))
        habit_id = cursor.lastrowid
        habit.id = habit_id
    return habit


def get_user_habits(user_id: int):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM habits WHERE user_id = ?''', (user_id,))
        rows = cursor.fetchall()
        habits = []
        for row in rows:
            habit = Habit(id=row[0], name=row[1], description=row[2], difficulty=row[3], days=row[4], user_id=row[5])
            habits.append(habit)
    return habits
