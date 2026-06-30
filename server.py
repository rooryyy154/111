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


#PUT
@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    updated_user = request.get_json()

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT username, password FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    print(user)

    if not user:
        connection.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    username = updated_user.get("username", user[0])
    password = updated_user.get("password", user[1])

    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    
    connection.commit()
    connection.close()

    return jsonify({
            "success": True,
            "message": "User updated successfully"
        }), 200


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


@app.get("/api/users/<int:user_id>") #path parameter <>
def get_user_by_id(user_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row #you need it if you want to use dict row
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)) #SQL lite is 
    row = cursor.fetchone()
    print(row)
    connection.close()

    if not row: #bettwer way to use if not to check it.
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    user = dict(row)

    return jsonify({
        "success": True,
        "message": "User retrieved succesfully",
        "data": user

    }), 200


#PUT


#DELETE
@app.delete("/api/users/<int:user_id>")
def delete_user_by_id(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT id,username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        connection.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "User deleted succesfully"
    }), 200


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

    allowed_categories = ["Food", "Entertainment", "Education"]
    if category not in allowed_categories:
        return jsonify({
            "success": False,
            "message": "Invalid category"
        }), 400
    

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

@app.get("/api/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    connection.close()

    if not row:
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Expense found succesfully",
        "data": dict(row)
    }), 200

# PUT /api/expenses/<expense_id>
@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    updated_expense = request.get_json()
    print(updated_expense)

    if "category" in updated_expense and updated_expense["category"] not in ["Food", "Education", "Entertainment"]:
        return jsonify({
            "success": False,
            "message": "Invalid category."
        }), 400

    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()

    if not expense:
        connection.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    title = updated_expense.get("title", expense["title"])
    description = updated_expense.get("description", expense["description"])
    amount = updated_expense.get("amount", expense["amount"])
    category = updated_expense.get("category", expense["category"])
    user_id = updated_expense.get("user_id", expense["user_id"])

    cursor.execute("""
        UPDATE expenses
        SET title = ?, description = ?, amount = ?, category = ?, user_id = ?
        WHERE id = ?""", (title, description, amount, category, user_id, expense_id))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Expense updated successfully"
    }), 200


# DELETE /api/expenses/<expense_id>
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()

    if not expense:
        connection.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Expense deleted succesfully"
    }), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
