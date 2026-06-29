from flask import Flask, jsonify, request
import sqlite3
from datetime import date


app = Flask(__name__)

DB_NAME = "budget_manager.db"


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount INTERGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)


    connection.commit()
    connection.close()


# http://127.0.0.1:5000/api/health
@app.get("/api/health")
def health_check():
    return jsonify({
        "status" : "OK"
    }), 200


@app.post("/api/users")
def register():
    new_user = request.get_json()
    print(new_user)

    username = new_user["username"]
    password = new_user["password"]

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    connection.commit()
    connection.close()
    
    
    return jsonify({
        "succes": True,
        "message" : "User created succesfully"
    }), 201


# http://127.0.0.1:5000/api/users
@app.get("/api/users")
def get_users():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print(rows)
    connection.close()

    users = []
    for row in rows:
        print(dict(row))
        users.append(dict(row))

    return jsonify({
        "success": True,
        "message" : "Users retrueved succesfully",
        "data": users
    }),200


@app.post("/api/expenses")
def create_expense():
    new_expense = request.get_json()
    print("new_expense")

    title = new_expense.get("title","")
    description = new_expense.get("description","")
    amount = new_expense.get("amount", 0)
    date_expense = new_expense.get("date", date.today())
    category = new_expense.get("category","")
    user_id = new_expense.get("user_id", 0)

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES(?, ?, ?, ?, ?, ?)""", (title, description, amount, date_expense, category, user_id))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Expenses created succesfully"
    }), 201

@app.get("/api/expenses")
def get_expenses():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    connection.close()
    print(rows)

    expenses = []
    for row in rows:
        print(dict(row))
        expenses.append(dict(row))


    return jsonify({
        "success": True,
        "message": "Expenses retrieved succesfully",
        "data": expenses
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
