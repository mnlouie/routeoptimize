import MySQLdb
import networkx as nx
from geopy.distance import great_circle
import folium
from geopy.geocoders import Nominatim 



db = MySQLdb.connect(user="root", host="localhost", db="bk_map",  charset='utf8')
with db: 
	cur = db.cursor()

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

def ReadNodefromSQL(cur):
	#fetch data for nodes and edges
	cur.execute('''SELECT nodeid, latitude, longitude FROM bk_nodes
                ''')  
	nodes_sql = cur.fetchall()
	return nodes_sql

def ReadEdgefromSQL(cur):
	cur.execute('''SELECT edgeid, node1, node2, weight FROM bk_weights
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


def make_path(start_lat, start_lng, end_lat, end_lng, G):
#INPUT 
	start = nearest_node(start_lat,start_lng)
	end = nearest_node(end_lat, end_lng)
#exeption!!
	#nx.has_path(G,start,end)
	return nx.shortest_path(G,source = start, target = end, weight='weight'), nx.shortest_path_length(G,source = start, target = end, weight='weight')#
	 

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


def path_node_list(path, node_dic):
    line_paths = []
    for pa in path:
        line=[]
        for node in pa:
            line.append([float(node_dic[node][0]),float(node_dic[node][1])])
        line_paths.append(line)
    return line_paths

def get_start_end(start,end):
	geolocator = Nominatim()
	location = geolocator.geocode(start)
	#put in exceptions if geolocator doesn't work
	start_tuple = (location.latitude, location.longitude)
	location = geolocator.geocode(end)
	end_tuple = (location.latitude, location.longitude)
	return start_tuple, end_tuple

def get_bar_location(bar1, bar2, bar3):
	getbars = '''SELECT latitude, longitude FROM crawl_venues
				WHERE venue_name IN (%s, %s, %s)
                '''  % ("'"+bar1+"'", "'"+bar2+"'", "'"+bar3+"'")
	cur.execute(getbars)
	bar_tuple_list = cur.fetchall()
	return bar_tuple_list

def get_bar_address(bar1, bar2, bar3):
	getbars = '''SELECT venue_name, address FROM crawl_venues
				WHERE venue_name IN (%s, %s, %s)
                '''  % ("'"+bar1+"'", "'"+bar2+"'", "'"+bar3+"'")
	cur.execute(getbars)
	bar_tuple_list = cur.fetchall()
	return bar_tuple_list

def path_node_line(path, node_dic):
    line_paths = []
    for pa in path:
        line=[]
        for node in pa:
            line.append([float(node_dic[node][0]),float(node_dic[node][1])])
        line_paths.append(line)
    return line_paths


def reorder_beer_list(bar_list, path):
	order = []
	for i in path[1:-1]:
		order.append(int(i.split('B')[1])-1)
	ordered_bars = [ bar_list[i] for i in order ]
	return ordered_bars

def tuplebarlist_floatlist(bar_tuple_list):
	floatlist = []
	for t in bar_tuple_list:
		floatlist.append(list(t))
	return floatlist

def tuplebarlist_floatlist(bar_tuple_list):
	floatlist = []
	for t in bar_tuple_list:
		floatlist.append(list(t))
	return floatlist

def tuplebarlist_stringlist(bar_address):
	bar_add = []
	for bar in bar_address:
		bar_add.append([str(bar[0]),str(bar[1])])
	return bar_add

def make_bar_dic(bar_add, bar_latlng):
	bar_dic = {}
	for i in range(0,len(bar_add)):
		bar_dic[bar_add[i][0]] = [bar_add[i][1], bar_latlng[i]]
	return bar_dic

def crawl_path(G, start_tuple, bar_tuple_list, end_tuple, node_dic, edge_dic):
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


    #print min_path
    #print "has a distance of"
    #print min_dist
#print (route) #nodes
    #print line_paths #lat and lng of nodes
    #print 'runtime :' , datetime.now() - startTime
    return min_path, line_paths