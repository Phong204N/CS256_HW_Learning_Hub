from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Bcrypt and LoginManager
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MySQL connection setup
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Change to your MySQL username
        password='password',  # Change to your MySQL password
        database='ai_learning_hub'
    )
    return connection

# User Model
class User(UserMixin):
    def __init__(self, userid, username, email, password, role, first_name, last_name, institute_name):
        self.userid = userid
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.institute_name = institute_name

    def get_id(self):
        return str(self.userid)  # Flask-Login needs the user id to be a string

# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # Hash the password
        role = 'user'  # Default role is user
        institute_name = request.form['institute_name']

        # Check if email or username already exists
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, username))
        user = cursor.fetchone()

        if user:
            flash("Email or Username already exists!", "danger")
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO users (first_name, last_name, email, password, role, institute_name, username) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (first_name, last_name, email, hashed_password, role, institute_name, username))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        # Check if user exists by username or email
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s OR username = %s', (username_or_email, username_or_email))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):  # Use bcrypt to check the password
            user_obj = User(user['userid'], user['username'], user['email'], user['password'], user['role'],
                            user['first_name'], user['last_name'], user['institute_name'])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

        cursor.close()
        connection.close()

    return render_template('login.html')

# Home Route
@app.route("/home")
@login_required
def home():
    return render_template("home.html", username=current_user.username)

# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# User Loader
@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if user_data:
        userid, username, email, password, role, first_name, last_name, institute_name = user_data
        return User(userid, username, email, password, role, first_name, last_name, institute_name)
    return None

if __name__ == "__main__":
    app.run(debug=True)
