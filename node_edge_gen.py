#!/usr/local/bin/python


"""
Usage: node_edge_gen.py

This script reads in a a osm file and determines the nodes and edges
and writes them as dictionies to be used in networkX
"""

try:
    from xml.etree import cElementTree as ET
    from matplotlib import pylab as plt 
except ImportError, e:
    from xml.etree import ElementTree as ET


def extract_intersections(osm, verbose=True):
    # This function takes an osm file as an input. It then goes through each xml 
    # element and searches for nodes that are shared by two or more ways.
    # Parameter:
    # - osm: An xml file that contains OpenStreetMap's map information
    # - verbose: If true, print some outputs to terminal.
    # 
    # Ex) extract_intersections('WashingtonDC.osm')
    #
    tree = ET.parse(osm)
    root = tree.getroot()
    counter = {}
    way_counter = {}
    node_intersections = {}
    for child in root:
        if child.tag == 'way':
            hwstat = False
            way_node = []
            #while hwstat == False:
            for item in child:
                if item.tag == 'tag' and item.attrib['k'] == 'highway':
                    way_id = child.attrib['id']
               #     way_name = item.attrib['v'] pull some name data to save later!
                    hwstat = True
            if hwstat == True:
                for item in child:
                    if item.tag == 'nd':
                        nd_ref = item.attrib['ref']
                        way_node.append(nd_ref)
                        if not nd_ref in counter:
                            counter[nd_ref] = 0
                        counter[nd_ref] += 1
                        #way_counter[way_id] = []
                way_counter[way_id] = way_node
            else:
                hwstat = False
    # Find nodes that are shared with more than one way, which
    # might correspond to intersections
    intersections = filter(lambda x: counter[x] > 1,  counter)

    # Extract intersection coordinates
    # You can plot the result using this url.
    # http://www.darrinward.com/lat-long/
    intersection_coordinates = []
    for child in root:
        if child.tag == 'node' and child.attrib['id'] in intersections:
            coordinate = child.attrib['lat'] + ',' + child.attrib['lon']
            if verbose:
                print coordinate
            intersection_coordinates.append(coordinate)
            node_intersections[child.attrib['id']] = (child.attrib['lat'], child.attrib['lon'])

    return intersection_coordinates, way_counter, node_intersections


def inters_latlong(string):
    lat_float = float(string.split(',')[0])
    long_float = float(string.split(',')[1])
    return [lat_float, long_float]

def ways_to_edge(waydict, nodes):
    ways3 = {}
    for w in waydict:
        num_el = len(waydict[w])
        new_w = []
        for i in waydict[w]:
            if nodes.get(i) == None: 
                tmp = 0
            else:
                new_w.append(i)
        ways3[w] = new_w

    
    ways4 = {}
    for w in ways3:
        num_el = len(ways3[w])
        if num_el == 2:
            ways4[w]=ways3[w]
        elif num_el > 2:
            for j in range(0,num_el-1):
                new_list= [ways3[w][j], ways3[w][j+1]]
                ways4[w+str(j)] = new_list
    return ways4


def plot_nodes_edges(nodes,edges):
    for d in nodes:
        plt.scatter(nodes[d][0],nodes[d][1])
    

    for w in edges:
        node_list = []

        for i in edges[w]:
            if i in nodes: 
                node_list.append(nodes[i]) 
            
        plt.plot(*zip(*node_list))
    plt.show()
#filename = 'full_bklynmap'
#filename = 'map_extrasmall.osm'
#int_string, ways_bk, nodes_bk = extract_intersections(filename, verbose= False)
#edges_bk = ways_to_edge(ways_bk, nodes_bk)
#plot_nodes_edges(nodes_bk,edges_bk)





#import sys
#if len(sys.argv) < 2:
#   print __doc__ % {'scriptName' : sys.argv[0].split("/")[-1]}
#   sys.exit(0)
