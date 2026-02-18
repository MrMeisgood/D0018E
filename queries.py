from flask import Flask, render_template, url_for, request, redirect
from base import get_conn

def login_user(uname, passw):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE name = %s', (uname,))
    user_record = cur.fetchone()
    if user_record:
        id, name, password, isadmin = user_record
        if password == passw:
            return True, id, name
    return False, None, 'Invalid username or password'