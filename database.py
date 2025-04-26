from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
import qrcode
from PIL import Image
from IPython.display import display





app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Important for session management

# Configure the upload folder for profile pictures
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="13feb2005",
        database="eduverse"
    )

def get_profile_image_data(student_id):
    conn = None
    cursor = None
    image_data = None  # Initialize to None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT name, picture_path FROM my_images WHERE id = %s"
        cursor.execute(sql, (student_id,))
        result = cursor.fetchone()  # Fetch only one row

        if result:
            image_data = {'name': result[0], 'path': result[1]}  # Use meaningful keys
            print("imagepath is:", image_data['path'])
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return image_data

@app.route('/', methods=['GET'])
def index():
    if 'student_id' not in session:
        return redirect('/login')  # Redirect to the login page
    else:
        student_id = session['student_id']
        image_data = get_profile_image_data(student_id)
        return render_template('index.html', image_data=image_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles both displaying the login form (GET) and processing login (POST)."""
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

    elif request.method == 'GET':
        return render_template('login2.html')  # Serve the login form

@app.route('/index.html')
def serve_index():
    """Renders the index page."""
    if 'student_id' in session:
        student_id = session['student_id']
        image_data = get_profile_image_data(student_id)  # Fetch image data
        return render_template('index.html', image_data=image_data)  # Pass image_data
    else:
        return redirect('/login')  # Redirect to login if not logged in

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

@app.route('/report.html')
def report():
    if 'student_id' not in session:
        return redirect('/')

    student_id = session['student_id']
    sql = "SELECT Subject, Code, MidTheory, MidPractical, EndTheory, EndPractical FROM result WHERE id = %s"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, (student_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    total_marks = 0
    for result in results:
        total_marks += result[2] + result[3] + result[4] + result[5]

    grade = calculate_grade(total_marks)

    return render_template('report.html', results=results, grade=grade)

def calculate_grade(total_marks):
    if total_marks >= 180:
        return 'A+'
    elif total_marks >= 160:
        return 'A'
    elif total_marks >= 140:
        return 'B+'
    elif total_marks >= 120:
        return 'B'
    elif total_marks >= 100:
        return 'C'
    else:
        return 'F'

@app.route('/profile.html')
def profile_img():
    if 'student_id' not in session:
        return redirect('/')

    student_id = session['student_id']
    conn = None
    cursor = None
    image_data = None  # Initialize to None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT name, picture_path FROM my_images WHERE id = %s"
        cursor.execute(sql, (student_id,))
        result = cursor.fetchone()  # Fetch only one row

        if result:
            image_data = {'name': result[0], 'path': result[1]}  # Use meaningful keys
            print("imagepath is :",image_data['path'])
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # Handle the error appropriately
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template('profile.html', image_data=image_data)

@app.route('/foodcourt/asian.html', methods=['POST', 'GET'])
def foodorders():
    if 'student_id' not in session:
        return redirect('/')

    student_id = session['student_id']
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            # Get data from the form
            dish_name = request.form['item']
            quantity = int(request.form['quantity'])
            pickup_time = request.form['pickup']
            customer_name = request.form['name']
            contact_number = request.form['contact']
            
            price = 0
            if "Hakka Noodles" in dish_name:
                price = 100
            elif "Spring Rolls" in dish_name:
                price = 80
            elif "Veg Manchurian" in dish_name:
                price = 110

            total_cost = price * quantity
            
            data = "https://www.example.com"

# Generate QR code
            qr = qrcode.QRCode(
            version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
            qr.add_data(data)
            qr.make(fit=True)

# Create image
            img = qr.make_image(fill_color="black", back_color="white")

# Display the image in Colabdisplay(img)

            # Print the data to debug
            print(f"Data received: student_id={student_id}, dish_name={dish_name}, quantity={quantity}, pickup_time={pickup_time}, customer_name={customer_name}, contact_number={contact_number}")

            # SQL query to insert data into the Orders table
            sql = """
                INSERT INTO Orders (id, dish_name, quantity, pickup_time, customer_name, contact_number,totalprice)
                VALUES (%s, %s, %s, %s, %s, %s,%s)
            """
            # Execute the query with the form data
            cursor.execute(sql, (student_id, dish_name, quantity, pickup_time, customer_name, contact_number,total_cost))
            conn.commit()
            print("Order placed successfully!")

        else:
            print("Received a GET request (form not submitted).")  # Added to debug

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print(f"SQL query: {sql}")  # prints the sql query
        print(f"Parameters: {(student_id, dish_name, quantity, pickup_time, customer_name, contact_number)}")  # prints the parameters
        # conn.rollback() # uncomment this if you want to rollback
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template('/foodcourt/asian.html')



if __name__ == '__main__':
    app.run(debug=True)