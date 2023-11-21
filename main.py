from flask import Flask, render_template, jsonify
from database import engine
from sqlalchemy import text
from dotenv import load_dotenv
import os
app = Flask(__name__)



def load_jobs():
    results_dict = []
    with engine.connect() as conn:
        result_all = conn.execute(text("SELECT * FROM job_listings")).fetchall()
        for row in result_all:
            row = row._asdict()
            results_dict.append(row)
    return results_dict

@app.route('/')
def main():
    jobs = load_jobs()
    return render_template('home.html', jobs=jobs)

@app.route('/api/jobs')
def list_jobs():
    jobs = load_jobs()
    return jsonify(jobs)

if __name__ == '__main__':
    print('This is the main program')
app.run(host='0.0.0.0', debug=True)

def list_jobs():
    return JOBS