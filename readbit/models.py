from readbit import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


mod_list = db.Table('mod_list',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('module_id', db.Integer, db.ForeignKey('module.id'), primary_key=True)
)

stud_list = db.Table('stud_list',
    db.Column('stud_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('module_class.id'), primary_key=True)
)

class_list = db.Table('class_list',
    db.Column('instr_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('module_class.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(10), nullable=False, default='student')
    mod_list = db.relationship('Module', secondary=mod_list, lazy='subquery')

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
    class_list = db.relationship('ModuleClass', secondary=class_list, lazy='subquery',
                                 backref=db.backref('instructors', lazy=True))

    __mapper_args__ = {
        'polymorphic_identity': 'instructor'
    }


# Backrefs: owner
class Frog(db.Model):
    __tablename__ = 'frog'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mod_name = db.Column(db.String(20), unique=False, nullable=False)
    frog_state = db.Column(db.String(20), unique=False, nullable=False, default='egg')

    def __repr__(self):
        return f"Frog('{self.id}', '{self.frog_state}', '{self.mod_name}', '{self.student_id}')"


class Module(db.Model):
    __tablename__ = 'module'

    id = db.Column(db.Integer, primary_key=True)
    mod_name = db.Column(db.String(100), unique=True, nullable=False)
    class_list = db.relationship('ModuleClass', backref='module', lazy=True)

    def __repr__(self):
        return f"Module('{self.id}', '{self.mod_name}')"


# Backrefs: module, instructors
class ModuleClass(db.Model):
    __tablename__ = 'module_class'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    class_name = db.Column(db.String(100), unique=True, nullable=False)
    class_size = db.Column(db.Integer, nullable=False)
    stud_list = db.relationship('Student', secondary=stud_list, lazy='subquery')

    def __repr__(self):
        return f"ModuleClass('{self.id}', '{self.class_name}', '{self.class_size}')"