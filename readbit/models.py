from readbit import db, login_manager, bcrypt
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

class UserManager():
    @staticmethod
    def addMod(user, module):
        if module not in user.mod_list:
            user.mod_list.append(module)
        else:
            raise ValueError("Append failed: Module already exist")

    @staticmethod
    def changePassword(user, password):
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashed_pw

class Student(User):
    frog_list = db.relationship('Frog', backref='owner', lazy=True)
    feedback_list = db.relationship('Feedback', foreign_keys='Feedback.stud_id',lazy=True)
    listeners = db.relationship('ModuleClass', secondary=stud_list, lazy='subquery', back_populates='stud_list')

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

class StudentManager():
    @staticmethod
    def getGrade(student, module):
        total = 0

        for feedback in student.feedback_list:
            if feedback.mod_name == module.mod_name:
                total += feedback.marks

        if total >= 80:
            grade = 'A'
        elif total >= 70:
            grade = 'B'
        elif total >= 60:
            grade = 'C'
        elif total >= 50:
            grade = 'D'
        else:
            grade = 'F'

        return {'marks' : total, 'grade' : grade}




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
        if module_class not in student.listeners:
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


class ModuleManager():
    @staticmethod
    def addClass(module, module_class):
        if module_class not in module.class_list:
            module.class_list.append(module_class)
        else:
            raise ValueError("Append failed: Class already exist")

    @staticmethod
    def addComponent(module, main_component):
        total = main_component.weightage
        for comp in module.comp_list:
            total += comp.weightage

        if total <= 100:
            module.comp_list.append(main_component)
        else:
            return "Error: Module weightage exceeds 100%"



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

    @staticmethod
    def addStudent(module_class, student):
        if student in module_class.stud_list:
            return "Error: Student is already registered in the class"
        elif len(module_class.stud_list) >= module_class.class_size:
            return "Error: Class is already full"
        elif module_class.module in student.mod_list:
            return "Error: Student is already in another class"
        else:
            frog = Frog(student_id=student.id, class_id=module_class.id, mod_name=module_class.module.mod_name)
            module_class.frog_list.append(frog)
            UserManager.addMod(student, module_class.module)
            module_class.stud_list.append(student)


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
        total = 0
        for feedback in frog.owner.feedback_list:
            if feedback.mod_name == frog.mod_name:
                total += feedback.marks

        if (total <= 19):
            frog.frog_state = 'egg'
        elif (total <= 39):
            frog.frog_state = 'tadpole'
        elif (total <= 59):
            frog.frog_state = 'frogling'
        elif (total <= 79):
            frog.frog_state = 'froglet'
        else:
            frog.frog_state = 'frog'


class Component(db.Model):
    __tablename__ = 'component'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weightage = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='main')
    feedback_list = db.relationship('Feedback', backref='component', lazy=True)

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

class ComponentManager():
    @staticmethod
    def addSubComp(main_comp, sub_comp):
        total = sub_comp.weightage
        for sub in main_comp.sub_comp_list:
            total += sub.weightage

        if total <= main_comp.weightage:
            main_comp.sub_comp_list.append(sub_comp)
        else:
            return "Error: Total sub-component weightage exceeds main-component's weightage"


class ComponentFactory():
    @staticmethod
    def createComponent(type, name, weightage, **kwargs):
        if type == 'main':
            module_id = kwargs.get('module_id')
            return MainComp(name=name, weightage=weightage, type=type)
            #return MainComp(name=name, weightage=weightage, type=type, module_id=module_id)
        elif type == 'sub':
            main_comp_id = kwargs.get('main_comp_id')
            return SubComp(name=name, weightage=weightage, type=type)
            #return SubComp(name=name, weightage=weightage, type=type, main_comp_id=main_comp_id)
        else:
            raise ValueError(f'ComponentFactory.createComponent(type=\'{type}\'): type must be of \'main\' or \'sub\'')


# Backref(s): component
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    stud_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    inst_id = db.Column(db.Integer, db.ForeignKey(Instructor.id), nullable=False)
    comp_id = db.Column(db.Integer, db.ForeignKey(Component.id), nullable=False)
    mod_name = db.Column(db.String(100), db.ForeignKey(Module.mod_name), unique=True, nullable=False)
    comment = db.Column(db.Text)
    marks = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Feedback('{self.id}', '{self.comment}', '{self.marks}', '{self.date}')"

class FeedbackManager():
    @staticmethod
    def addMarks(feedback, marks):
        if 0 <= marks <= feedback.component.weightage:
            feedback.marks = marks
        else:
            raise ValueError("Marks must not exceed component weightage")

    @staticmethod
    def addComment(feedback, comment):
        if comment:
            feedback.comment = comment
        else:
            raise ValueError("Comment must not be empty")

class iInstructor():
    #  iInstructor.addStudent(modid, selected, stud_info)
    @staticmethod
    def addStudent(module_id, class_name, student_info):
        student = Student.query.filter_by(id=student_info['id']).first()
        if student:
            if student.email == student_info['email'] and student.username == student_info['name']:
                module = Module.query.filter_by(id=module_id).first()
                for mod_class in module.class_list:
                    if mod_class.class_name == class_name:
                        error = ClassManager.addStudent(mod_class, student)
                        if error:
                            return error
                        break
            else:
                return "Error: Student particulars are incorrect"
        else:
            return "Error: Student ID is incorrect"

        db.session.commit()

    @staticmethod
    def addStudentCSV():
        pass

    # iInstructor.addComponent(module, form.main_comps.data)
    @staticmethod
    def addComponent(module, components):
        original = module
        for main in components:
            main_comp = ComponentFactory.createComponent(type='main', name=main['comp_name'],
                                                    weightage=main['weightage'], module_id=module.id)
            error = ModuleManager.addComponent(module, main_comp)

            if error:
                module = original
                return error

            for sub in main['sub_comps']:
                sub_comp = ComponentFactory.createComponent(type='sub', name=sub['comp_name'],
                                                            weightage=sub['weightage'])
                error = ComponentManager.addSubComp(main_comp, sub_comp)

                if error:
                    module = original
                    return error

        db.session.commit()

    @staticmethod
    def viewClass(class_name, module):
        student_list = []
        for mod_class in module.class_list:
            if mod_class.class_name == class_name:
                for student in mod_class.stud_list:
                    stud_info = StudentManager.getGrade(student, module)
                    stud_info['name'] = student.username
                    student_list.append(stud_info)
                break
        return student_list

    @staticmethod
    def addMarks():
        pass

    @staticmethod
    def addMarksCSV():
        pass

class iStudent():
    pass
