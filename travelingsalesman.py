start_tuple = (40.6868, -73.9824)
bar_tuple_list = [( 40.68680000, -73.97510000),(40.68200000, -73.98020000),( 40.69340000, -73.97300000), ( 40.69330000,-73.96910000),(40.67720000, -73.95740000)]
end_tuple = (40.67430000,-73.99540000)

def crawl_path(G, start_tuple, bar_tuple_list, end_tuple):
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
    return min_path, line_path

crawl_path(start_tuple, bar_tuple_list, end_tuple)