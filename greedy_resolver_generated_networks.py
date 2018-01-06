import sys
import math
from pprint import pprint
import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
import json

def link_cost(v1, v2):
    dx = v1["x"]-v2["x"]
    dy = v1["y"]-v2["y"]
    return math.sqrt(dx*dx + dy*dy)

def load_graph(network_file, link_capacity):
    graph = nx.DiGraph()
    filepath = "network_cplex_model/network/data/" + network_file + "_hist.dat"
    with open(filepath, 'r') as f:
        network_data = json.load(f)

        graph = nx.DiGraph()

        for node in network_data['nodes']:
            graph.add_node(node[0], x=float(node[1]['x']), y=float(node[1]['y']))

        for link in network_data['edges']:
            graph.add_edge(link[0],link[1],
                    id=1, #TODO
                    capacity_left=link[2]['cap'],
                    cost=0)
            graph.add_edge(link[1],link[0],
                    id=1, #TODO
                    capacity_left=link[2]['cap'],
                    cost=0)

    return graph

def calculate_demands(graph, link_capacity):
    demands = []
    i = 0
    for vi in graph.nodes:
        i += 1
        j = 0
        for vj in graph.nodes:
            j += 1
            if j <= i:
                continue
            d = abs(i-j) * 2
            if d > link_capacity:
                raise Exception("Demand is greater than link_capacity, problem unsolvable: %d > %d" % (d, link_capacity))
            assert (vi, vj, d) not in demands
            demands.append((vi, vj, d))
            assert (vj, vi, d) not in demands
            demands.append((vj, vi, d))
    return demands

def parse_premiums(network_file):
    filepath = "network_cplex_model/network/data/" + network_file + "_hist.dat"
    premium_pairs = []

    with open(filepath, 'r') as f:
        network_data = json.load(f)
        for backup in network_data['backups']:
            premium_pairs.append((backup['src'],backup['dst']))
    return premium_pairs

def remove_too_small_edges(graph, demand):
    tmpgraph = graph.copy()
    edges_to_remove = []
    for v1, v2, attr in tmpgraph.edges(data=True):
        if attr["capacity_left"] < demand:
            edges_to_remove.append((v1,v2))
    tmpgraph.remove_edges_from(edges_to_remove)
    return tmpgraph

def find_best_add_edge_v1(existing_edges, graph, src, dst):
    minedge = None
    for vt1 in graph.nodes:
        for vt2 in graph.nodes:
            if ((vt1,vt2) not in existing_edges and
                (vt2,vt1) not in existing_edges):
                tmpgraph = graph.copy()
                tmpgraph.add_edge(vt1, vt2)
                tmpgraph.add_edge(vt2, vt1)
                cost = link_cost(tmpgraph.nodes[vt1], tmpgraph.nodes[vt2])
                if not minedge or cost < minedge[2]:
                    try:
                        p = nx.dijkstra_path(tmpgraph, src, dst)
                    except nx.exception.NetworkXNoPath:
                        continue
                    minedge = (vt1, vt2, cost)
    if not minedge:
        print("Couldn't find path for:", (src,dst))
        raise Exception("Unsolvable with greedy algorithm")
    return p, minedge

def find_best_add_edge_v2(existing_edges, graph, src, dst):
    if ((src,dst) in existing_edges or
        (dst,src) in existing_edges):
        raise Exception("Direct link between two nodes already exist, not solvable with greedy v2 algorithm :(")
    tmpgraph = graph.copy()
    tmpgraph.add_edge(src, dst)
    tmpgraph.add_edge(dst, src)
    cost = link_cost(tmpgraph.nodes[src], tmpgraph.nodes[dst])
    p = nx.dijkstra_path(tmpgraph, src, dst)
    if not p:
        print("Couldn't find path for demand:", d)
        raise Exception("Unsolvable with greedy algorithm")
    return p, (src, dst, cost)

def find_best_add_edge_v3(existing_edges, graph, src, dst):
    a = None
    b = None
    for c in nx.algorithms.components.strongly_connected_components(graph):
        if src in c and dst in c:
            raise Exception("OOO")
        if src in c:
            a = c
        if dst in c:
            b = c
    if not a or not b:
        raise Exception(":(")

    minedge = None
    for v1 in a:
        for v2 in b:
            if ((v1,v2) not in existing_edges and
                (v2,v1) not in existing_edges):
                c = link_cost(tmpgraph.nodes[v1],tmpgraph.nodes[v2])
                if not minedge or c < minedge[2]:
                    minedge = (v1,v2,c)
    if not minedge:
        raise Exception("Unsolvable with greedy algorithm: all links joining 2 currently separated components already exist! :(")

    tmpgraph.add_edge(minedge[0], minedge[1])
    tmpgraph.add_edge(minedge[1], minedge[0])
    p = nx.dijkstra_path(tmpgraph, src, dst)
    if not p:
        print("Couldn't find path for demand:", d)
        raise Exception("Unsolvable with greedy algorithm")
    return p, minedge

def setup_path(existing_edges, graph, src, dst, new_link_capacity):
    edges_to_add = []
    try:
        p = nx.dijkstra_path(tmpgraph, src, dst)
    except nx.exception.NetworkXNoPath:
        p, edge = find_best_add_edge_v3(existing_edges, graph, src, dst)
        attrs = {
            "capacity_left": new_link_capacity,
            "cost": edge[2]/2
        }
        edges_to_add.append((edge[0], edge[1], attrs))
        edges_to_add.append((edge[1], edge[0], attrs))
    return p, edges_to_add

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) % 2 != 1:
        print("Usage: greedy_resolver.py network_file.xml link_capacity premium_pairs...")
        print("  - link_capacity is in Gbit/s")
        sys.exit(2)
    link_capacity = int(sys.argv[2])
    graph = load_graph(sys.argv[1], link_capacity)
    demands = calculate_demands(graph, link_capacity)
    premium_pairs = parse_premiums(sys.argv[1])

    demands.sort(key=lambda x: x[2], reverse=True)

    tunnels = []
    i = 0
    for src_node, dst_node, demand_bw in demands:
        i += 1
        print("Processing demand {}/{}".format(i, len(demands)), end="             \r")
        tmpgraph = remove_too_small_edges(graph, demand_bw)

        path, new_edges = setup_path(graph.edges, tmpgraph, src_node, dst_node, link_capacity)
        graph.add_edges_from(new_edges)

        is_premium = ((src_node, dst_node) in premium_pairs or
                      (dst_node, src_node) in premium_pairs)

        tunnels.append({ "path": path, "premium": is_premium, "backup": False })

        for e in nx.utils.pairwise(path):
            graph.edges[e]["capacity_left"] -= demand_bw

        if is_premium:
            tmpgraph = remove_too_small_edges(graph, demand_bw)
            tmpgraph.remove_edges_from(list(nx.utils.pairwise(path)))

            path, new_edges = setup_path(graph.edges, tmpgraph, src_node, dst_node, link_capacity)
            graph.add_edges_from(new_edges)

            is_premium = ((src_node, dst_node) in premium_pairs or
                          (dst_node, src_node) in premium_pairs)

            tunnels.append({ "path": path, "premium": is_premium, "backup": True })

            for e in nx.utils.pairwise(path):
                graph.edges[e]["capacity_left"] -= demand_bw

    print("")
    print("Tunnels")
    pprint(tunnels)
    print("Edges to add:")
    pprint([ e for e in graph.edges(data=True) if e[2]["cost"] > 0])
    print("Total cost:")
    pprint(sum([ e[2]["cost"] for e in graph.edges(data=True)]))
