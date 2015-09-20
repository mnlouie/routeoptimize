import MySQLdb
import networkx as nx
from geopy.distance import great_circle


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
    db = MySQLdb.connect(user="root", host="localhost", db="bk_map",  charset='utf8')
    with db: 
        cur.db.cursor()

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
	db = MySQLdb.connect(user="root", host="localhost", db="bk_map",  charset='utf8')
	with db: 
		cur.db.cursor()
	cur.execute('''SELECT nodeid, latitude, longitude FROM bk_nodes
                ''')  
	nodes_sql = cur.fetchall()
	return nodes_sql

def ReadEdgefromSQL():
	db = MySQLdb.connect(user="root", host="localhost", db="bk_map",  charset='utf8')
	with db: 
		cur.db.cursor()
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