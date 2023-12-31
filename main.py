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


@app.route('/test-update')
def test_update():
    # Hardcoded test values
    test_job_id = 12  # Replace with a valid job ID from your database
    test_update_data = {
        'title': 'Test Title2',
        'description': 'Test Description',
        'spaces': 10,
        'location': 'Test Location',
        'company': 'Test Company',
        'date': datetime(2023, 1, 1)  # Example date, change as needed
    }

    # Call the update function
    try:
        update_job_in_db(test_job_id, test_update_data)
        return 'Update successful'
    except Exception as e:
        return f'Update failed: {e}'
    print(test_job_id)
    print(test_update_data)


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


# admin dashboard
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
            print("Received form data:", request.form)
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
            print(job)

            # Call the add_job function
            add_job(job)
            printy = add_job(job)
            print(printy)

            # Redirect or return a success message

        elif request.form.get('action') == 'remove':
            print("Received form data:", request.form)
            # Retrieve the job ID from the form input
            job_id_str = request.form.get('job_id_to_remove')
            print("Received Job ID to remove (string):", job_id_str)

            # Convert job_id_str to an integer and handle potential errors
            try:
                job_id = int(job_id_str)
                print("Converted Job ID to remove (int):", job_id)
            except ValueError:
                print("Error in converting Job ID to remove. Received:", job_id_str)
                return 'Invalid Job ID', 400

            # Remove the job using its ID
            try:
                remove_job(job_id)
                print("Job successfully removed with ID:", job_id)
            except Exception as e:
                print("Error in removing job:", e)
                return 'Error in removing job', 500

            # Redirect or return a success message

        elif request.form.get('action') == 'update':
            job_id_str = request.form.get('job_id')
            print("Received Job ID (string):", job_id_str)

            # Safely convert job_id to int and handle potential errors
            try:
                job_id = int(job_id_str)
                print("Converted Job ID (int):", job_id)
            except ValueError:
                print("Job ID conversion error. Received Job ID:", job_id_str)
                return 'Invalid Job ID', 400

            current_job = load_job_by_id(job_id)
            if not current_job:
                print("Job not found for Job ID:", job_id)
                return 'Job not found', 404

            # Initialize update_data with current job data
            update_data = current_job.copy()

            # Update fields if new data is provided
            for field in ['title', 'description', 'location', 'company']:
                new_value = request.form.get(f'update_{field}')
                if new_value:
                    update_data[field] = new_value

            # Handle 'spaces' field
            spaces_str = request.form.get('update_spaces')
            if spaces_str:
                try:
                    update_data['spaces'] = int(spaces_str)
                except ValueError:
                    print("Invalid spaces value:", spaces_str)
                    return 'Invalid spaces value. Please enter a number.', 400

            # Handle 'date' field
            date_str = request.form.get('update_date')
            if date_str:
                try:
                    update_data['date'] = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format:", date_str)
                    return 'Invalid date format. Please use YYYY-MM-DD format.', 400

            print("Update data:", update_data)

            try:
                update_job_in_db(job_id, update_data)
                print("Update operation successful for Job ID:", job_id)
            except Exception as e:
                print("Error in updating job:", e)
                return 'Error in updating job', 500

    jobs = load_all_jobs()
    return render_template('admin_dashboard.html', jobs=jobs)
# user dashboard
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
            text(
                "INSERT INTO job_listings (title, description, spaces, location, company, date) VALUES (:title, :description, :spaces, :location, :company, :date)"),
            {"title": job['title'], "description": job['description'], "spaces": job['spaces'],
             "location": job['location'], "company": job['company'], "date": job['date']}
        )
        return result


def remove_job(job_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM job_listings WHERE id = :job_id"),
            {"job_id": job_id}
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


def update_job_in_db(job_id, update_data):
    with engine.connect() as conn:
        try:
            conn.execute(
                text(
                    "UPDATE job_listings SET title=:title, description=:description, spaces=:spaces, location=:location, company=:company, date=:date WHERE id = :job_id"),
                {**update_data, "job_id": job_id}
            )
            conn.commit()
        except Exception as e:
            print("SQL Error:", e)
            conn.rollback()


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

