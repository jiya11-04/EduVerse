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
    """Handles the login form submission and inserts data into the database."""
    if request.method == 'POST':
        student_id = request.form['student-id']
        password = request.form['password']

        conn = None
        cursor = None

        try:
            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO login (id, password) VALUES (%s, %s)"
            val = (student_id, password)

            cursor.execute(sql, val)
            conn.commit()

            # Redirect to index.html after successful insertion
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
            return redirect('/index.html')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
            return "An error occurred during login."
        # finally block is for guaranteed cleanup, not returning responses
        # finally:
        #     if 'conn' in locals() and conn.is_connected():
        #         if 'cursor' in locals():
        #             cursor.close()
        #         conn.close()
    # This should ideally not be reached on a POST request
    return render_template('login2.html')

@app.route('/index.html')
def serve_index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)