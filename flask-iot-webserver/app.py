from flask import Flask, render_template, redirect, request, session, jsonify
from flask_bcrypt import Bcrypt
from database import *
from datetime import datetime, timedelta
import string

bcrypt = Bcrypt()
app = Flask(__name__)

# Set the secret key (needed for session)
# Normally this would generate a random key like this:
# >>> import os
# >>> os.urandom(24)
# But I'm using a fixed key for this example

app.secret_key = "secret"

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url)
        
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
        valGegevens = do_database(f"SELECT vi.*, st.statusNaam FROM valInfo AS vi JOIN users AS usr ON vi.user_ID = usr.user_ID JOIN status AS st ON vi.valStatus = st.status_ID WHERE email = '{loggedInUser}' AND vi.val_ID = '{val_ID}'")
        valStatus = valGegevens[0][4]
        return render_template('valDetail.html', loggedInUser=loggedInUser, loggedIn=loggedIn, valGegevens=valGegevens, val_ID=val_ID, valStatus=valStatus)
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

        vallenInfo = do_database(f"SELECT vi.*, st.statusNaam FROM valInfo AS vi JOIN users AS usr ON vi.user_ID = usr.user_ID JOIN status AS st ON vi.valStatus = st.status_ID WHERE email = '{loggedInUser}'")
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

@app.route('/vallen/edit')  # complete bullshit for now.
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
        resetDatabase()
        return render_template('edit.html', loggedInUser=loggedInUser, loggedIn=loggedIn, stageInfo=stageInfo, aantalStage=aantalStage)

    elif loggedIn!=True:
        return render_template('nietIngelogd.html')

    return redirect('/404')

@app.route('/edit/<int:val_ID>')    # complete bullshit for now x2.
def val_edit2(val_ID):
    if 'email' in session:
        val = do_database(f"SELECT * FROM vallen WHERE val_ID = {val_ID} and user_ID = {user_ID}")
        boekingen = do_database(f"SELECT boekingweek from boeking WHERE huisje_ID = {huisje[0][2]}")
        newboeking = []
        for item in boekingen:
            newboeking.append(item[0])
        return render_template('boeking_edit.html', val=val, boekingen=newboeking)
    
    return redirect('/404')

def validate_mac(mac):
    return len(mac) == 12 and all(i in string.hexdigits for i in mac)

def existing_mac(mac):
    exists = do_database(f"SELECT COUNT(valMac) FROM valInfo WHERE valMac = '{mac}'")
    return bool(exists[0][0])

def validate_val_id(val_ID):
    validate = [(1,)]
    if len(str(val_ID)) > 12 or not all(i in string.digits for i in str(val_ID)):
        validate = [(0,)]
    return bool(validate[0][0])

def existing_val_id(val_ID):
    validate = do_database(f"SELECT COUNT(val_ID) FROM valInfo WHERE val_ID = '{val_ID}'")
    return bool(validate[0][0])

def resetDatabase():
    curTime = datetime.utcnow().timestamp()
    do_database(f"DELETE FROM valConnect WHERE timeStamp < {curTime};")


@app.route('/app/connect', methods=['POST'])
def val_connectie():
    valMac = request.json['valMac']
    val_ID = request.json['val_ID']
    timeStamp = datetime.utcnow()
    timeStamp = (timeStamp + timedelta(minutes=5)).timestamp()
    if not request.json:
        return jsonify({ "error": "invalid-json: request must be in json formatting" })
    if not validate_mac(valMac):
        return jsonify({ "error": "invalid-mac: mac must be in '1234567890AB' format" })
    if existing_mac(valMac):
        return jsonify({ "error": "invalid-mac: valMac already exists" })
    if not validate_val_id(val_ID):
        return jsonify({"error": "invalid-valId: invalid format: must be in 0 - 123456789012 format. only numeric."})
    if existing_val_id(val_ID):
        return jsonify({"error": "valId already exists"})
    
    print("val_ID & valMac:", val_ID, valMac)
    do_database(f"INSERT INTO valConnect (val_ID, valMac, timeStamp) VALUES ('{val_ID}', '{valMac}', '{timeStamp}')")
    inserted = do_database(f"SELECT * FROM valConnect WHERE val_ID == '{val_ID}' AND valMac == '{valMac}'")
    print("inserted:",inserted)
    if inserted == []:
        inserted = [(None,None)]
    print("'inserted':",inserted)
    database_ID = inserted[0][0]
    databaseMac = inserted[0][1]

    print("val_ID & valMac:", val_ID,valMac,"database_ID & databaseMac:", database_ID, databaseMac)
    if int(val_ID) == database_ID and valMac == databaseMac:
        return jsonify({ "error": "OK: no errors caught" })
    else:
        return jsonify({"error": "ERROR!: something went wrong in the database"})

@app.route('/app/valUpdate', methods=['POST'])
def val_update():
    valMac = request.json['valMac']
    val_ID = request.json['val_ID']

    if not request.json:
        return jsonify({ "error": "invalid-json: request must be in json formatting" })
    if not validate_mac(valMac):
        return jsonify({ "error": "invalid-mac: mac must be in '1234567890AB' format" })
    if not existing_mac(valMac):
        return jsonify({ "error": "invalid-valMac: valMac does not exists" })
    if not validate_val_id(val_ID):
        return jsonify({"error": "invalid-valId: invalid format: must be in 0 - 123456789012 format. only numeric."})
    if not existing_val_id(val_ID):
        return jsonify({"error": "invalid-valId: valId does not exist"})


    print(val_ID,valMac)
    return jsonify({ "error": "Nothing happened" })

@app.route('/valToevoegen', methods=['GET', 'POST'])
def val_toevoegen():
    pass

@app.route('/404')
def fourOfour_page():
    return render_template('404.html')
@app.errorhandler(404)
def error_page(e):
    return redirect('/404')

if __name__ == '__main__':
    privKey = 'ssl/kickinganimal.nl/privatekey.pem'
    cert = 'ssl/kickinganimal.nl/cert.pem'
    def sslContext():
        return (cert, privKey)


    app.run(debug=True, host='0.0.0.0',port=5000, ssl_context=sslContext())