import MySQLdb
import node_edge_gen as neg
import networkx as nx

from geopy.distance import great_circle

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
    db = DATABASE 
    )

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

def distance_btw_nodes(node1,node2,node_dic):
    return great_circle(node_dic[node1], node_dic[node2]).miles

def accident_weight_btw_nodes(node1, node2, weight_dic):
##    node1 = str(node1)
##    node2 = str(node2)
    if node1 in weight_dic and node2 in weight_dic:
        return weight_dic[node1] + weight_dic[node2]
    elif node1 in weight_dic and node2 not in weight_dic:
        return weight_dic[node1]
    elif node1 not in weight_dic and node2 in weight_dic:
        return weight_dic[node2]
    else:
        return 0

def ReadNodefromSQL():
	#fetch data for nodes and edges
	cur.execute('''SELECT nodeid, latitude, longitude FROM bk_nodes
                ''')  
	nodes_sql = cur.fetchall()
	return nodes_sql

def ReadEdgefromSQL():
	#read in the nearest neighbor weights
	cur.execute('''SELECT edgeid, node1, node2, weight FROM bk_edges
                ''')  
	edge_sql = cur.fetchall()
	return edge_sql

def NodeSQLtoDic(nodes_sql):
	node_dic = {}
	for node in nodes_sql:
		node_dic[str(node[0])] = str(node[1]) ,str(node[2]) 
	return node_dic

def EdgeSQLtoDic(edge_sql):
	edge_dic = {}
	for edge in edge_sql:
		edge_dic[edge[0]]= edge[1:]
	return edge_dic

def gen_network(node_dic, edge_dic):
    G = nx.Graph()
    for d in node_dic:
        G.add_node(d)
    for e in edge_dic:
        G.add_edge(edge_dic[e][0],edge_dic[e][1])

    print 'NODES: ', G.number_of_nodes()
    print 'EDGES: ', G.number_of_edges()
    return G

def find_neighbors(Graph):
	neighbor_dic = {}
	for node in Graph.nodes():
    	neighbor_dic[node] = Graph.neighbors(node)
    return neighbor_dic

def make_nearestneighborhood_weights(node_dict,edge_dict,feature_dict,feature_factor):
    traffic_weightnn = {}
    for node in neighbor_dic:
        traffic_weight = 0
        for no in neighbor_dic[node]:
            traffic_weight += feature_dic[no] 
        #weight = traffic_weight + traffic_dic[node]    
        if traffic_weight + feature_dic[node] != 0:
             weight = feature_dic[node] / (traffic_weight + feature_dic[node])
        else:
            weight = 0
        traffic_weightnn[node] = weight
    tmp_edge = {}
    for edge in edge_dic:
        #print edge_dict[edge][0], edge_dict[edge][1]
        acc_wei = accident_weight_btw_nodes(edge_dic[edge][0], edge_dic[edge][1], traffic_weightnn)
        weight = ((feature_factor*acc_wei) + 1)*distance_btw_nodes(edge_dic[edge][0],edge_dic[edge][1],node_dic)
        tmp_edge[edge] = edge_dic[edge][0], edge_dic[edge][1], weight
    return tmp_edge

def addweighttoSQL(edge_dic, table):
	add_edge= ("INSERT INTO %s "
           " (edgeid, node1, node2, weight)"
           " VALUES (%s, %s,%s, %s)")
    
	for ed in edge_dic:
    	edge_data = table, ed, edge_dic[ed][0], edge_dic[ed][1], edge_dic[ed][2]
    	cur.execute(add_edge, edge_data)
    db_connect.commit()
    return

def AccidentsPerNode(accident_dic):
	tmp_dic = {}
	for acc in accident_dic:
	node = accident_dic[acc][3]
	if node != 'NULL':
		if node in tmp_dic:
			tmp_dic[node] =  tmp_dic[node] + 1
		else:
			tmp_dic[node] = feature_dict[feat][2]
	else:
		pass
	
	traffic_dic = {}
	for node in node_dic:
		if node in tmp_dic:
			traffic_dic[node] = float(tmp_dic[node])
		else:
			traffic_dic[node] = 0
	return traffic_dic


def close_db():
	cur.close()
	db_connect.close()


nodelist_sql = ReadNodefromSql()
edgelist_sql = ReadEdgefromSql()

node_dic = NodeSqltoDic(nodelist_sql)
edge_dic = EdgeSQLtoDic(edgelist_sql)

G = gen_network(node_dic, edge_dic)


neighbor_dic = find_neighbors(G)


#accidents

cur.execute("""SELECT id, latitude, longitude , n_ped_inj  
    FROM bk_trafficaccidents 
    WHERE n_ped_inj > 0
    AND date BETWEEN '2014-09-01' AND '2015-09-01'
    """)
accidents_sql = cur.fetchall()


acc_dic = {}
for a in range(0,len(accidents_sql)):
    node = nearest_node(accidents_sql[a][1],accidents_sql[a][2])
    acc_dic[accidents_sql[a][0]] = accidents_sql[a][1],accidents_sql[a][2],accidents_sql[a][3], node

acc_dic_allnode = AccidentsPerNode(acc_dic)

nn_weights = make_nearestneighborhood_weights(node_dic, edge_dic,acc_dic_allnode, 1)

#addweighttoSQL(nn_weights, 'bk_weights_acc_nn')



close_db()
