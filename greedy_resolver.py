import sys
import math
from pprint import pprint
import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt

def link_cost(v1, v2):
    return math.sqrt(v1["x"]*v2["x"] + v1["y"]*v2["y"])

def solve(network_file, link_capacity):
    tree = ET.parse(network_file)
    root = tree.getroot()
    graph = nx.DiGraph()

    for node in root.iter('{http://sndlib.zib.de/network}node'):
        # tutaj maja byc node'y id, x, y 
        graph.add_node(node.attrib['id'], x=float(node[0][0].text), y=float(node[0][1].text))

    for link in root.iter('{http://sndlib.zib.de/network}link'):
        # id src, id dest, capacity - global, albo z obiektu
        # koszt zerowy
        graph.add_edge(link[0].text,link[1].text,
                id=link.attrib['id'],
                capacity_left=link_capacity,
                cost=0)
        graph.add_edge(link[1].text,link[0].text,
                id=link.attrib['id'],
                capacity_left=link_capacity,
                cost=0)

    demands = []
    i = 0
    for vi in graph.nodes:
        i += 1
        j = 0
        for vj in graph.nodes:
            j += 1
            if vi == vj:
                continue
            d = abs(i-j) * 2
            if d > link_capacity:
                raise Exception("Demand is greater than link_capacity, problem unsolvable: %d > %d" % (d, link_capacity))
            demands.append((vi, vj, d))

    return graph, demands

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: greedy_resolver.py network_file.xml link_capacity")
        print("  - link_capacity is in Gbit/s")
        sys.exit(2)
    graph, demands = solve(sys.argv[1], int(sys.argv[2]))
    demands.sort(key=lambda x: x[2], reverse=True)
    tunnels = []
    for d in demands:
        tmpgraph = graph.copy()

        edges_to_remove = []
        for v1, v2, attr in tmpgraph.edges(data=True):
            if attr["capacity_left"] < d[2]:
                edges_to_remove.append((v1,v2))
        tmpgraph.remove_edges_from(edges_to_remove)

        try:
            p = nx.dijkstra_path(tmpgraph, d[0], d[1])
        except nx.exception.NetworkXNoPath:
            minedge = None
            for vt1 in tmpgraph.nodes:
                for vt2 in tmpgraph.nodes:
                    tmpgraph2 = tmpgraph.copy()
                    tmpgraph2.add_edge(vt1, vt2)
                    tmpgraph2.add_edge(vt2, vt1)
                    cost = link_cost(tmpgraph2.nodes[vt2], tmpgraph2.nodes[vt2])
                    if not minedge or cost < minedge[2]:
                        try:
                            p = nx.dijkstra_path(tmpgraph2, d[0], d[1])
                        except nx.exception.NetworkXNoPath:
                            continue
                        minedge = (vt1, vt2, cost, p)
            if not minedge:
                print("Couldn't find path for demand:", d)
                raise Exception("Unsolvable with greedy algorithm")
            graph.add_edge(minedge[0], minedge[1], capacity_left=int(sys.argv[2]), cost=minedge[2]/2)
            graph.add_edge(minedge[1], minedge[0], capacity_left=int(sys.argv[2]), cost=minedge[2]/2)

        tunnels.append(p)
        for e in nx.utils.pairwise(p):
            graph.edges[e]["capacity_left"] -= d[2]

    print("Tunnels")
    pprint(tunnels)
    print("Edges to add:")
    pprint([ e for e in graph.edges(data=True) if e[2]["cost"] > 0])
    print("Total cost:")
    pprint(sum([ e[2]["cost"] for e in graph.edges(data=True)]))
