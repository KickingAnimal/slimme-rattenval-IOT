from flask import Flask, render_template, redirect, request, session
from flask_bcrypt import Bcrypt
from database import *

bcrypt = Bcrypt()
app = Flask(__name__)

# Set the secret key (needed for session)
# Normally this would generate a random key like this:
# >>> import os
# >>> os.urandom(24)
# But I'm using a fixed key for this example

app.secret_key = "secret"

@app.route('/')
def home():
    if 'email' in session:  # if session exists give params.
        loggedIn=True
        loggedInUser=session['email']
    else:                   # else give other params.
        loggedIn=False
        loggedInUser="niet ingelogd"
    return render_template('home.html', loggedInUser=loggedInUser, loggedIn=loggedIn)   # return home with params based on logged in or not

@app.route('/login')
def login():
    return render_template('login.html', pwLabelKleur="black", eLabelKleur="black")

@app.route('/app/login', methods=['POST'])
def login_user():
    # Get the form data
    email = request.form['email']
    password = request.form['password']

    # Check if the email exists
    user_id = do_database(f"SELECT COUNT(user_ID) FROM users WHERE email = '{email}'")
    if user_id[0][0] == 0:
        return render_template('login.html', eMessage=" does not exist", pwMessage=" is incorrect", eLabelKleur="red", pwLabelKleur="red")
    # Check if the password is correct
    user_password = do_database(f"SELECT password FROM users WHERE email = '{email}'")
    if not bcrypt.check_password_hash(user_password[0][0], password):
        return render_template('login.html', pwMessage=" is incorrect", pwLabelKleur="red")

    # If the email and password are correct, log the user in and set the session
    session['email'] = email
    # Return user to home page
    return redirect('/')
    
@app.route('/logout')
def logout():
    # Check if the user is logged in
    if 'email' in session:
        # Remove the email from the session
        session.pop('email', None)
    return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html', uLabelKleur="black")

@app.route('/app/register', methods=['POST'])
def register_user():
    # Get the form data
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']

    # Check if the first name already exists
    user_id = do_database(f"SELECT COUNT(user_ID) FROM users WHERE email = '{email}'")
    if user_id[0][0] != 0:
        return render_template('register.html', eMessage=" already registered", eLabelKleur="red")
    # check password not empty and hash the password
    if len(password) == 0:
        return render_template('register.html', pMessage=" must not be empty", pLabelKleur="red")
    elif password != password2:
        return render_template('register.html', pMessage=" is not the same", pLabelKleur="red")
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # Add the user to the database
        do_database(f"INSERT INTO users (email, password) VALUES ('{email}','{hashed_password}')")
        # Log the user in
        session['email'] = email
        # Redirect to the home page
        return redirect('/')
    return redirect('/register')

@app.route('/valDetail')
def val_detail_none():
    return render_template('nietGeldig.html')

@app.route('/valDetail/<int:val_ID>')
def val_details(val_ID):
    print(val_ID)
    if 'email' in session:
        loggedIn=True
        loggedInUser=session['email']
    else:
        loggedIn=False
        loggedInUser="niet ingelogd"

    if val_ID == 0:
        return render_template('nietGeldig.html')

    if loggedIn:    #rewrite based on new database struct.
        valGegevens = do_database(f"SELECT vi.* FROM valInfo AS vi JOIN users AS usr ON vi.user_ID = usr.user_ID WHERE email = '{loggedInUser}' AND vi.val_ID = {val_ID}")
        #for i in range(0, len(valGegevens)):
        #    for j in range(0, len(valGegevens[i])):
        #        if valGegevens[i][j] == " " or valGegevens[i][j] == "" or valGegevens[i][j] == "NULL":
        #            y = list(valGegevens[i])
        #            y[j] = "geen info"
        #            valGegevens[i] = tuple(y)
        #if val_ID == 2:
        #    valGegevens = [('valNaam2', '2', "offline")]
        print(valGegevens)
        return render_template('valDetail.html', loggedInUser=loggedInUser, loggedIn=loggedIn, valGegevens=valGegevens, val_ID=val_ID)
    elif loggedIn!=True:
        return render_template('nietIngelogd.html')
    return redirect('/404')

@app.route('/mijnVallen')
def mijn_vallen():
    if 'email' in session:
        loggedIn=True
        loggedInUser=session['email']
    else:
        loggedIn=False
        loggedInUser="niet ingelogd"
    if loggedIn:

        vallenInfo = do_database(f"SELECT vi.* FROM valInfo AS vi JOIN users AS usr ON vi.user_ID = usr.user_ID WHERE email = '{loggedInUser}'")
        aantalVallen = len(vallenInfo)
        gegevens = []
        allGegevens =[]
        for i in range(0, len(vallenInfo)):
            (allGegevens.append(list(vallenInfo[i])))
            for j in range(0, len(vallenInfo[i])):
                (gegevens.append(vallenInfo[i][j]))
        print(vallenInfo)
        return render_template('mijnVallen.html', loggedInUser=loggedInUser, loggedIn=loggedIn, vallenInfo=vallenInfo, aantalVallen=aantalVallen, gegevens=gegevens)
    elif loggedIn!=True:
        return render_template('nietIngelogd.html')
    return redirect('/404')

@app.route('/vallen/edit')
def val_edit():
    if 'email' in session:
        loggedIn=True
        loggedInUser=session['email']
    else:
        loggedIn=False
        loggedInUser="niet ingelogd"

    if loggedIn:
        stageInfo = do_database(f"SELECT si.ID, si.instelling_ID, ins.instellingType, ins.instellingNaam, si.begleider_ID, beg.email, beg.achternaam,  si.omschrijving FROM stageInfo AS si JOIN instelling AS ins ON si.instelling_ID = ins.ID JOIN begleider AS beg ON si.begleider_ID = beg.ID")
        aantalStage = len(stageInfo)
        return render_template('edit.html', loggedInUser=loggedInUser, loggedIn=loggedIn, stageInfo=stageInfo, aantalStage=aantalStage)

    elif loggedIn!=True:
        return render_template('nietIngelogd.html')

    return redirect('/404')

@app.route('/edit/<int:val_ID>')
def val_edit2(val_ID):
    if 'email' in session:
        val = do_database(f"SELECT * FROM vallen WHERE val_ID = {val_ID} and user_ID = {user_ID}")
        boekingen = do_database(f"SELECT boekingweek from boeking WHERE huisje_ID = {huisje[0][2]}")
        newboeking = []
        for item in boekingen:
            newboeking.append(item[0])
        return render_template('boeking_edit.html', val=val, boekingen=newboeking)
    
    return redirect('/404')

@app.route('/404')
def fourOfour_page():
    return render_template('404.html')
@app.errorhandler(404)
def error_page(e):
    return redirect('/404')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)