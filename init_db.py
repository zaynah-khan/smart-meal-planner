"""Run this once (and any time you want to reset your data) to create meal_planner.db"""
import sqlite3

conn = sqlite3.connect("meal_planner.db")
with open("schema.sql") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Database initialized: meal_planner.db")
