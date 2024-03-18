# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def show_entries():
    db = get_db()
    filter = request.args.get('selected_category')
    cur = db.execute('SELECT title, category, text, id FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    filtered_entries = []

    if not filter or filter == 'noFilter':
        filtered_entries = entries
    else:
        for entry in entries:
            if filter == entry['category']:
                filtered_entries.append(entry)

    return render_template('show_entries.html', filtered_entries=filtered_entries, entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    if request.form['title'] and request.form['category'] and request.form['text']:
        db.execute('INSERT INTO entries (title, category, text) VALUES (?, ?, ?)',
                   [request.form['title'], request.form['category'], request.form['text']])
        db.commit()
        flash('New entry was successfully posted')
    else:
        flash('Entry failed: Please enter a title, category, and text in the input field')

    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_entry():
    if request.form["edit"]:
        return redirect(url_for('edit_entry', title=request.form['title'],
                                category=request.form['category'], text=request.form['text'],
                                id=request.form['id']))
    else:
        db = get_db()
        db.execute('DELETE FROM entries WHERE title = ? AND category = ? AND text = ?',
                   [request.form['title'], request.form['category'], request.form['text']])
        db.commit()
        flash('Entry was successfully deleted')

        return redirect(url_for('show_entries'))


@app.route('/edit', methods=['GET', 'POST'])
def edit_entry():
    title = request.args.get('title')
    category = request.args.get('category')
    text = request.args.get('text')
    id = request.args.get('id')

    return render_template('edit_entry.html',
                           title=title, category=category, text=text, id=id)


@app.route('/update', methods=['GET', 'POST'])
def update_entry():
    if request.form['title'] and request.form['category'] and request.form['text'] and request.form['id']:
        db = get_db()
        db.execute('UPDATE entries SET title = ?, category = ?, text = ? WHERE id = ?;',
                   [request.form['title'], request.form['category'],
                    request.form['text'], request.form['id']])
        db.commit()
        flash('Entry was successfully updated')
    else:
        flash('Update failed: Please enter a title, category, and text in the input field')

    return redirect(url_for('show_entries'))