##  Begin Standard Imports
import requests, mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

##  Begin Local Imports
import resources

app = Flask(__name__, template_folder=str(resources.CONST_FRONTEND_DIR), static_folder=str(resources.CONST_ROOT_DIR))

app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Bcrypt and LoginManager
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MySQL connection setup
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change to your MySQL username
            password='password',  # Change to your MySQL password
            database='ai_learning_hub'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# gen
# trending_repos = fetch_trending_repos()
def fetch_trending_repos():
    response = requests.get(resources.GITHUB_API_URL, headers=resources.HEADERS)
    if response.status_code == 200:
        data = response.json()["items"][:10]  # Get top 10 trending AI repos
        repos = []
        
        for repo in data:
            # Get repo details
            repo_details = {
                "name": repo["name"],
                "url": repo["html_url"],
                "description": repo["description"],
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "contributors_url": repo["contributors_url"]
            }
            
            # Fetch top contributors
            contributors = requests.get(repo["contributors_url"], headers=resources.HEADERS)
            if contributors.status_code == 200:
                repo_details["contributors"] = [contributor["login"] for contributor in contributors.json()[:5]]  # Get top 5
            else:
                repo_details["contributors"] = []

            repos.append(repo_details)
        
        return repos
    return []

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
    
@app.route("/")
def root():
    return redirect(url_for('home'))

# Home Route
@app.route("/home")
@login_required
def home():
    print(f"Logged in user: {current_user.username} - Role: {current_user.role}")  # Debugging line
    return render_template("home.html", username=current_user.username)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
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

# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    logout_user()
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
        print(f"Loaded user: {username} - Role: {role}")  # Debugging line
        return User(userid, username, email, password, role, first_name, last_name, institute_name)
    return None

@app.route("/trending")
@login_required
def trending_page():
    trending_repos = fetch_trending_repos()
    return render_template("trending.html", repos=trending_repos)

# Submit Resource Route (for logged-in users)
@app.route("/submit_resource", methods=["GET", "POST"])
@login_required
def submit_resource():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']  
        description = request.form['description']
        author_name = request.form['author_name']
        user_id = current_user.userid  # Get the logged-in user's ID

        # Insert the resource into the database with 'pending' status
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(""" 
            INSERT INTO resources (title, link, category, description, author_name, user_id, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
        """, (title, url, category, description, author_name, user_id, 'pending'))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Resource submitted successfully. Waiting for approval!', 'success')
        return redirect(url_for('home'))

    return render_template('submit_resource.html')

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('home'))

    # Fetch pending resources or other admin-specific content
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM resources WHERE status = 'pending'")
    resources = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin_dashboard.html', resources=resources)

# Approve Resource Route
@app.route("/admin/approve_resource/<int:resource_id>")
@login_required
def approve_resource(resource_id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('home'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE resources SET status = 'approved' WHERE resource_id = %s", (resource_id,))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Resource approved!', 'success')
    return redirect(url_for('admin_dashboard'))

# Reject Resource Route
@app.route("/admin/reject_resource/<int:resource_id>")
@login_required
def reject_resource(resource_id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('home'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE resources SET status = 'rejected' WHERE resource_id = %s", (resource_id,))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Resource rejected!', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
