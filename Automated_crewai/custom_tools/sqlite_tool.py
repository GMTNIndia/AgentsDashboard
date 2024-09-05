

# import sqlite3
# from crewai_tools import tool
# import hashlib

# class SQLite3Tool:
#     def __init__(self, database):
#         self.database = database
#         self.conn = None
#         self.cursor = None

#     def connect(self):
#         self.conn = sqlite3.connect(self.database)
#         self.cursor = self.conn.cursor()

#     def close(self):
#         if self.conn:
#             self.conn.close()

#     def create_table(self, create_table_sql):
#         try:
#             self.cursor.execute(create_table_sql)
#             self.conn.commit()
#         except sqlite3.Error as e:
#             print(f"Error creating table: {e}")

#     def insert_data(self, insert_sql, data):
#         try:
#             self.cursor.execute(insert_sql, data)
#             self.conn.commit()
#         except sqlite3.Error as e:
#             print(f"Error inserting data: {e}")

#     def fetch_one(self, select_sql, data=None):
#         try:
#             if data:
#                 self.cursor.execute(select_sql, data)
#             else:
#                 self.cursor.execute(select_sql)
#             return self.cursor.fetchone()
#         except sqlite3.Error as e:
#             print(f"Error fetching data: {e}")
#             return None

# @tool
# def setup_login_registration_database(database_path="users.db"):
#     """
#     Sets up a SQLite database for storing login and registration details.

#     Args:
#     - database_path (str): Path to the SQLite database file. Defaults to "users.db".

#     Returns:
#     - str: A message indicating the success of the database setup.

#     Raises:
#     - sqlite3.Error: If there's an error executing the SQL queries.
#     """
#     create_table_sql = """
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT NOT NULL UNIQUE,
#         email TEXT NOT NULL UNIQUE,
#         password TEXT NOT NULL,
#         company_name TEXT NOT NULL,
#         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#     );
#     """

#     db_tool = SQLite3Tool(database_path)
#     db_tool.connect()
#     db_tool.create_table(create_table_sql)
#     db_tool.close()

#     return "Login and registration database set up successfully"

# @tool
# def register_user(username, email, password, company_name, database_path="users.db"):
#     """
#     Registers a new user in the database.

#     Args:
#     - username (str): User's chosen username.
#     - email (str): User's email address.
#     - password (str): User's password (will be hashed before storage).
#     - company_name (str): User's company name.
#     - database_path (str): Path to the SQLite database file. Defaults to "users.db".

#     Returns:
#     - str: A message indicating the success or failure of the user registration.

#     Raises:
#     - sqlite3.Error: If there's an error executing the SQL queries.
#     """
#     insert_sql = """
#     INSERT INTO users (username, email, password, company_name)
#     VALUES (?, ?, ?, ?);
#     """

#     hashed_password = hashlib.sha256(password.encode()).hexdigest()

#     db_tool = SQLite3Tool(database_path)
#     db_tool.connect()
    
#     try:
#         db_tool.insert_data(insert_sql, (username, email, hashed_password, company_name))
#         return f"User {username} registered successfully"
#     except sqlite3.IntegrityError:
#         return f"Error: Username or email already exists"
#     finally:
#         db_tool.close()
# @tool
# def authenticate_user(email, password, database_path="users.db"):
#     """
#     Authenticates a user based on email and password.

#     Args:
#     - email (str): User's email address.
#     - password (str): User's password.
#     - database_path (str): Path to the SQLite database file. Defaults to "users.db".

#     Returns:
#     - str: A message indicating the success or failure of the authentication.

#     Raises:
#     - sqlite3.Error: If there's an error executing the SQL queries.
#     """
#     select_sql = "SELECT password FROM users WHERE email = ?"
    
#     db_tool = SQLite3Tool(database_path)
#     db_tool.connect()
    
#     try:
#         result = db_tool.fetch_one(select_sql, (email,))
#         if result:
#             stored_password = result[0]
#             hashed_password = hashlib.sha256(password.encode()).hexdigest()
#             if stored_password == hashed_password:
#                 return "Login successful"
#             else:
#                 return "Error: Incorrect password"
#         else:
#             return "Error: User not found"
#     finally:
#         db_tool.close()

# if __name__ == "__main__":
#     database_path = "users.db"
#     setup_login_registration_database(database_path)
    # print(register_user("testuser", "test@example.com", "password123", database_path))
    # print(authenticate_user("test@example.com", "password123", database_path))


import sqlite3
from crewai_tools import tool
import hashlib
import re
import traceback

class SQLite3Tool:
    def __init__(self, database):
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_table(self, create_table_sql):
        try:
            self.cursor.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_data(self, insert_sql, data):
        try:
            self.cursor.execute(insert_sql, data)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def fetch_one(self, select_sql, data=None):
        try:
            if data:
                self.cursor.execute(select_sql, data)
            else:
                self.cursor.execute(select_sql)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return None
@tool
def is_valid_email(email):
    """
    Validate email address format using a regular expression.

    Args:
    - email (str): Email address to validate.

    Returns:
    - bool: True if the email format is valid, otherwise False.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

@tool
def setup_login_registration_database(database_path="users.db"):
    """
    Sets up a SQLite database for storing login and registration details.

    Args:
    - database_path (str): Path to the SQLite database file. Defaults to "users.db".

    Returns:
    - str: A message indicating the success of the database setup.

    Raises:
    - sqlite3.Error: If there's an error executing the SQL queries.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        company_name TEXT NOT NULL,
        email_verified INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    db_tool = SQLite3Tool(database_path)
    db_tool.connect()
    db_tool.create_table(create_table_sql)
    db_tool.close()

    return "Login and registration database set up successfully"

@tool
def register_user(username, email, password, company_name, database_path="users.db"):
    """
    Registers a new user in the database.

    Args:
    - username (str): User's chosen username.
    - email (str): User's email address.
    - password (str): User's password (will be hashed before storage).
    - company_name (str): User's company name.
    - database_path (str): Path to the SQLite database file. Defaults to "users.db".

    Returns:
    - str: A message indicating the success or failure of the user registration.

    Raises:
    - sqlite3.Error: If there's an error executing the SQL queries.
    """
    insert_sql = """
    INSERT INTO users (username, email, password, company_name)
    VALUES (?, ?, ?, ?);
    """

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    db_tool = SQLite3Tool(database_path)
    db_tool.connect()
    
    try:
        db_tool.insert_data(insert_sql, (username, email, hashed_password, company_name))
        return f"User {username} registered successfully"
    except sqlite3.IntegrityError:
        return f"Error: Username or email already exists"
    finally:
        db_tool.close()
@tool
def verify_email(email, database_path="users.db"):
    """
    Verifies the user's email address.

    Args:
    - email (str): User's email address.
    - database_path (str): Path to the SQLite database file. Defaults to "users.db".

    Returns:
    - str: A message indicating the success or failure of the email verification.

    Raises:
    - sqlite3.Error: If there's an error executing the SQL queries.
    """
    update_sql = """
    UPDATE users
    SET email_verified = 1
    WHERE email = ?;
    """

    db_tool = SQLite3Tool(database_path)
    db_tool.connect()
    
    try:
        db_tool.insert_data(update_sql, (email,))
        return "Email verified successfully."
    except sqlite3.Error as e:
        return f"Error verifying email: {e}"
    finally:
        db_tool.close()

@tool
def authenticate_user(email, password, database_path="users.db"):
    """
    Authenticates a user based on email and password.

    Args:
    - email (str): User's email address.
    - password (str): User's password.
    - database_path (str): Path to the SQLite database file. Defaults to "users.db".

    Returns:
    - str: A message indicating the success or failure of the authentication.

    Raises:
    - sqlite3.Error: If there's an error executing the SQL queries.
    """
    select_sql = "SELECT password, email_verified FROM users WHERE email = ?"
    
    db_tool = SQLite3Tool(database_path)
    db_tool.connect()
    
    try:
        result = db_tool.fetch_one(select_sql, (email,))
        if result:
            stored_password, email_verified = result
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if stored_password == hashed_password:
                if email_verified:
                    return "Login successful"
                else:
                    return "Error: Email not verified"
            else:
                return "Error: Incorrect password"
        else:
            return "Error: User not found"
    finally:
        db_tool.close()

if __name__ == "__main__":
    database_path = "users.db"
    setup_login_registration_database(database_path)
