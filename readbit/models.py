from readbit import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import logging

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

class Student(User):
    frog_list = db.relationship('Frog', backref='owner', lazy=True)
    feedback_list = db.relationship('Feedback', foreign_keys='Feedback.stud_id',lazy=True)
    listeners = db.relationship('ModuleClass', secondary=stud_list, lazy='subquery', back_populates='stud_list')

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }


class Instructor(User):
    class_list = db.relationship('ModuleClass', secondary=class_list, lazy='subquery',
                                 backref=db.backref('instructors', lazy=True))

    __mapper_args__ = {
        'polymorphic_identity': 'instructor'
    }

class UserFactory():
    @staticmethod
    def createUser(type, username, email, password):
        if type == 'student':
            return Student(type=type, username=username, email=email, password=password)
        elif type == 'instructor':
            return Instructor(type=type, username=username, email=email, password=password)
        else:
            raise ValueError(f'UserFactory.createUser(type=\'{type}\'): type must be of \'student\' or \'instructor\'')

class StudentNotifier():
    @staticmethod
    def attachListener(student, module_class):
        student.listeners.append(module_class)

    @staticmethod
    def detachListener(student, module_class):
        student.listeners.remove(module_class)

    @staticmethod
    def notify(student):
        for listener in student.listeners:
            ClassManager.updateFrogList(listener)

class Module(db.Model):
    __tablename__ = 'module'

    id = db.Column(db.Integer, primary_key=True)
    mod_name = db.Column(db.String(100), unique=True, nullable=False)
    class_list = db.relationship('ModuleClass', backref='module', lazy=True)
    comp_list = db.relationship('MainComp', backref='module', lazy=True)

    def __repr__(self):
        return f"Module('{self.id}', '{self.mod_name}')"


# Backref(s): module, instructors
class ModuleClass(db.Model):
    __tablename__ = 'module_class'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey(Module.id), nullable=False)
    class_name = db.Column(db.String(100), unique=True, nullable=False)
    class_size = db.Column(db.Integer, nullable=False)
    stud_list = db.relationship('Student', secondary=stud_list, lazy='subquery', back_populates='listeners')
    frog_list = db.relationship('Frog', backref='class', lazy=True)

    def __repr__(self):
        return f"ModuleClass('{self.id}', '{self.class_name}', '{self.class_size}')"


class ClassManager():
    @staticmethod
    def updateFrogList(module_class):
        for frog in module_class.frog_list:
            FrogManager.updateState(frog)


# Backref(s): owner
class Frog(db.Model):
    __tablename__ = 'frog'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey(ModuleClass.id), nullable=False)
    mod_name = db.Column(db.String(20), unique=False, nullable=False)
    frog_state = db.Column(db.String(20), unique=False, nullable=False, default='egg')

    def __repr__(self):
        return f"Frog('{self.id}', '{self.frog_state}', '{self.mod_name}', '{self.student_id}')"


class FrogManager():
    @staticmethod
    def updateState(frog):
        pass

class Component(db.Model):
    __tablename__ = 'component'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weightage = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='main')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'component'
    }

    def __repr__(self):
        return f"Component('{self.type}', '{self.id}', '{self.weightage}')"


# Backref(s): module
class MainComp(Component):
    module_id = db.Column(db.Integer, db.ForeignKey(Module.id), nullable=True)
    sub_comp_list = db.relationship('SubComp', remote_side='SubComp.main_comp_id')

    __mapper_args__ = {
        'polymorphic_identity': 'main'
    }


class SubComp(Component):
    main_comp_id = db.Column(db.Integer, db.ForeignKey(MainComp.id), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'sub'
    }

class ComponentFactory():
    @staticmethod
    def createComponent(type, name, weightage, **kwargs):
        if type == 'main':
            module_id = kwargs.get('module_id')
            return MainComp(name=name, weightage=weightage, type=type, module_id=module_id)
        elif type == 'sub':
            main_comp_id = kwargs.get('main_comp_id')
            return SubComp(name=name, weightage=weightage, type=type, main_comp_id=main_comp_id)
        else:
            raise ValueError(f'ComponentFactory.createComponent(type=\'{type}\'): type must be of \'main\' or \'sub\'')

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    stud_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    inst_id = db.Column(db.Integer, db.ForeignKey(Instructor.id), nullable=False)
    comp_name = db.Column(db.String(100), db.ForeignKey(MainComp.name), nullable=False)
    comment = db.Column(db.Text)
    marks = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Feedback('{self.id}', '{self.comment}', '{self.marks}', '{self.date}')"