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



start_tuple = (40.6868, -73.9824)
bar_tuple_list = [( 40.68680000, -73.97510000),(40.68200000, -73.98020000),( 40.69340000, -73.97300000), ( 40.69330000,-73.96910000),(40.67720000, -73.95740000)]
end_tuple = (40.67430000,-73.99540000)

def crawl_path(start_tuple, bar_tuple_list, end_tuple):
    from datetime import datetime
    startTime = datetime.now()

#generate graph including points and locations
#define location dictionary of crawl
    crawl = {}
    crawl['S'] = start_tuple 
    if start_tuple == end_tuple:
        start = 'S'
        end ='S'
    elif end_tuple!=start_tuple:
        crawl['E'] = end_tuple
        start = 'S'
        end = 'E'
    i=1
    for bar in bar_tuple_list:
        crawl['B'+str(i)]= bar
        i+=1
#loop through all combinations of nodes to find distances
    crawl_edge = {}
    for loc1 in crawl:
        for loc2 in crawl:
            if loc1 == loc2:
                pass
            else:
                dist = make_path (crawl[loc1][0], crawl[loc1][1], crawl[loc2][0],crawl[loc2][1],G)
                crawl_edge[loc1+loc2] = loc1, loc2, dist[1], dist[0]
            
    G_crawl = gen_network(crawl, crawl_edge)

    distances = []
    for path in nx.all_simple_paths(G_crawl, source= start , target = end, cutoff = len(bar_tuple_list)+2):
    #we only want the longest ones
        if(len(path)==len(bar_tuple_list)+2):
            distance=0
        #add up the weights for each edge
            for i in range(0,len(path)-1):
                distance=distance+G_crawl[path[i]][path[i+1]]['weight']
            #add these to a list
            distances.append((distance,path))
            
#defaults
    min_dist=distances[0];
    min_path=[]

#find the min distance
    for dist in distances:
        if(dist[0]<=min_dist):
            min_dist=dist[0]
            min_path=dist[1]

# determine the final between bars
    route = []
    for i in range(0,len(min_path)-1):
        route.append(crawl_edge[min_path[i]+min_path[i+1]][3])

    line_paths = path_node_line(route, node_dic)


    print min_path
    print "has a distance of"
    print min_dist
#print (route) #nodes
    print line_paths #lat and lng of nodes
    print 'runtime :' , datetime.now() - startTime


crawl_path(start_tuple, bar_tuple_list, end_tuple)


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