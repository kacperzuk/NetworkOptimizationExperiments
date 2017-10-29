import networkx as nx
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

tree = ET.parse('networks/atlanta.xml')
root = tree.getroot()
graph = nx.DiGraph()

for node in root.iter('{http://sndlib.zib.de/network}node'):
  graph.add_node(node.attrib['id'], x = node[0][0].text, y = node[0][1].text)

for link in root.iter('{http://sndlib.zib.de/network}link'):
  graph.add_edge(link[0].text,link[1].text , id = link.attrib)
  graph.add_edge(link[1].text,link[0].text , id = link.attrib)


nx.draw(graph, pos=nx.spring_layout(graph),with_labels = True)
plt.show()