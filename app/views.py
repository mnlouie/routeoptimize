from flask import render_template, request
from app import app
import MySQLdb
from a_Model import ModelIt

import networkx as nx
import matplotlib.pylab as plt
from geopy.distance import great_circle 
from geopy.geocoders import Nominatim 
from setup_functions2 import *




@app.route('/')

@app.route('/index')
def index():
	return render_template("index.html",
		title = 'Home', user = { 'nickname': 'Missy' },
		)

@app.route('/db')
def bkmap_page():
	db = MySQLdb.connect(user="root", host="localhost", db="bk_map",  charset='utf8')
	with db: 
		cur = db.cursor()
		cur.execute("SELECT * FROM bk_weights LIMIT 15;")
		query_results = cur.fetchall()
	edges = ""
	for result in query_results:
		edges += result[0]
		edges += "<br>"
		return edges

@app.route("/db_fancy")
def bkmap_page_fancy():
	db = MySQLdb.connect(user="root", host="localhost", db="bk_map",  charset='utf8')
	with db:
		cur = db.cursor()
		cur.execute("SELECT edgeid, node1, node2, weight FROM bk_weights LIMIT 15;")

		query_results = cur.fetchall()
	edges = []
	for result in query_results:
		edges.append(dict(edgeid=result[0], node1=result[1], node2=result[2], weight = result[3]))
	return render_template('cities.html', edges = edges) 

@app.route('/input')
def crawl_input():
	return render_template("input.html")

@app.route('/input_2')
def crawl_input2():
	return render_template("input_2.html")

@app.route('/output')
def crawl_output():
	start = request.args.get("START_LOC")
	bar1 = request.args.get("BAR1")
	bar2 = request.args.get("BAR2")
	bar3 = request.args.get("BAR3")
	end = request.args.get("END_LOC")
	bar_input_list = [bar1, bar2, bar3]
	bar_address = get_bar_address(bar1, bar2, bar3)

	start_tuple, end_tuple = get_start_end(start,end)
	bar_tuple_list = get_bar_location(bar1,bar2,bar3)

	node_sql = ReadNodefromSQL(cur)
	edge_sql = ReadEdgefromSQL(cur)

	node_dic = NodeSQLtoDic(node_sql)
	edge_dic = EdgeDQLtoDic(edge_sql)

	G = gen_network(node_dic, edge_dic)

	path, line_path = crawl_path(G, start_tuple, bar_tuple_list, end_tuple, node_dic, edge_dic)
	bar_address = reorder_beer_list(bar_address, path)
	bar_tuple_list = reorder_beer_list(bar_tuple_list, path)
	single_path = []
	for line in line_path:
		single_path.extend(line)
	bar_list = tuplebarlist_floatlist(bar_tuple_list)
	bar_add = tuplebarlist_stringlist(bar_address)
	bar_dic = make_bar_dic(bar_add, bar_list)
	return render_template('output.html',  start = [start, start_tuple[0],start_tuple[1]],  bar_add =bar_add, bar_dic = bar_dic, end = [end,end_tuple[0],end_tuple[1]], path = path, path_list = single_path)

