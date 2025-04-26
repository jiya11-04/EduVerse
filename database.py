from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Important for session management

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="13feb2005",
        database="eduverse"
    )

@app.route('/', methods=['GET'])
def index():
    """Renders the login form as the homepage."""
    return render_template('login2.html')

@app.route('/login', methods=['POST'])
def login():
    """Handles the login form submission and verifies credentials."""
    if request.method == 'POST':
        student_id = request.form['student-id']
        password = request.form['password']

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT id, password FROM login WHERE id = %s"
            cursor.execute(sql, (student_id,))
            result = cursor.fetchone()

            if result:
                db_id, db_password = result
                if student_id == str(db_id) and password == db_password:
                    session['student_id'] = student_id  # Store student ID in session
                    return redirect('/index.html')
                else:
                    return "Invalid student ID or password."
            else:
                return "Student ID not found."

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "An error occurred during login."
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    return render_template('login2.html')

@app.route('/index.html')
def serve_index():
    """Renders the index page."""
    if 'student_id' in session:
        return render_template('index.html')
    else:
        return redirect('/')  # Redirect to login if not logged in

@app.route('/query.html', methods=['GET', 'POST'])
def add_query():
    if 'student_id' not in session:
        return redirect('/')

    conn = None
    cursor = None
    queries = []  # Initialize an empty list to store queries

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        student_id = session['student_id']
        sql_select = "SELECT query FROM Queries WHERE id = %s ORDER BY id DESC"  # Fetch queries for the current user
        cursor.execute(sql_select, (student_id,))
        results = cursor.fetchall()
        for row in results:
            queries.append(row[0])

        if request.method == 'POST':
            query_text = request.form['queryInput']
            sql_insert = "INSERT INTO Queries (id, query) VALUES (%s, %s)"
            cursor.execute(sql_insert, (student_id, query_text))
            conn.commit()
            return redirect('/query.html')  # Redirect to refresh and show the new query

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # Handle the error appropriately
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template('query.html', queries=queries)

if __name__ == '__main__':
    app.run(debug=True)