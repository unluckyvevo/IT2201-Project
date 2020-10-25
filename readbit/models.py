from readbit import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(10), nullable=False, default='student')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'user'
    }

    def __repr__(self):
        return f"User('{self.type}', '{self.id}', '{self.username}', '{self.email}')"

class Frog(db.Model):
    frog_state = db.Column(db.Integer, primary_key=True)
    frog_image_link = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Frog state {self.frog_state}'


class Student(User):
    frog_list = db.relationship('Frog', backref='owner', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

class Instructor(User):
    """
    Temp instructor data to test polymorphism - will be changed later
    """
    instructor_data = db.Column(db.String(50), default='I am an instructor')

    __mapper_args__ = {
        'polymorphic_identity': 'instructor'
    }

class Frog(db.Model):
    __tablename__ = 'frog'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mod_name = db.Column(db.String(20), unique=False, nullable=False)
    frog_state = db.Column(db.String(20), unique=False, nullable=False, default='egg')

    def __repr__(self):
        return f"Frog('{self.id}', '{self.frog_state}', '{self.mod_name}', '{self.student_id}')"
