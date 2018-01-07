#!/bin/bash

for i in `ls final_networks/*.json | cut -c16-`;
do
    echo $i 
    python greedy_resolver_generated_networks.py $i > heuristic_outputs/$i
done