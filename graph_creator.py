import networkx as nx
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

tree = ET.parse('networks/abilene.xml')
root = tree.getroot()
graph = nx.DiGraph()

positions = {}

for node in root.iter('{http://sndlib.zib.de/network}node'):
  graph.add_node(node.attrib['id'], x = node[0][0].text, y = node[0][1].text)
  positions[node.attrib['id']] = [float(node[0][0].text), float(node[0][1].text)]

for link in root.iter('{http://sndlib.zib.de/network}link'):
  graph.add_edge(link[0].text,link[1].text , id = link.attrib['id'])
  graph.add_edge(link[1].text,link[0].text , id = link.attrib['id'])


nx.draw_networkx(graph, pos=positions, with_labels = True)
# nx.draw_networkx_edge_labels(graph, positions)
plt.show()