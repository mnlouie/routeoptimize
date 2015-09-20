#!/opt/local/bin/python

import MySQLdb
import networkx as nx
import matplotlib.pylab as plt
from geopy.distance import great_circle
from geopy.geocoders import Nominatim 
import folium

# DEFINE SQL LOG IN 
HOST = 'localhost'
USER = 'root'
PASSWD = ''
DATABASE = 'bk_map'

#CONNECT TO MySQL
db_connect = MySQLdb.connect(
	host = HOST,
	user = USER,
	passwd = PASSWD,
	db = DATABASE)

cur = db_connect.cursor()

def nearest_node(lat_input, lon_input):
    dis_near=0.05
    find_nearby_nodes = ('''SELECT nodeid, latitude, longitude FROM bk_nodes 
                WHERE latitude BETWEEN %s AND %s
                AND longitude BETWEEN %s AND %s
                ''')
    node_range = (lat_input-dis_near, lat_input+dis_near, lon_input-dis_near, lon_input+dis_near)

    cur.execute(find_nearby_nodes,node_range)  
    rows = cur.fetchall()
    if len(rows) == 0:
        return 'NULL'
    #for row in rows:
    else:
        dist = [rows[0][0],great_circle((lat_input,lon_input),rows[0][1:3]).miles ]
        for row in rows[1:]:
            node_dist =  great_circle((lat_input,lon_input),row[1:3]).miles
            if dist[1] > node_dist:
                dist = [row[0],node_dist]
        return dist[0]

def gen_network(node_dic, edge_dic):
	G = nx.Graph()
	for d in node_dic:
 		G.add_node(d)
	
	for e in edge_dic:
		G.add_edge(str(edge_dic[e][0]),str(edge_dic[e][1]), weight = edge_dic[e][2])

	#print 'NODES: ', G.number_of_nodes()
	#print 'EDGES: ', G.number_of_edges()
	return G

def ReadNodefromSQL():
	#fetch data for nodes and edges
	cur.execute('''SELECT nodeid, latitude, longitude FROM bk_nodes
                ''')  
	nodes_sql = cur.fetchall()
	return nodes_sql

def ReadEdgefromSQL():
	#read in the nearest neighbor weights
	cur.execute('''SELECT edgeid, node1, node2, weight FROM bk_weights_acc_nn
                ''')  
	edge_sql = cur.fetchall()
	return edge_sql

def NodeSQLtoDic(nodes_sql):
	node_dic = {}
	for node in nodes_sql:
		node_dic[str(node[0])] = str(node[1]) ,str(node[2]) 
	return node_dic

def EdgeDQLtoDic(edge_sql):
	edge_dic = {}
	for edge in edge_sql:
		edge_dic[edge[0]]= edge[1:]
	return edge_dic


def make_path(start_lat, start_lng, end_lat, end_lng):
#INPUT 
	start = nearest_node(start_lat,start_lng)
	end = nearest_node(end_lat, end_lng)
#exeption!!
	#nx.has_path(G,start,end)
	return nx.shortest_path(G,source = start, target = end, weight='weight')#
	 

def plot_path(node_dic, path_nodes):
	for d in node_dic:
		plt.scatter(node_dic[d][0],node_dic[d][1])
    
	node_list = []

	for p in path_nodes[0]:
		node_list.append(node_dic[str(p)]) 
            
		plt.plot(*zip(*node_list), color='g')

	node_list = []
	for p in path_nodes[1]:
		node_list.append(node_dic[str(p)])

		plt.plot(*zip(*node_list), color='r')

	plt.show()
	return

def crawl_path(start_lat, start_lng, bar_lat, bar_lng, end_lat, end_lng):
	path1 = make_path(start_lat, start_lng, bar_lat, bar_lng)
	path2 = make_path(bar_lat, bar_lng, end_lat, end_lng)
	return path1, path2

def close_db():
	cur.close()
	db_connect.close()

#ACTUAL PROGRAM



geolocator = Nominatim()

location = geolocator.geocode("Atlantic Terminal, Brooklyn")
start_lat, start_lng = location.latitude, location.longitude


location = geolocator.geocode("82 4th Ave, Brooklyn")
bar_lat, bar_lng = location.latitude, location.longitude

location = geolocator.geocode("Prospect Park, Brooklyn")
end_lat, end_lng = location.latitude, location.longitude

#max_lat = max([start_lat,bar_lat, end_lat])
#max_lng = max([start_lng,bar_lng, end_lng])

#min_lat = min([start_lat,bar_lat, end_lat])
#min_lng = min([start_lng,bar_lng, end_lng])

#print min_lat, max_lat
#print min_lng, max_lng

node_sql = ReadNodefromSQL()
edge_sql = ReadEdgefromSQL()

node_dic = NodeSQLtoDic(node_sql)
edge_dic = EdgeDQLtoDic(edge_sql)
G = gen_network(node_dic, edge_dic)



#start_lat = 40.6868 
#start_lng = -73.9824
#bar_lat =40.68200000 
#bar_lng = -73.98020000
#end_lat = 40.67430000 
#end_lng = -73.99540000

#path = make_path(start_lat, start_lng, end_lat, end_lng)
path = crawl_path(start_lat, start_lng, bar_lat, bar_lng, end_lat, end_lng)

#plot_path(node_dic, path)

map_osm = folium.Map(location=[40.6928, -73.990340], width=500, height = 300)
map_osm.polygon_marker(location=[start_lat, start_lng], popup='Starting Point',
                     fill_color='#132b5e', num_sides=3, radius=10)
map_osm.polygon_marker(location=[bar_lat, bar_lng], popup='Bar',
                     fill_color='#45647d', num_sides=4, radius=10)
map_osm.polygon_marker(location=[end_lat, end_lng], popup='Ending Point',
                     fill_color='#769d96', num_sides=6, radius=10)


for pa in paths:
	locat = []
	for p in pa:
		locat.append(node_dic[]) 
	#map.line(locations=[nodedic[,
#[45.324224, -121.657763]
    #[45.318702, -121.652871]])


map_osm.create_map(path='osm.html')
cur.close()
db_connect.close()