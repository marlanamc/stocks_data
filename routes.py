from flask import render_template, url_for, flash, redirect, request, Response, abort, jsonify, send_file, make_response
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from app.top_comp import do_plot
from io import BytesIO
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')


db.create_all()



@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Profile', form=form)

@app.route('/top_comp')
def plot_html():
    figfile = do_plot()
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    return render_template('sandp.html', result=result)

@app.route('/gains', methods=("POST", "GET"))
def get_gains():
    json = pd.read_json('https://financialmodelingprep.com/api/v3/gainers?apikey=a5bee999241cc8d8f9f2281f838312e0')
    json.to_json('dataframe.json')
    json.index += 1
    df = json.rename({'ticker': 'Ticker', 'changes': 'Change', 'price': 'Price', 'changesPercentage': 'Change %', 'companyName': 'Company Name'}, axis=1)
    return render_template('gainers.html', tables=[df.to_html(classes='data', header="true")])

@app.route('/lose', methods=("POST", "GET"))
def get_losses():
    json = pd.read_json('https://financialmodelingprep.com/api/v3/losers?apikey=a5bee999241cc8d8f9f2281f838312e0')
    json.to_json('dataframe.json')
    json.index += 1
    df = json.rename({'ticker': 'Ticker', 'changes': 'Change', 'price': 'Price', 'changesPercentage': 'Change %', 'companyName': 'Company Name'}, axis=1)
    return render_template('losers.html', tables=[df.to_html(classes='data', header="true")])

if __name__ == "__main__":
    app.run()


