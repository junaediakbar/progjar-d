#!/bin/bash

read -p "Enter URLs (space separated): " urls_string
urls=(${urls_string})

read -p "Enter number of requests (space separated): " requests_string
requests=(${requests_string})

read -p "Enter number of concurrency level (space separated): " con_levels_string
con_levels=(${con_levels_string})

for url in "${urls[@]}"; do
    for con in "${con_levels[@]}"; do
        for req in "${requests[@]}"; do
            if [ $con -gt $req ]; then
                continue
            fi

            echo "Benchmarking $url with $con connections and $req requests"
            ab -n $req -c $con $url > "results/ab-${con}-${req}-${url##*/}.txt" 2>&1 || sleep 60
        done
    done
done