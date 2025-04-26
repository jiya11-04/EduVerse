from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

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
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)