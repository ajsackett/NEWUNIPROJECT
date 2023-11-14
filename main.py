from flask import Flask, render_template, jsonify

app = Flask(__name__)

JOBS = [
    {
        'id': 1,
        'title': 'soup maker',
        'description': 'This is a job description',
        'spaces': 2,
        'company': 'Charity',
        'location': 'London',
        'date': '12/12/2023'
    },
  {
        'id': 1,
        'title': 'Homeless helper',
        'description': 'This is a job description',
        'spaces': 2,
        'company': 'Charity',
        'location': 'Bmouth',
        'date': ''

    },
  {
        'id': 1,
        'title': 'charity manager',
        'description': 'This is a job description',
        'spaces': 2,
        'company': 'Charity',
        'location': 'Brixton',
        'date': '12/12/2023'
    },
]




@app.route('/')
def main():
    return render_template('home.html',jobs=JOBS, company='Charity')

@app.route('/api/jobs')
def list_jobs():
    return jsonify(JOBS)

if __name__ == '__main__':
    print('This is the main program')
app.run(host='0.0.0.0', debug=True)

def list_jobs():
    return JOBS