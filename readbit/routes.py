from flask import render_template, url_for, flash, redirect, request
from readbit import *
from readbit.forms import *
from readbit.models import *
from flask_login import login_user, current_user, logout_user, login_required
import typing, logging, pprint
from flask import request

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])

def login():
    if current_user.is_authenticated:
        if current_user.type == 'student':
            return redirect(url_for('student_dashboard'))
        return redirect(url_for('module_list'))
        
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            if next_page:
                return redirect(url_for(next_page[1:]))

            else:
                return redirect(url_for('student_dashboard')) if current_user.type == 'student' else redirect(
                    url_for('module_list'))

        else:
            flash(f'Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/module_list')
def module_list():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))

    return render_template('module_list.html', title='Module List', modulelist=current_user.mod_list)



@app.route('/view_component_scores')
def view_component_scores():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))
    module_name = "Module"
    component_name = "Component"
    return render_template('view_component_scores.html', title='View Component Scores', module_name=module_name, component_name=component_name)

@app.route('/manage_feedback')
def manage_feedback():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))
    module_name: typing.List[str] = "Module"
    component_name: typing.List[str] ="Component"
    teaching_classlist: typing.List[str] = ['T1','T2','T3','T4','T5', 'T6']
    return render_template('manage_feedback.html', title='Manage Feedback', module_name=module_name, component_name=component_name, teaching_classlist=teaching_classlist)


@app.route('/manage_class')
def manage_class():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))

    teaching_classlist: typing.List[str] = ['T1','T2','T3','T4','T5', 'T6']
    return render_template('manage_class.html', title='Manage Class', teaching_classlist=teaching_classlist)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

"""
Added by Dylan Woo
"""
@app.route('/manage_module')
def manage_module():
    if current_user.type == 'student':
            return redirect(url_for('student_dashboard'))

    if request.args.get('success'):
        flash('Component added successfully.', 'success')

    modid = request.args.get('mod_id')
    module = Module.query.filter_by(id=modid).first()
    comp_list = []
    for comp in module.comp_list:
        comp_list.append(comp)
        for sub in comp.sub_comp_list:
            comp_list.append(sub)

    return render_template('manage_module.html', title='Manage Module', module=module, components=comp_list)

@app.route('/add_student_manually')
def add_student_manually():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))
    return render_template('add_student_manually.html', title='Add Student Manually')

@app.route('/student_dashboard')
def student_dashboard():
    student_frog_state = url_for('static', filename='frog_state_1.png')

    context = {
        'student_frog_state': student_frog_state
    }
    return render_template('student_dashboard.html', title='Student Dashboard', context=context)

@app.route('/class_dashboard')
def class_dashboard():
    # if current_user.type == 'student':
    #     return redirect(url_for('student_dashboard'))
    classlist: typing.List[int] = [1,2,3,4,5,6]
    return render_template('class_dashboard.html', title='Class Dashboard', classlist=classlist)

@app.route('/add_marks')
def add_marks():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))
    teaching_classlist: typing.List[str] = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
    module = 'Module'
    component = 'Quiz 1'
    return render_template('add_marks.html', title='Add Marks',teaching_classlist=teaching_classlist, module=module, component=component)

@app.route('/view_student')
def view_student():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))
    student = 'Studentname'
    student_id = 190000
    return render_template('view_student.html', title='View Student Dashboard', student=student, student_id=student_id)

@app.route('/add_component', methods=['GET', 'POST'])
def add_component():
    if current_user.type == 'student':
        return redirect(url_for('student_dashboard'))

    form = AddComponentForm()
    modid = request.args.get('mod_id')
    module = Module.query.filter_by(id=modid).first()

    if form.add_main.data:
        form.main_comps.append_entry()
        return render_template('add_component.html', title='Add Component', form=form, modid=modid)

    for main in form.main_comps:
        if main.add_sub.data:
            main.sub_comps.append_entry()
            return render_template('add_component.html', title='Add Component', form=form, modid=modid)

    if form.validate_on_submit():
        error = iInstructor.addComponent(module, form.main_comps.data)
        if error:
            flash(error, 'danger')
        else:
            return redirect(url_for('manage_module', mod_id=modid, success=True))

    return render_template('add_component.html', title='Add Component', form=form, modid=modid)