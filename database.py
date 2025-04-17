import mysql.connector


mydb = mysql.connector.connect(
  host="localhost",
  user="root",       
  password="13feb2005",   
  database="eduverse"    
)

# cursor sql query ke liye
cursor = mydb.cursor()

# sql yha se hai
sql = "INSERT INTO login (id, password) VALUES (%s, %s)"
val = ("mohit", "hey2")  

# tupple me data reach hoga
cursor.execute(sql, val)

# Commit changes
mydb.commit()

print(cursor.rowcount, "record inserted.")


cursor.close()
mydb.close()
