from flask import Flask, render_template, redirect, request, session, jsonify
from flask_bcrypt import Bcrypt
import string

bcrypt = Bcrypt()
app = Flask(__name__)
app.secret_key = "secret"

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        url = url.replace(':8080', ':4430', 1)
        return redirect(url)

@app.route('/404')
def fourOfour_page():
    return render_template('404.html')
@app.errorhandler(404)
def error_page(e):
    return redirect('/404')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',port=4000)