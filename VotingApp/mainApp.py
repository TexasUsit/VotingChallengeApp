from __future__ import print_function # In python 2.7
import sys, os, operator
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
import forms
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import User, Tickers, Transactions
from VotingApp import db, app, login_manager
from yahoo_finance import Share

basedir = os.path.abspath(os.path.dirname(__file__))

# app = Flask(__name__)
# app.config['SECRET_KEY'] = '~t\x86\xc9\x1ew\x8bOcX\x85O\xb6\xa2\x11kL\xd1\xce\x7f\x14<y\x9e'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'usit.db')
# db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def index():
    form = forms.LoginForm()
    setForm = forms.SignUpForm()
    if request.method=='POST' and request.form['btn'] == 'log in':
        email = form.email.data
        password = form.password.data
        user = User.get_by_email(email)
        # print(user, sys.stderr)
        # print(user.password, sys.stderr)
        if user is not None and user.check_password(password):
            login_user(user, False)
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect Email or Password")
            #return redirect(url_for('index'))
    elif request.method=='POST' and request.form['btn'] == 'Sign Up':
        if validateSignUp():
            user = User(email=setForm.setEmail.data,
                        firstName=setForm.firstName.data,
                        lastName=setForm.lastName.data,
                        password = setForm.setPassword.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('index.html', form=form, setForm=setForm, login="login-hide", signup="signup-show", login_active="", signup_active="active")
    return render_template('index.html', form=form, setForm=setForm, login="login", signup="signup", login_active="active", signup_active="")

def validateSignUp():
    setForm = forms.SignUpForm()
    ok = True
    if User.query.filter_by(email=setForm.setEmail.data).first():
        flash("User with email already exists")
        ok = False
    if setForm.setPassword.data != setForm.setPassword2.data:
        flash("Passwords do NOT match")
        ok = False
    if (setForm.setEmail.data)[-10:] != "utexas.edu":
        flash("Must use utexas.edu email")
        ok = False
    if not setForm.setEmail.data or not setForm.firstName.data or not setForm.lastName.data or not setForm.setPassword.data:
        flash("All fields are required")
        ok = False
    return ok


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user, sys.stderr)
    """Getting Position on Leaderboard"""
    allUsers = User.query.all()
    returns = {}
    for student in allUsers:
        totalStocks = len(student.stocks)
        ret = 0
        activeStocks = student.stocks

        "Calculates returns on active positions"
        for stock in activeStocks:
            ret += (float(Share(stock.ticker).get_price()) - stock.startingPrice)/stock.startingPrice

        "Calculates returns on sold positions"
        userTransactions = Transactions.query.filter_by(user_id=student.id)
        totalStocks += userTransactions.count()
        for trans in userTransactions:
            ret += (trans.end_price - trans.ticker.startingPrice)/trans.ticker.startingPrice
        if totalStocks is not 0:
            returns[student.id] = ret/totalStocks
        else:
            returns[student.id] = 0
    "Sorts the dictionary by returns"
    ret_tups = sorted(returns.items(), key=operator.itemgetter(1), reverse=True)
    "Finds leadboard position"
    standing = 1
    for userid, ret in ret_tups:
        if userid is current_user.id:
            break
        standing += 1

    """Finished getting position"""
    prices = {}
    for stock in current_user.stocks:
        prices[stock.ticker] = float("%.2f" % float(Share(stock.ticker).get_price()))
    return render_template('dashboard.html', stocks=current_user.stocks, prices=prices, totalReturn=returns[current_user.id], standing=standing)

@app.route('/exitPosition/<int:exitIndex>')
def exitPosition(exitIndex):
    #print(current_user.id)  #user_id
    #print(current_user.stocks[exitIndex-1].id)  #ticker_id
    user = User.query.filter_by(id=current_user.id).first()
    print(current_user.stocks.pop(exitIndex-1))
    db.session.commit()
    """user = User(email=setForm.setEmail.data,
                firstName=setForm.firstName.data,
                lastName=setForm.lastName.data,
                password = setForm.setPassword.data)
    db.session.add(user)
    db.session.commit()"""
    return redirect(url_for('dashboard'))


@app.route('/loggedin')
def loggedin():
    return render_template('loggedin.html')
if __name__ == '__main__':
    app.run(debug=True)
