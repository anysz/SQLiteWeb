# -*- coding: utf-8 -*-
# ==============
#  SQLITE3 Explorer (Webapp)
#  Written by Anysz
# ==============
#  (!!!) WARNING: DO NOT RUN THIS AS PUBLIC SERVICE.
# ==============
import os, sys
from flask import (
	Flask,
	render_template, abort,
	request, Response, url_for,
	session, jsonify, redirect,
)
import json
import time
import re

import sqlite3

app = Flask(__name__,
	static_url_path = '/assets',
	static_folder = 'static',
	template_folder = 'templates',
	)
app.config.update({
	'time': time.time,
	'int': int,
	'str': str,

	'app_title': 'MySqlite3',

	'DEBUG': True,
	'SECRET_KEY': 'wkwkland-anysz101-app-sqlite-explorer',
	'JSONIFY_MIMETYPE': 'application/json;charset=UTF-8',
})

def get_db_files():
	dbs_file = [f for f in os.listdir("databases/")]
	return dbs_file
def make_connection(dbfile):
	conn = sqlite3.connect('databases/' + dbfile,check_same_thread=False)
	return conn

def getTableList(conn):
	return conn.execute('SELECT * FROM sqlite_master').fetchall()

jx = re.compile(r'\(([^\"]*)\)')
def parse_query(q):
	#'CREATE TABLE new_badge (id TEXT PRIMARY KEY,show_time_millis INTEGER,hide_time_millis INTEGER)'
	jas = jx.findall(q)
	sx = jas[0]
	raw_fields = sx.split(',')
	sxe = []
	for field in raw_fields:
		sfield = field.split(' ')
		try: 
			is_primary = sfield[2]
			is_primary = True
		except: is_primary = False
		jl = {'name': sfield[0], 'type': sfield[1], 'primary': is_primary}
		sxe.append(jl)
	return sxe


@app.route('/')
def index():
	page = {
		'title': 'Select Database',
		'dbs': get_db_files(),
	}
	return render_template('dblisting.html', page_set=page)

@app.route('/explore')
def db_explore():
	dblist = get_db_files()
	db_name = request.args.get('db', None)
	if db_name == None:
		db_name = session.get('current_db', None)
		if db_name == None:
			return redirect(url_for('index'))
	if db_name not in dblist:
		return redirect(url_for('index'))

	session['current_db'] = db_name
	db = make_connection(db_name)
	tblist = getTableList(db)
	page = {
		'title': db_name,
		'cur_db': db_name,
		'table_list': tblist,
	}
	return render_template('dbexplore.html', page_set=page)

@app.route('/explore/table', methods=['GET','POST'])
def db_explore_table():
	dblist = get_db_files()
	db_name = request.args.get('db', None)
	tb_name = request.args.get('table', None)
	if (db_name == None) or (tb_name == None):
		db_name = session.get('current_db', None)
		tb_name = session.get('current_tb', None)
		if (db_name == None) or (tb_name == None):
			return redirect(url_for('index'))
	if db_name not in dblist:
		return redirect(url_for('index'))
	db = make_connection(db_name)
	tblist = getTableList(db)
	rtb = {}
	for tbx in tblist:
		if tbx[0] == 'table':
			rtb[tbx[1]] =tbx
	if tb_name not in rtb:
		return redirect(url_for('db_explore'))
	session['current_db'] = db_name
	session['current_tb'] = tb_name
	cnf = rtb[tb_name]
	scx = parse_query(cnf[4])

	query = f'SELECT * FROM {tb_name}'
	if request.environ['REQUEST_METHOD'] == 'POST':
		query = request.form.get('query', query)
	items = db.execute(query).fetchall()
	if request.environ['REQUEST_METHOD'] == 'GET':
		if len(items) > 140:
			query = f'SELECT * FROM {tb_name} LIMIT 140'
			items = db.execute(query).fetchall()


	page = {
		'title': db_name,
		'cur_db': db_name,
		'cur_tb': tb_name,
		'finfos': scx,
		'iquery': query,
		'items': items,
		'length_field': len(scx),
		'length_item': len(items),
	}
	return render_template('dbshow.html', page_set=page)

if __name__ == "__main__":
	app.run(port=6677)