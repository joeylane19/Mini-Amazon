from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

# Creates a user object
class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, addr, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.addr = addr
        self.balance = balance

# Authenticates a user
    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, addr, balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

# Checks to see if an email is already in the databes
    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

# Registers a user
    @staticmethod
    def register(email, password, firstname, lastname, addr):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, addr, balance)
VALUES(:email, :password, :firstname, :lastname, :addr, :balance)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname,
                                  lastname=lastname,
                                  addr=addr,
                                  balance=0.0
                                  )
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and
            # reporting needed
            print(e)
            return None

# Gets the id of a given user
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, addr, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

# Chages the firstname of a user
    @staticmethod
    def change_fname(user_id, firstname):
        try:
            rows = app.db.execute('''
            UPDATE Users
            SET
                firstname = :firstname
            WHERE id = :user_id
            ''',
                                  user_id=user_id,
                                  firstname=firstname)
        except Exception as e:
            print(e)
            return None

# Chages the lastname of a user
    @staticmethod
    def change_lname(user_id, lastname):
        try:
            rows = app.db.execute('''
            UPDATE Users
            SET
                lastname = :lastname
            WHERE id = :user_id
            ''',
                                  user_id=user_id,
                                  lastname=lastname)
        except Exception as e:
            print(e)
            return None

# Changes the address of a user
    @staticmethod
    def change_addr(user_id, addr):
        try:
            rows = app.db.execute('''
            UPDATE Users
            SET
                addr = :addr
            WHERE id = :user_id
            ''',
                                  user_id=user_id,
                                  addr=addr)
        except Exception as e:
            print(e)
            return None

# Changes the password of a user
    @staticmethod
    def change_password(user_id, password):
        try:
            rows = app.db.execute('''
            UPDATE Users
            SET
                password = :password
            WHERE id = :user_id
            ''',
                                  user_id=user_id,
                                  password=generate_password_hash(password))
        except Exception as e:
            print(e)
            return None

# Changes the email of a user
    @staticmethod
    def change_email(user_id, email):
        try:
            rows = app.db.execute('''
            UPDATE Users
            SET
                email = :email
            WHERE id = :user_id
            ''',
                                  user_id=user_id,
                                  email=email)
        except Exception as e:
            print(e)
            return None
            
# Chages the balance of a user
    @staticmethod
    def change_balance(user_id, balance):
        try:
            rows = app.db.execute('''
            UPDATE Users
            SET
                balance = :balance
            WHERE id = :user_id
            ''',
                                  user_id=user_id,
                                  balance=balance)
        except Exception as e:
            print(e)
            return None
