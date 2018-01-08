python generate_network.py $1 $2 $3 temp
cp network_cplex_model/network/data/temp_hist.dat final_networks/net_$1_$2_$3.json
cp network_cplex_model/network/data/temp.dat final_networks/net_$1_$2_$3.dat