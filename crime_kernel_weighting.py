import MySQLdb
import node_edge_gen as neg
import networkx as nx

from geopy.distance import great_circle
from geopy.distance import vincenty

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_species_distributions
from sklearn.datasets.species_distributions import construct_grids
from sklearn.neighbors import KernelDensity

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


def getSQLcrime():
	cur.execute(""" SELECT longitude, latitude FROM bk_crime 
    	WHERE crime IN ('ROBBERY', 'GRAND LARCENY','FELONY ASSAULT', 'MURDER') 
    	AND latitude BETWEEN 40.569 AND 40.7847
    	AND longitude BETWEEN -74.0500 AND -73.5899
    	AND month = 8
    	""")
	crime_location = cur.fetchall()
	return crime_location


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

def plot_nodes(nodes):
    for d in nodes:
        plt.scatter(nodes[d][0],nodes[d][1])
    return

def make_data_numpy():
	cur.execute(""" SELECT latitude FROM bk_crime 
    	WHERE crime IN ('ROBBERY', 'GRAND LARCENY','FELONY ASSAULT', 'MURDER') 
    	AND latitude BETWEEN 40.569 AND 40.7847
    	AND longitude BETWEEN -74.0500 AND -73.5899
    	AND month = 8
    	""")
	crime_lat = cur.fetchall()
	crime_lat_list = []
	for lat in crime_lat:
    currime_lat_list.append(lat)
	cur.execute(""" SELECT longitude FROM bk_crime 
    	WHERE crime IN ('ROBBERY', 'GRAND LARCENY','FELONY ASSAULT', 'MURDER') 
    	AND latitude BETWEEN 40.569 AND 40.7847
    	AND longitude BETWEEN -74.0500 AND -73.5899
    	AND month = 8
    	""")
	crime_lng = cur.fetchall()
	crime_lng_list = []
	for lng in crime_lng:
    	crime_lng_list.append(lng)
	cur.execute("""SELECT total FROM bk_crime 
    	WHERE crime IN ('ROBBERY', 'GRAND LARCENY','FELONY ASSAULT', 'MURDER') 
    	AND latitude BETWEEN 40.569 AND 40.7847
    	AND longitude BETWEEN -74.0500 AND -73.589
    	AND month = 8
    	""")
	crime_total = cur.fetchall()
	crime_total_list = []
	for total in crime_total:
    	crime_total_list.append(total)
	crime_lat_np = np.array(crime_lat_list)
	crime_lng_np = np.array(crime_lng_list)
	crime_total_np = np.array(crime_total_list)
	data = np.hstack([crime_lat_np, crime_lng_np, crime_total_np])
	return data

def find_kernel(data, numgrid = 1000, bw = 0.002):
	Xtrain = data[:,0:2]
	ytrain = data[2]
	# Set up the data grid for the contour plot
	xgrid = np.linspace(-74.1, -73.65, numgrid=1000)
	ygrid = np.linspace(40.5, 40.8, numgrid=1000)
	X, Y = np.meshgrid(xgrid, ygrid)

	xy = np.vstack([Y.ravel(), X.ravel()]).T

	# Plot map of with distributions of each species
	fig = plt.figure()
    # construct a kernel density estimate of the distribution
	kde = KernelDensity(bandwidth=bw,
                    kernel='gaussian')
	kde.fit(Xtrain, y = ytrain)

 # evaluate only on the land: -9999 indicates ocean
	Z = np.exp(kde.score_samples(xy))
	Z = Z.reshape(X.shape)

    # plot contours of the density
	levels = np.linspace(0, Z.max(), 25)
	plt.contourf(X, Y, Z, levels=levels, cmap=plt.cm.Reds)
	plt.title('BK CRIME')
	plt.show()
	return Z

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx
    
def crimeheatmap_to_node(node_dic, lnggrid, latgrid, colormap):
    crime_dic = {}
    for node in node_dic:
        tmpx = find_nearest(lnggrid,float(node_dic[node][1])) #lng
        tmpy = find_nearest(latgrid,float(node_dic[node][0])) #lat
        #print tmpx, tmpy
        #crime_dic[node] = node_dic[node][0], node_dic[node][1], colormap[tmpx,tmpy]
        crime_dic[node] = colormap[tmpx,tmpy]        
    return crime_dic
    

def distance_btw_nodes(node1,node2,node_dic):
    return great_circle(node_dic[node1], node_dic[node2]).miles

def accident_weight_btw_nodes(node1, node2, weight_dic):
    if node1 in weight_dic and node2 in weight_dic:
        return weight_dic[node1] + weight_dic[node2]
    elif node1 in weight_dic and node2 not in weight_dic:
        return weight_dic[node1]
    elif node1 not in weight_dic and node2 in weight_dic:
        return weight_dic[node2]
    else:
        return 0

def make_weights_crime(node_dict,edge_dict,feature_dict, feature_factor):
    tmp_edge = {}
    for edge in edge_dict:
        wei = accident_weight_btw_nodes(edge_dict[edge][0], edge_dict[edge][1], feature_dict)
        weight = ((feature_factor*wei) + 1)* distance_btw_nodes(edge_dict[edge][0],edge_dict[edge][1],node_dic)
        tmp_edge[edge] = edge_dict[edge][0], edge_dict[edge][1], weight
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


nodelist_sql = ReadNodefromSql()
edgelist_sql = ReadEdgefromSql()

node_dic = NodeSqltoDic(nodelist_sql)
edge_dic = EdgeSQLtoDic(edgelist_sql)

crime_list = getSQLcrime()

data =  make_data_numpy()

Z = find_kernel(data, numgrid = 1000, bw = 0.002)

crime_dic = crimeheatmap_to_node(node_dic, xgrid,ygrid,Z)
crime_weights  =  make_weights_crime(node_dic,edge_dic,crime_dic, 1)
#addweightstoSql(crime_dic, crime_weights)

