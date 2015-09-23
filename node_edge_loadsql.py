#!/usr/local/bin/python


"""
Usage: node_edge_loadsql.py

This script generates and writes the node and edge OSM data to a mySQL db
"""

import MySQLdb
import node_edge_gen as neg


#generate nodes and edges
#filename = 'map_region2'
filename =  'northern_bk_map'
int_string, ways, nodes = neg.extract_intersections(filename, verbose= False)
edges = neg.ways_to_edge(ways, nodes)
#neg.plot_nodes_edges(nodes,edges)

print 'nodes', len(nodes)
print 'edges', len(edges)


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

cursor = db_connect.cursor()

#Do you need to create the database?
#cursor.execute('create database bk_map')

#CREATE TABLES FOR NODES AND EDGES

cursor.execute("""
CREATE TABLE bk_nodes_full(
    id INTEGER NOT NULL AUTO_INCREMENT,
    nodeid MEDIUMTEXT NOT NULL,
    latitude DOUBLE(12,8) NOT NULL,
    longitude DOUBLE(12,8) NOT NULL,
    PRIMARY KEY (id)
    )
    """)

cursor.execute("""
CREATE TABLE bk_edges_full(
	id INTEGER NOT NULL AUTO_INCREMENT,
    edgeid MEDIUMTEXT NOT NULL,
    node1 MEDIUMTEXT NOT NULL,
    node2 MEDIUMTEXT NOT NULL,
    PRIMARY KEY (id)
    )
    """)

# SQL CALL USED FOR INSERTING INTO DBs

add_node = ("INSERT INTO bk_nodes_full "
           " (nodeid, latitude, longitude)"
           " VALUES (%s, %s, %s)")

add_edge = ("INSERT INTO bk_edges_full"
           " (edgeid, node1, node2)"
           " VALUES (%s, %s, %s)")


# add the node_dict and node_edge into the database

for no in nodes:
    node_data =  no, nodes[no][0],nodes[no][1]
    cursor.execute(add_node, node_data)
count = 0
for ed in edges:
	count += 1
	edge_data = ed, edges[ed][0], edges[ed][1]
	cursor.execute(add_edge, edge_data)

print 'edges_written', count
# commit the changes to the db
db_connect.commit()

#close database connection
cursor.close()
db_connect.close()

    