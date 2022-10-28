from flask import Flask, render_template, request, session, redirect, url_for
import secrets
import ibm_db
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex()

conn = ibm_db.connect(
    f"DATABASE={os.environ.get('DATABASE')};"
    f"HOSTNAME={os.environ.get('HOSTNAME')};"
    f"PORT={os.environ.get('PORT')};"
    f"USERNAME={os.environ.get('DB_USERNAME')};"
    f"PASSWORD={os.environ.get('PASSWORD')};"
    "SECURITY=SSL;"
    f"SSLSERVERCERTIFICATE={os.environ.get('SSLSERVERCERTIFICATE')};",
    '',
    ''
)


@app.route('/', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        sql = 'SELECT * FROM users WHERE email = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            msg = 'Account already exists!'
        else:
            insert_sql = 'INSERT INTO users (email, password) VALUES (?, ?)'
            insert_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(insert_stmt, 1, email)
            ibm_db.bind_param(insert_stmt, 2, password)
            ibm_db.execute(insert_stmt)
            msg = 'Account created created successfully!'
            return redirect(url_for('login'))

    return render_template('register.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sql = 'SELECT * FROM users WHERE email = ? AND password = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            session['id'] = account['EMAIL']
            return render_template(
                'index.html',
                msg='Logged In Successfully!'
            )
        else:
            return render_template(
                'login.html',
                msg='Incorrect username or password!'
            )
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
