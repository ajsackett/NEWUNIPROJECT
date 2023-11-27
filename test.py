
@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form['username']
    password = request.form['password']
    print(username)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        user = result.fetchone()

        if user and check_password_hash(user.password, password):
            # Assuming the admin has a specific role or is_admin flag
            if user.is_admin:
                # Logic to handle admin login
                # e.g., storing user info in session
                return redirect('/admin/dashboard')
            else:
                return 'Access Denied', 403

        return 'Invalid credentials', 401





if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
