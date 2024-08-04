import sqlite3
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import openai

def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                      (id INTEGER PRIMARY KEY, description TEXT, amount REAL, date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets
                      (id INTEGER PRIMARY KEY, category TEXT, limit REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals
                      (id INTEGER PRIMARY KEY, description TEXT, amount REAL, target_date TEXT)''')

    conn.commit()
    conn.close()

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (description, amount, date) VALUES (?, ?, ?)",
                   (data['description'], data['amount'], data['date']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    expenses = query_db("SELECT * FROM expenses")
    return jsonify(expenses)

# Similar endpoints for budgets and goals

if __name__ == '__main__':
    app.run(debug=True)

# Example training data
descriptions = ["Grocery shopping", "Monthly rent", "Gym membership", "Restaurant dinner"]
categories = ["Groceries", "Rent", "Health", "Dining"]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(descriptions)

clf = MultinomialNB()
clf.fit(X, categories)

def categorize_expense(description):
    x_new = vectorizer.transform([description])
    return clf.predict(x_new)[0]

# Example usage
print(categorize_expense("Bought some apples and bananas"))  # Output: "Groceries"

openai.api_key = 'YOUR_API_KEY'

def ai_assistant(query):
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=query,
      max_tokens=150
    )
    return response.choices[0].text.strip()

# Example usage
print(ai_assistant("How much did I spend on groceries last month?"))