import networkx as nx
import xml.etree.ElementTree as ET
import sys
import random
import math
import json

BACKUP_DEMANDS = 4
SEED = 1337


backup_demands = list()

def demands_generator(nodes_number):

    demands = []

    for idx in range(0, nodes_number):
        for jdy in range(0, nodes_number):
            if idx != jdy:
                demands.append({"src": idx, "dst": jdy, "volume": abs(idx - jdy)*2, "backup": 0})

    print("Demands number: ", len(demands))
    return demands

def random_backup(demands):
    for x in range(0, BACKUP_DEMANDS):
        node_id = random.randint(0, len(demands)-1)
        backup_node = demands[node_id]
        backup_node['backup'] = 1
        demands.append(backup_node)
        backup_demands.append(backup_node)

def calc_cost(G, idx, idy):

    A = (G.node[idx]['x'] - G.node[idy]['x'])
    B = (G.node[idx]['y'] - G.node[idy]['y'])

    return round(math.sqrt(A**2 + B**2)**2 / 2)

def save_to(filename, G, demands):

    # nx.write_gml(G, "test")
    filepath = "network_cplex_model/network/data/" + filename + ".dat"

    with open(filepath, "w") as f :
        f.write("Nodes = {")
        temp = 0
        for idx in G.nodes(True):
            if temp == len(G.nodes()) - 1:
                f.write("\"" + str(idx[0]) + "\"")
            else:
                f.write("\"" + str(idx[0]) + "\", ")
                temp += 1
        f.write("};\n")
        f.write("Arcs = {")
        arc_temp = 0
        for e in G.edges(None, True):
            if arc_temp == len(G.edges()) - 1:
                f.write("<\""+ str(e[0]) + "\",\""+ str(e[1]) + "\"," + str(e[2]["cap"]) + "," + str(e[2]["cost"]) + ">, ")
                f.write("<\""+ str(e[1]) + "\",\""+ str(e[0]) + "\"," + str(e[2]["cap"]) + "," + str(e[2]["cost"]) + ">")
            else:
                f.write("<\""+ str(e[0]) + "\",\""+ str(e[1]) + "\"," + str(e[2]["cap"]) + "," + str(e[2]["cost"]) + ">, ")
                f.write("<\""+ str(e[1]) + "\",\""+ str(e[0]) + "\"," + str(e[2]["cap"]) + "," + str(e[2]["cost"]) + ">, ")
                arc_temp += 1
        f.write("};\n")
        f.write("Demands = {")
        for idx, d in enumerate(demands):
            if idx == len(demands) - 1:
                f.write("<\""+ str(d["src"]) + "\",\""+ str(d["dst"]) + "\"," + str(d["volume"]) + "," + str(d["backup"]) + ">")
            else:
                f.write("<\""+ str(d["src"]) + "\",\""+ str(d["dst"]) + "\"," + str(d["volume"]) + "," + str(d["backup"]) + ">, ")
        f.write("};\n")

def save_to_heuristic(filename, G):
    nodes = list(G.nodes(True));
    edges = list()

    for e in G.edges(None, True):
        if e[2]["cost"] == 0:
            edges.append(e)

    output_data = dict()
    output_data['nodes'] = nodes
    output_data['edges'] = edges
    output_data['backups'] = backup_demands

    filepath = "network_cplex_model/network/data/" + filename + "_hist.dat"
    with open(filepath, "w") as f :
        f.write(json.dumps(output_data))
        f.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: generate_network.py nodes_number edges_number link_capacity output_file")
        print("Creates file in network_cplex_model/network/data/<output_file>.dat")
        sys.exit(2)

    nodes_number = int(sys.argv[1])
    edges_number = int(sys.argv[2])
    LINK_CAP = int(sys.argv[3])
    filename = sys.argv[4]

    G = nx.gnm_random_graph(nodes_number, edges_number, SEED)
    #G = nx.newman_watts_strogatz_graph(10, 3, 0.2, SEED)
    #G = nx.connected_watts_strogatz_graph(7, 3, 0.2, 2 , SEED)

    for itr in G.nodes():
        G.node[itr]['x'] = round(random.uniform(72, 36), 3) # europe N-S,
        G.node[itr]['y'] = round(random.uniform(-9, 68), 3) # europe W-E

    # remember to create "reverse" edge
    for itr in G.edges():
        G[itr[0]][itr[1]].update(cap=LINK_CAP)
        G[itr[0]][itr[1]].update(cost=0)

    for itr in G.edges():
        print("Base links", itr)

    for idx in range(0, nodes_number):
        for idy in range(0, nodes_number):
            if idx != idy:
                try:
                    G[idx][idy]
                    G[idy][idx]
                    #print("Link", idx, idy, "exists")
                except KeyError: # xD
                    print("Add link", idx, idy)
                    G.add_edge(idx, idy, cap=LINK_CAP, cost=calc_cost(G, idx, idy))

    demands = demands_generator(nodes_number)
    random_backup(demands)

    save_to(filename, G, demands)
    save_to_heuristic(filename, G)
