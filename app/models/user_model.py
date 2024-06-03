from app import app
from flask import flash
from app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[a-zA-Z]')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*[0-9]).{8,}$')

bcrypt = Bcrypt(app)

class User: 
    
    db = "chore_track"
    
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email_address = data['email_address']
        self.password = data['password']
        
        self.chores = []
        
        
    @classmethod
    def register(cls, data):
        
        data['password'] = bcrypt.generate_password_hash(data['password'])
        
        query = """
            INSERT INTO 
                users 
            (first_name, last_name, email_address, password) 
            VALUES
            (%(first_name)s, %(last_name)s, %(email_address)s, %(password)s)
        """
        
        return connectToMySQL(cls.db).query_db(query, data)
    
    
    @classmethod
    def get_by_email(cls, email_address):
        query = """
            SELECT *
            FROM users
            WHERE email_address = %(email_address)s
        """
        results = connectToMySQL(cls.db).query_db(query, {'email_address':email_address})
        
        #? Check to make sure something was loaded
        # if not results:
        #     return None
        
        return cls(results[0]) if results else None
    
    @classmethod
    def get_one_by_id(cls, id):
        from app.models.chore_model import Chore
        query = """
            SELECT *, 
                    (
                        SELECT count(*) 
                        FROM chore_track.chores_has_likes
                        WHERE chore_id = chores.id
                    ) as num_likes
            FROM users 
            LEFT JOIN chores ON chores.user_id = users.id
            WHERE users.id = %(id)s
        """
        results = connectToMySQL(cls.db).query_db(query, {'id':id})

        if not results: 
            return None
        
        user = cls(results[0])
        
        for row in results:
            if row['chores.id']:
                user.chores.append(Chore({
                    'id': row['chores.id'],
                    'title': row['title'],
                    'description': row['description'],
                    'location': row['location'],
                    'num_likes': row['num_likes']
                }))
        
        return user
    
    
    
    @staticmethod
    def validate_registration(registration_form):
        #blacklisting
        is_valid = True
        
        #?check if user exists 
        if User.get_by_email(registration_form['email_address']):
            is_valid = False
            flash("Email already exist", "registration")
        
        #? Check First name and last name
        if len(registration_form['first_name']) < 3:
            is_valid = False
            flash("First name must be at least 3 characters", "registration")
            
        if len(registration_form['last_name']) < 3:
            is_valid = False
            flash("Last name must be at least 3 characters", "registration")
        
        if not NAME_REGEX.match(registration_form['last_name']):
            is_valid = False
            flash("Name must contain only letters", "registration")
        
        #? Check password length
        if not PASSWORD_REGEX.match(registration_form['password']):
            flash("Invalid password format, and must be 8 characters, contain at least 1 uppercase letter, and at least 1 number", "registration")
            is_valid = False
        
        #? Check password and confirm password matches
        if registration_form['password'] != registration_form['confirm_password']:
            is_valid = False
            flash("Password must match", "registration")
        
        if len(registration_form['email_address']) == 0:
            is_valid = False
            flash("Email is required", "registration")
        
        if not EMAIL_REGEX.match(registration_form['email_address']):
            is_valid = False
            flash("Invalid email address", "registration")
        
        if is_valid:
            flash("Thanks for registering", 'registration')
        
        return is_valid