import mysql.connector

def build_database():
    print("Connecting to MySQL...")
    try:
        # Connect to MySQL (no database selected yet)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234' # <--- Put your password here if you have one
        )
        cursor = conn.cursor()

        print("Reading schema.sql...")
        with open('schema.sql', 'r') as file:
            sql_script = file.read()

        # Split the file by the ';' character to run each command one by one
        sql_commands = sql_script.split(';')
        
        print("Building database and tables...")
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Success! Database and tables created perfectly.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    build_database()