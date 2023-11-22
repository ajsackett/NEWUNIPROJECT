from flask import Flask, render_template, jsonify, request
from database import engine
from sqlalchemy import text

app = Flask(__name__)

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

@app.route('/')
def main():
    jobs = load_all_jobs()
    return render_template('home.html', jobs=jobs)

@app.route('/api/jobs')
def list_jobs():
    jobs = load_all_jobs()
    return jsonify(jobs)

@app.route('/job/<id>')
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

    # Now, you can process this data (e.g., save to the database, send an email, etc.)

    # For demonstration, return the data as JSON
    return jsonify({'name': name, 'email': email})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

