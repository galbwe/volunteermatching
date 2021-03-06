from volunteermatching import app, db
from volunteermatching.decorators import requires_roles
from .models import User
from .forms import LoginForm, CreateUser, EditUser, DeleteUser
from flask import render_template, request, flash, url_for, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = User.query.filter_by(email=form.email.data).first()
        if email is None or not email.verify_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(email, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page) != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin/create_user', methods=["GET", "POST"])
@login_required
@requires_roles('Admin','User')
def create_user():
    form = CreateUser()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('auth/create_user.html', title='Create User',
                           form=form)


@app.route('/admin/users')
@login_required
@requires_roles('Admin','User')
def users():
    users = User.query.all()
    return render_template('auth/users.html', title='Admin Users', users=users)


@app.route('/admin/edit_user/<id>', methods=["GET", "POST"])
@login_required
@requires_roles('Admin','User')
def edit_user(id):
    user = User.query.filter_by(id=id).first()
    form = EditUser()
    if form.validate_on_submit():
        user.email = form.email.data
        user.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin'))
    elif request.method == "GET":
        form.email.data = user.email
    return render_template('auth/edit_user.html', title='Edit User', form=form)


@app.route('/admin/delete_user/<id>', methods=["GET", "POST"])
@login_required
@requires_roles('Admin','User')
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    form = DeleteUser()
    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('auth/delete_user.html', title='Delete User',
                           form=form, user=user)
