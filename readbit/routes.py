from flask import render_template, url_for, flash, redirect, request
from readbit import app, db, bcrypt
from readbit.forms import LoginForm
from readbit.models import User
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) if current_user.type == 'student' else redirect(url_for('module_list'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(url_for(next_page[1:]))
            else:
                return redirect(url_for('dashboard')) if current_user.type == 'student' else redirect(
                    url_for('module_list'))
        else:
            flash(f'Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Personal Dashboard')

@app.route('/module_list')
def module_list():
    return render_template('module_list.html', title='Module List')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')