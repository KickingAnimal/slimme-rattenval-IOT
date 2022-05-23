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
    if 'email' in session:
        loggedIn=True
        loggedInUser=session['email']
    else:
        loggedIn=False
        loggedInUser="niet ingelogd"
    return render_template('home.html', loggedInUser=loggedInUser, loggedIn=loggedIn)

@app.route('/login')
def login():
    return render_template('login.html', pwLabelKleur="black", uLabelKleur="black")

@app.route('/app/login', methods=['POST'])
def login_user():
    # Get the form data
    email = request.form['email']
    password = request.form['password']
    begleider = request.form.get('begleider')
    if begleider == None:
        begleider = False
    if begleider == False:
        # Check if the username exists
        user_id = do_database(f"SELECT COUNT(student_ID) FROM student WHERE email = '{email}'")
        if user_id[0][0] == 0:
            return render_template('login.html', uMessage=" does not exist", pwMessage=" is incorrect", uLabelKleur="red", pwLabelKleur="red")
        if user_id[0][0] == 0:
            return render_template('login.html', uMessage=" does not exist", pwMessage=" is incorrect", uLabelKleur="red", pwLabelKleur="red")
        # Check if the password is correct
        user_password = do_database(f"SELECT password FROM student WHERE email = '{email}'")
        if not bcrypt.check_password_hash(user_password[0][0], password):
            return render_template('login.html', pwMessage=" is incorrect", pwLabelKleur="red")
    else:
        # Check if the username exists
        user_id = do_database(f"SELECT COUNT(ID) FROM begleider WHERE email = '{email}'")
        if user_id[0][0] == 0:
            return render_template('login.html', uMessage=" does not exist", pwMessage=" is incorrect", uLabelKleur="red", pwLabelKleur="red")

        # Check if the password is correct
        user_password = do_database(f"SELECT password FROM begleider WHERE email = '{email}'")
        if not bcrypt.check_password_hash(user_password[0][0], password):
            return render_template('login.html', pwMessage=" is incorrect", pwLabelKleur="red")

    # If the username and password are correct, log the user in and set the session
    session['email'] = email
    session['begleider'] = begleider

    # Return user to home page
    return redirect('/')
    
@app.route('/logout')
def logout():
    # Check if the user is logged in
    if 'email' in session:
        # Remove the username from the session
        session.pop('email', None)
    if 'begleider' in session:
        session.pop('begleider', None)
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
    user_id = do_database(f"SELECT COUNT(student_ID) FROM student WHERE email = '{email}'")
    if user_id[0][0] != 0:
        return render_template('register.html', uMessage=" already exists", uLabelKleur="red")
    # check password not empty and hash the password
    if len(password) == 0:
        return render_template('register.html', pMessage=" must not be empty", pLabelKleur="red")
    elif password != password2:
        return render_template('register.html', pMessage=" is not the same", pLabelKleur="red")
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Add the user to the database
    do_database(f"INSERT INTO student (email, password) VALUES ('{email}','{hashed_password}')")

    # Log the user in
    session['email'] = email

    # Redirect to the home page
    return redirect('/')

@app.route('/valDetail')
def val_detail_none():
    return redirect("/valDetail/0")

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

    if loggedIn:
        valGegevens = do_database(f"SELECT ins.instellingNaam, ins.instellingType, beg.email, st.cijfer, st.periode FROM stage AS st JOIN instelling AS ins ON st.instelling_ID = ins.ID JOIN begleider AS beg ON st.begleider_ID = beg.ID WHERE st.id = {val_ID}")
        print(valGegevens)
        #for i in range(0, len(valGegevens)):
        #    for j in range(0, len(valGegevens[i])):
        #        if valGegevens[i][j] == " " or valGegevens[i][j] == "" or valGegevens[i][j] == "NULL":
        #            y = list(valGegevens[i])
        #            y[j] = "geen info"
        #            valGegevens[i] = tuple(y)
        #if val_ID == 2:
        #    valGegevens = [('valNaam2', '2', "offline")]
        return render_template('valDetail.html', loggedInUser=loggedInUser, loggedIn=loggedIn, valGegevens=valGegevens, val_ID=val_ID)
    elif False:
        valGegevens = [('geen stage info voor een begleider', '')]
        return render_template('valDetail.html', loggedInUser=loggedInUser, loggedIn=loggedIn, valGegevens=valGegevens)
        pass
    elif loggedIn!=True:
        return render_template('nietIngelogd.html')

@app.route('/mijnVallen')
def mijn_vallen():
    if 'email' in session:
        loggedIn=True
        loggedInUser=session['email']
    else:
        loggedIn=False
        loggedInUser="niet ingelogd"
    if loggedIn:

        stageInfo = do_database(f"SELECT si.ID, ins.instellingType, ins.instellingNaam, beg.email,  si.omschrijving FROM stageInfo AS si JOIN instelling AS ins ON si.instelling_ID = ins.ID JOIN begleider AS beg ON si.begleider_ID = beg.ID")
        aantalStage = len(stageInfo)
        gegevens = []
        allGegevens =[]
        for i in range(0, len(stageInfo)):
            (allGegevens.append(list(stageInfo[i])))
            for j in range(0, len(stageInfo[i])):
                (gegevens.append(stageInfo[i][j]))
        print(stageInfo)
        return render_template('mijnVallen.html', loggedInUser=loggedInUser, loggedIn=loggedIn, stageInfo=stageInfo, aantalStage=aantalStage, gegevens=gegevens)

    elif loggedIn!=True:
        return render_template('nietIngelogd.html')

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

@app.route('/edit/<int:boeking_ID>')
def boeking_edit(boeking_ID):
    if 'username' in session:
        huisje = do_database(f"SELECT * FROM boeking WHERE id = {boeking_ID}")
        boekingen = do_database(f"SELECT boekingweek from boeking WHERE huisje_ID = {huisje[0][2]}")
        newboeking = []
        for item in boekingen:
            newboeking.append(item[0])
        return render_template('boeking_edit.html', huisje=huisje, boekingen=newboeking)

if __name__ == '__main__':
    app.run(debug=True)