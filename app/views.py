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

@app.route('/output')
def crawl_output():
	  #pull 'ID' from input field and store it
 	start = request.args.get('START_LOC')  #, 'BAR_LOC', 'END_LOC')
	bar = request.args.get('BAR_LOC')
	end = request.args.get('END_LOC')

	geolocator = Nominatim()

	location = geolocator.geocode(start)
	#put in exceptions if geolocator doesn't work
	start_lat, start_lng = location.latitude, location.longitude


	location = geolocator.geocode(bar)
	bar_lat, bar_lng = location.latitude, location.longitude

	location = geolocator.geocode(end)
	end_lat, end_lng = location.latitude, location.longitude


	node_sql = ReadNodefromSQL(cur)
	edge_sql = ReadEdgefromSQL(cur)



	node_dic = NodeSQLtoDic(node_sql)
	edge_dic = EdgeDQLtoDic(edge_sql)
	G = gen_network(node_dic, edge_dic)
	
	path = crawl_path(G, start_lat, start_lng, bar_lat, bar_lng, end_lat, end_lng)
	tmp = path_node_list(path, node_dic)
 	#return render_template('output.html', start = {start: start_lat, start_lng } , bar = {bar:bar_lat, bar_lng}, end = {end : end_lat, end_lng}, path = path, path_list = tmp)
 	return render_template('output.html', start = start, startlat=start_lat,startlng=start_lng, bar = bar, barlat=bar_lat, barlng=bar_lng, end = end, endlat= end_lat,endlng =end_lng, path = path, path_list = tmp)
