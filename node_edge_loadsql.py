#!/usr/local/bin/python


"""
Usage: node_edge_loadsql.py

This script generates  and writes the node and edge OSM data to a mySQL db
"""

import MySQLdb
import node_edge_gen as neg


#generate nodes and edges
filename = 'map_bk_test'
int_string, ways, nodes = neg.extract_intersections(filename, verbose= False)
edges = neg.ways_to_edge(ways, nodes)
#neg.plot_nodes_edges(nodes,edges)

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
CREATE TABLE bk_nodes(
    nodeid BIGINT NOT NULL,
    latitude DOUBLE(11,7) NOT NULL,
    longitude DOUBLE(11,7) NOT NULL,
    PRIMARY KEY (nodeid)
    )
    """)

cursor.execute("""
CREATE TABLE bk_edges(
    edgeid BIGINT NOT NULL,
    node1 BIGINT NOT NULL,
    node2 BIGINT NOT NULL,
    PRIMARY KEY (edgeid)
    )
    """)

# SQL CALL USED FOR INSERTING INTO DBs

add_node= ("INSERT INTO bk_nodes "
           " (nodeid, latitude, longitude)"
           " VALUES (%s, %s, %s)")

add_edge= ("INSERT INTO bk_edges "
           " (edgeid, node1, node2)"
           " VALUES (%s, %s, %s)")


# add the node_dict and node_edge into the database

for no in nodes:
    node_data =  no, nodes[no][0],nodes[no][1]
    cursor.execute(add_node, node_data)
    
for ed in edges:
    edge_data = ed, edges[ed][0], edges[ed][1]
    cursor.execute(add_edge, edge_data)

# commit the changes to the db
db_connect.commit()

#close database connection
cursor.close()
db_connect.close()

    