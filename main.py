from flask import Flask, render_template, jsonify, request, redirect
from database import engine
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask import Flask, render_template, jsonify, request, redirect, abort
from flask_login import login_user, current_user
from flask import redirect, url_for
from datetime import datetime

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = 'fmweo9h094832htg'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Define a user loader function
@login_manager.user_loader
def load_user(user_id):
    # You can use user_id to load the user from the database
    user_data = get_user_by_id(user_id)
    if user_data:
        user = User(user_data[0], user_data[1], user_data[2])
        return user
    return None

# A sample function to get user data by username and role
def get_user_by_username(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        return result.fetchone()

def get_user_by_role(role):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE role = :role"), {"role": role})
        return result.fetchone()

#admin dashboard
# Admin login page (GET request)
@app.route('/admin/login', methods=['GET'])
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return 'Logged out successfully'

# Admin login handling (POST request)
@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form['username']
    password = request.form['password']

    # Retrieve the user from the database by username
    user = get_user_by_username(username)

    if user and user[2] == password:  # Compare plaintext passwords (not recommended)
        # Authentication successful
        # Create a User object and log in the user
        user_obj = User(user[0], username, user[1])  # Replace with appropriate column indices
        login_user(user_obj)

        return redirect('/admin/dashboard')  # Redirect to the admin dashboard after successful login
    else:
        return 'Invalid credentials', 401


@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required  # Protect the admin dashboard route with authentication
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('action') == 'add':
            # Handle job addition here (insert job data into the database)
            title = request.form.get('title')
            description = request.form.get('description')
            spaces = request.form.get('spaces')
            location = request.form.get('location')
            company = request.form.get('company')
            date_str = request.form.get('date')

            if not date_str:
                date = None
            else:
                try:
                    # Attempt to parse the date string into a datetime object
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    # Handle the case where the date is not in the correct format
                    return 'Invalid date format. Please use YYYY-MM-DD format.', 400
            # Create a job dictionary
            job = {
                'title': title,
                'description': description,
                'spaces': spaces,
                'location': location,
                'company': company,
                'date': date
            }

            # Call the add_job function
            add_job(job)

            # Redirect or return a success message

        elif request.form.get('action') == 'remove':
            # Handle job removal here (delete job from the database)
            title_to_remove = request.form.get('title_to_remove')

            # Create a job dictionary for removal
            job_to_remove = {
                'title': title_to_remove
            }

            # Call the remove_job function
            remove_job(job_to_remove)

            # Redirect or return a success message

        elif request.form.get('action') == 'update':
            job_name = request.form.get('job_name')
            current_job = load_job_by_name(job_name)
            if not current_job:
                return 'Job not found', 404

            update_data = {}
            for field in ['title', 'description', 'spaces', 'location', 'company', 'date']:
                update_data[field] = request.form.get(field) if request.form.get(field) else current_job[field]

            if update_data['date']:
                try:
                    update_data['date'] = datetime.strptime(update_data['date'], '%Y-%m-%d')
                except ValueError:
                    return 'Invalid date format. Please use YYYY-MM-DD format.', 400

            update_job_in_db(job_name, update_data)
            return redirect('/admin/dashboard')

    jobs = load_all_jobs()
    return render_template('admin_dashboard.html', jobs=jobs)




#user dashboard
@app.route('/')
def main():
    jobs = load_all_jobs()
    return render_template('home.html', jobs=jobs)


def load_all_jobs():
    results_dict = []
    with engine.connect() as conn:
        result_all = conn.execute(text("SELECT * FROM job_listings")).fetchall()
        for row in result_all:
            row = row._asdict()
            results_dict.append(row)
    return results_dict


def load_job_by_id(job_id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM job_listings WHERE id = :val"), {"val": job_id})
        rows = result.fetchall()
        return rows[0]._asdict() if rows else None


def add_application(application):
    with engine.connect() as conn:
        result = conn.execute(
            text("INSERT INTO applications (name, email, job_id) VALUES (:name, :email, :job_id)"),
            {"name": application['name'], "email": application['email'], "job_id": application['job_id']}
        )
        return result


def add_job(job):
    with engine.connect() as conn:
        result = conn.execute(
            text("INSERT INTO job_listings (title, description, spaces, location, company, date) VALUES (:title, :description, :spaces, :location, :company, :date)"),
            {"title": job['title'], "description": job['description'], "spaces": job['spaces'], "location": job['location'], "company": job['company'], "date": job['date']}
        )
        return result

def remove_job(job):
    with engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM job_listings WHERE title = :title"),
            {"title": job['title']}
        )
        return result


def get_user_by_username(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        return result.fetchone()

def get_user_by_role(role):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE role = :role"), {"role": role})
        return result.fetchone()

def get_user_by_id(id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": id})
        return result.fetchone()


def load_job_by_name(job_name):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM job_listings WHERE title = :title"), {"title": job_name})
        row = result.fetchone()
        return row._asdict() if row else None

def update_job_in_db(job_name, update_data):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE job_listings SET title=:title, description=:description, spaces=:spaces, location=:location, company=:company, date=:date WHERE title = :original_title"),
            {**update_data, "original_title": job_name}
        )

@app.route('/api/jobs')
def list_jobs():
    jobs = load_all_jobs()
    return jsonify(jobs)


@app.route('/job/<int:id>')
def job_detail(id):
    job = load_job_by_id(id)
    if not job:
        return render_template('404.html'), 404
    return render_template('jobsinfo.html', job=job)


@app.route('/job/<int:id>/apply', methods=['POST'])
def apply_for_job(id):
    job = load_job_by_id(id)
    if not job:
        return render_template('404.html'), 404

    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')

    # Add the application to the database
    application = {'name': name, 'email': email, 'job_id': id}
    add_application(application)

    # For demonstration, return a success message
    return render_template('applicationsubmitted.html', name=name, email=email)










if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
