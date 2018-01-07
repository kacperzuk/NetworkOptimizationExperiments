#!/bin/bash

python generate_network.py $1 $2 $3 temp
python greedy_resolver_generated_networks.py temp
echo -n "Nodes: $1 , Edges: $2, Capacity: $3"
echo -n " -- Is that cool?"
read -n 1 yno


if [ "$yno" == "Y" ]; then
	cp network_cplex_model/network/data/test_hist.dat final_networks/net_$1_$2_$3.json
	cp network_cplex_model/network/data/test.dat final_networks/net_$1_$2_$3.dat
	echo "Copied!."
  	exit 1
else
	exit 1
fi