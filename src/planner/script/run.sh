#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

while true; do
    clear
    echo -e "${BLUE}====== RisingLight Query Analyzer ======${NC}"
    echo "1. Execute Query"
    echo "2. Extract Last 4 Lines"
    echo "3. Generate Graph"
    echo "4. Full Analysis (Execute + Extract + Graph)"
    echo "0. Exit"
    echo "========================================"

    read -p "Choose an option: " option

    case $option in
        1)
            echo -e "\n${GREEN}=== Execute Query ===${NC}"
            echo "1. Query 1 (Basic Query)"
            echo "2. Query 2 (Complex Query)"
            echo "0. Back"
            
            read -p "Select query: " query_choice
            case $query_choice in
                1)
                    echo -e "\n${GREEN}Executing Query 1...${NC}"
                    cargo run --release -- -f tests/mytests/q.sql
                    ;;
                0)
                    continue
                    ;;
                *)
                    echo -e "${RED}Invalid query number!${NC}"
                    ;;
            esac
            ;;

        2)
            echo -e "\n${GREEN}=== Extract Last 4 Lines ===${NC}"
            echo "Digite o caminho do arquivo CSV original:"
            read input_file
            echo $input_file | python3 src/planner/script/extractor.py
            ;;

        3)
            echo -e "\n${GREEN}=== Generate Graph ===${NC}"
            echo "Digite o caminho do arquivo CSV filtrado:"
            read filtered_file
            echo $filtered_file | python3 src/planner/script/graphics.py
            ;;

        4)
            echo -e "\n${GREEN}=== Full Analysis ===${NC}"
            # Execute Query
            echo -e "1. Executing Query..."
            cargo run --release -- -f tests/mytests/q.sql
            
            # Extract data
            echo -e "\n2. Extracting data..."
            input_file="src/planner/outputs/query_data/q_data.csv"
            echo $input_file | python3 src/planner/script/extractor.py
            
            # Generate graph
            echo -e "\n3. Generating graph..."
            filtered_file="src/planner/outputs/filtered_query_data/q_data_filtered.csv"
            echo $filtered_file | python3 src/planner/script/graphics.py
            ;;

        0)
            echo -e "\n${GREEN}Exiting...${NC}"
            exit 0
            ;;

        *)
            echo -e "\n${RED}Invalid option${NC}"
            ;;
    esac

    echo -e "\nPressione ENTER para continuar..."
    read
done
