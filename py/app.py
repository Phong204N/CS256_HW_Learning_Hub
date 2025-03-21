##  Begin Standard Imports
import mysql, os
from openai import OpenAI
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

##  Begin Local Imports
import resources
from models import Bookmark, Resource
from models import db # Import the db and Resource class

# Initialize the Flask app

# Initialize the Flask app
app = Flask(__name__, template_folder=str(resources.CONST_FRONTEND_DIR), static_folder=str(resources.CONST_ROOT_DIR))
# Configure the database URI (make sure it's correct for your environment)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/ai_learning_hub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Set a secret key for session management

db.init_app(app)  # Initialize the database
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MY PRIVATE KEY.  
client = OpenAI(
  api_key="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"
)


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

# Gen
def fetch_trending_repos():
    response = requests.get(resources.GITHUB_API_URL, headers=resources.HEADERS)
    if response.status_code == 200:
        data = response.json()["items"][:10]  # Get top 10 trending AI repos
        repos = []
        
        for repo in data:
            repo_details = {
                "name": repo["name"],
                "url": repo["html_url"],
                "description": repo["description"],
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "contributors_url": repo["contributors_url"]
            }
            
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
    def __init__(self, id, username, email, password, role, first_name, last_name, institute_name):
        self.id = id  # Renamed from userid to id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.institute_name = institute_name

    def get_id(self):
        return str(self.id)  # Flask-Login needs the user id to be a string


@app.route("/")
def root():
    return redirect(url_for('home'))

# Home Route
@app.route("/home")
@login_required
def home():
    return render_template("home.html", username=current_user.username)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

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

        insert_stmt = "INSERT INTO users (first_name, last_name, email, password, role, institute_name, username) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # data = (first_name, last_name, email, hashed_password, role, institute_name, username)
        # cursor.execute(insert_stmt, data)

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
    cursor.execute("SELECT * FROM users WHERE userid = %s", (user_id,))  # This is correct because the `userid` is being used here to query the DB.
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()

    if user_data:
        print(user_data)
        # Destructure the data to match the User class constructor
        userid, first_name, last_name, email, password, role, institute_name, username = user_data
        return User(userid, username, email, password, role, first_name, last_name, institute_name)  # Pass `userid` to `User`
    return None


@app.route("/trending")
@login_required
def trending():
    trending_repos = fetch_trending_repos()
    return render_template("trending.html", repos=trending_repos)

@app.route("/chatbot")
@login_required
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    try:
        # New API call format (openai>=1.0.0)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        bot_message = response.choices[0].message.content
        return jsonify({"message": bot_message})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"})

@app.route('/submit_resource', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in before submitting a resource
def submit_resource():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form['title']
            description = request.form['description']
            link = request.form['link']  # Note: use 'url' for the field name in the form
            category = request.form['category']
            author_name = request.form['author_name']

            # Check if user is authenticated
            if current_user.is_authenticated:
                user_id = current_user.id  # Access current user ID
            else:
                flash('You need to be logged in to submit a resource.', 'danger')
                return redirect(url_for('login'))  # Redirect to login page if not authenticated

            # Create a new resource entry
            new_resource = Resource(
                title=title,
                description=description,
                link=link,
                category=category,
                author_name=author_name,
                user_id=user_id,  # Assign user_id to the resource
                status='pending'
            )

            db.session.add(new_resource)
            db.session.commit()

            flash('Resource submitted successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to home or other page after success

        except KeyError as e:
            flash(f"Missing form field: {str(e)}", 'danger')
            return redirect(url_for('submit_resource'))  # Redirect back if any field is missing

    return render_template('submit_resource.html')

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        print(vars(current_user).items())
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

# User's Resources View
@app.route("/my_resources")
@login_required
def my_resources():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM resources WHERE user_id = %s", (current_user.id,))
    resources = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("my_resources.html", resources=resources)


@app.route('/save_bookmark', methods=['POST'])
def save_bookmark():
    # Get the data from the POST request
    data = request.get_json()

    user_id = data.get('user_id')
    resource_id = data.get('resource_id')

    try:
        # Create a new Bookmark object
        new_bookmark = Bookmark(user_id=user_id, resource_id=resource_id)

        # Add the new bookmark to the session and commit
        db.session.add(new_bookmark)
        db.session.commit()

        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/my_bookmarks')
def my_bookmarks():
    # Fetch bookmarks for the current user, joining the resource to get its details
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).join(Resource).all()
    return render_template('my_bookmarks.html', bookmarks=bookmarks)


@app.route('/delete_bookmark/<int:bookmark_id>', methods=['GET'])
def delete_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    if bookmark.user_id != current_user.id:
        flash('You do not have permission to delete this bookmark.', 'danger')
        return redirect(url_for('my_bookmarks'))

    db.session.delete(bookmark)
    db.session.commit()
    flash('Bookmark deleted successfully!', 'success')
    return redirect(url_for('my_bookmarks'))


if __name__ == "__main__":
    app.run(debug=True)
