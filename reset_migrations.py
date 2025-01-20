import sqlite3

# Connect to your Django SQLite database
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Execute the SQL command to delete migrations for the 'classrooms' app
cursor.execute("DELETE FROM django_migrations WHERE app='classrooms'")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Migrations for the 'classrooms' app have been deleted.")
