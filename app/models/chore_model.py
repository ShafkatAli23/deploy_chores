from app.config.mysqlconnection import connectToMySQL

from app.models.user_model import User

class Chore:
    db = "chore_track"
    
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.location = data['location']
        
        self.likes =[]
        self.num_likes = data['num_likes']
        self.poster = None
        
        
        
        if 'users.id' in data:
            self.poster = User({
                'id': data['users.id'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email_address': data['email_address'],
                'password': data['password'],
            })
        
        
        
    @classmethod
    def get_one_chore(cls, id):
        query = """
            SELECT *, 
                    (
                        SELECT count(*) 
                        FROM chore_track.chores_has_likes
                        WHERE chore_id = chores.id
                    ) as num_likes
            FROM chores
            WHERE chores.id = %(id)s
        """
        results = connectToMySQL(cls.db).query_db(query, {'id':id})
        
        #? Check to make sure something was loaded
        # if not results:
        #     return None
        
        return cls(results[0]) if results else None
    
    @classmethod
    def get_all_chores(cls):
        query = """
            SELECT *, 
                    (
                        SELECT count(*) 
                        FROM chore_track.chores_has_likes
                        WHERE chore_id = chores.id
                    ) as num_likes
            FROM chores
            LEFT JOIN users ON users.id = chores.user_id
        """
        # results = connectToMySQL(cls.db).query_db(query)
        # chores = []
        
        # for result in results:
        #     chores.append(cls(result))
        
        #list comprehension
        return [cls(data) for data in connectToMySQL(cls.db).query_db(query)]
    
    @classmethod
    def create_chore(cls, data):
        query = """
            INSERT INTO chores
            (title, description, location, user_id)
            VALUES
            (%(title)s, %(description)s, %(location)s, %(user_id)s)
        """
        return  connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def update_chore(cls, data):
        query = """
            UPDATE chores
            SET title = %(title)s, description = %(description)s, location = %(location)s
            WHERE id = %(id)s
        """
        
        return  connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def delete_chore(cls, id):
        query = """
            DELETE
            FROM chores
            WHERE id = %(id)s
        """
        return connectToMySQL(cls.db).query_db(query, {'id':id})
    
    
    #?? Many to Many 
    @classmethod
    def get_one_with_likes(cls, id):
        
        query = """
            SELECT * , 
                    (
                        SELECT count(*) 
                        FROM chore_track.chores_has_likes
                        WHERE chore_id = chores.id
                    ) as num_likes
            FROM chores
            LEFT JOIN chores_has_likes ON chores.id = chores_has_likes.chore_id
            LEFT JOIN users ON  chores_has_likes.user_id = users.id 
            WHERE chores.id = %(id)s
        """
        results = connectToMySQL(cls.db).query_db(query, {'id':id})

        if not results: 
            return None
        
        chore = cls(results[0])
        
        for row in results:
            if row['users.id']:
                chore.likes.append(User({
                    'id': row['users.id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email_address': row['email_address'],
                    'password': row['password']
                }))
        
        return chore
    
    @classmethod
    def add_like(cls, chore_id, user_id):
        query = """
            INSERT INTO chores_has_likes
            (chore_id, user_id)
            VALUES
            (%(chore_id)s, %(user_id)s)
        """
        return  connectToMySQL(cls.db).query_db(query, {"chore_id": chore_id, "user_id": user_id})