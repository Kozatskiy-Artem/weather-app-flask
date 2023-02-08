from flask import render_template, redirect, url_for, flash, request
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter

from app.main import main
from app.main.forms import NameForm, GenerateDataForm
from app.main.models import GeneratedData
from generate_data.main import main as generate_data
from generate_data.data import emails_data
from app.main.utils import parse_range_from_paginator


@main.route('/', methods=['POST', 'GET'])
def index():
    """Home page"""
    form = GenerateDataForm()

    if form.validate_on_submit():
        if not GeneratedData.select():
            emails = generate_data(emails_data)
            for name, email in emails:
                data = GeneratedData(name=name, email=email)
                data.save()
            flash('Database filled with test data')
        else:
            flash('Database is not empty')

    return render_template(
        'index.html',
        title='Home page',
        current_time=datetime.utcnow(),
        form=form
    )


@main.route('/test_data/show')
def show_test_data():
    """Show test data information"""
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    data = GeneratedData.select()
    pagination = Pagination(page=page, total=data.count(), search=search, record_name='users')
    start, stop = parse_range_from_paginator(pagination.info)
    return render_template(
        'main/show_test_data.html',
        title='Test data',
        data=data[start:stop],
        pagination=pagination,
    )


@main.route('/test_data/edit/<int:user_id>')
def edit_test_data(user_id):
    """Edit user"""
    user = GeneratedData.select().where(GeneratedData.id == user_id).first()
    form = NameForm()
    if not user:
        flash(f'User with id: {user_id} not found! You can add user in this form.')
        return redirect(url_for('main.add_test_data'))
    form.id.data = user.id
    form.id.label.text = ''
    form.name.label.text = 'Edit this name'
    form.email.label.text = 'Edit this email'

    form.name.data = user.name
    form.email.data = user.email
    form.submit.label.text = 'Edit'
    print('*' * 20)
    return render_template(
        'main/edit_test_data.html',
        title=f'Edit user {user.name}',
        form=form,
    )


@main.route('/test_data/update', methods=['POST'])
def update_email():
    """Update test user from form"""
    form = NameForm()

    if form.validate_on_submit():
        user_id = form.id.data
        user_name = form.name.data
        user_email = form.email.data

        user = GeneratedData.select().where(GeneratedData.id == user_id).first()
        user.name = user_name
        user.email = user_email
        try:
            user.save()
            flash(f'{user_name} updated')
        except Exception:
            flash(f'Email already added into database')

    return redirect(url_for('main.index'))


@main.route('/add_test_data', methods=['POST', 'GET'])
def add_test_data():
    """Add name and email form page"""
    form = NameForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = f'Test user with name {name} already registered'
        if not GeneratedData.select().where(GeneratedData.email == email):
            user = GeneratedData(name=name, email=email)
            user.save()
            message = f'Test user with name {name} just registered'

        flash(message)
        return redirect(url_for('main.add_test_data'))

    return render_template(
        'main/add_test_data.html',
        title='Add test data',
        form=form
    )


@main.route('/test_data/delete', methods=['POST'])
def delete_test_data():
    """Delete selected data"""
    if request.method == 'POST':
        message = 'Deleted: '
        selectors = list(map(int, request.form.getlist('selectors')))

        if not selectors:
            flash('Nothing to delete')
            return redirect(url_for('main.show_test_data'))

        for selector in selectors:
            user = GeneratedData.get(GeneratedData.id == selector)
            message += f'{user.email} '
            user.delete_instance()

        flash(message)
        return redirect(url_for('main.show_test_data'))
