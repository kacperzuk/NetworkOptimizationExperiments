import xml.etree.ElementTree as ET
import os
import math
import re
import random

paths = []

def parse_file(filepath,filename, cap_multi):
    tree = ET.parse(filepath)
    root = tree.getroot()
    nodes = []
    links = []
    demands = []
    for node in root.iter('{http://sndlib.zib.de/network}node'):
        nodes.append({ "name":node.attrib['id'], "x" : float(node[0][0].text) , "y" : float(node[0][1].text)})

    for x in nodes:
        for y in nodes:
            if x != y:
                cost = math.sqrt((x["x"] - y["x"])*(x["x"] - y["x"]) + (x["y"] - y["y"])*(x["y"] - y["y"]))
                links.append({"src" : x["name"], "dst":y["name"], "cost": cost})

    nodes_count = len(nodes)

    for link in root.iter('{http://sndlib.zib.de/network}link'):
        for l in links:
            l["cap"] = nodes_count * cap_multi
            if (l["src"] == link[0].text and l["dst"] == link[1].text) or (l["src"] == link[1].text and l["dst"] == link[0].text):
                l["cost"] = 0

    for idx, x in enumerate(nodes):
        for jdx, y in enumerate(nodes):
            if idx != jdx:
                demands.append({"src": x["name"], "dst" : y["name"], "volume" : abs(idx - jdx) * 2, "backup": 0})

    random_backup(demands)

    file = re.sub('\.xml$', '', filename)
    path = "network_cplex_model/data/" + file + "_" + str(cap_multi) + ".dat"
    paths.append(file + "_" + str(cap_multi))
    with open(path,"w") as f :
        f.write("Nodes = {")
        for idx, n in enumerate(nodes):
            if idx == len(nodes) - 1:
                f.write("\""+ n["name"] + "\"")
            else:
                 f.write("\""+ n["name"] + "\", ")   
        f.write("};\n")
        f.write("Arcs = {") 
        for idx, l in enumerate(links):
            if idx == len(links) - 1:
                f.write("<\""+ l["src"] + "\",\""+ l["dst"] + "\"," + str(round(l["cap"])) + "," + str(round(l["cost"])) + ">")
            else:
                 f.write("<\""+ l["src"] + "\",\""+ l["dst"] + "\"," + str(round(l["cap"])) + "," + str(round(l["cost"])) + ">, ")
        f.write("};\n")
        f.write("Demands = {") 
        for idx, d in enumerate(demands):
            if idx == len(demands) - 1:
                f.write("<\""+ d["src"] + "\",\""+ d["dst"] + "\"," + str(d["volume"]) + "," + str(d["backup"]) + ">")
            else:
                f.write("<\""+ d["src"] + "\",\""+ d["dst"] + "\"," + str(d["volume"]) + "," + str(d["backup"]) + ">, ")
        f.write("};\n")

def random_backup(demands):
    for x in range(0, 4):
        node_id = random.randint(0, len(demands)-1)
        backup_node = demands[node_id]
        backup_node['backup'] = 1
        demands.append(backup_node)


for filename in os.listdir("networks"):
    # parse_file('networks/' + filename, filename, 2)
    parse_file('networks/' + filename, filename, 2.5)
    parse_file('networks/' + filename, filename, 3)

with open("network_cplex_model/data/paths.txt","w") as f:
    for x in paths:
        f.write(x + "\n")