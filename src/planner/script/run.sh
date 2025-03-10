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
    echo "2. Extract Query Data"
    echo "3. Generate Histogram"
    echo "4. Full Analysis (Execute + Extract + Histogram)"
    echo "0. Exit"
    echo "========================================"

    read -p "Choose an option: " option

    case $option in
        1)
            echo -e "\n${GREEN}=== Execute Query ===${NC}"
            echo "1. Query 1"
            echo "2. Query 2"
            echo "3. Query 3"
            echo "4. Query 4"
            echo "5. Query 5"
            echo "6. Query 6"
            echo "7. Query 7"
            echo "8. Query 8"
            echo "9. Query 9"
            echo "10. Query 10"
            echo "0. Back"
            
            read -p "Select query: " query_choice
            case $query_choice in
                1)
                    echo -e "\n${GREEN}Executing Query 1...${NC}"
                    cargo run --release -- -f tests/mytests/q1.sql
                    ;;
                2)
                    echo -e "\n${GREEN}Executing Query 2...${NC}"
                    cargo run --release -- -f tests/mytests/q2.sql
                    ;;
                3)
                    echo -e "\n${GREEN}Executing Query 3...${NC}"
                    cargo run --release -- -f tests/mytests/q3.sql
                    ;;
                4)
                    echo -e "\n${GREEN}Executing Query 4...${NC}"
                    cargo run --release -- -f tests/mytests/q4.sql
                    ;;
                5)
                    echo -e "\n${GREEN}Executing Query 5...${NC}"
                    cargo run --release -- -f tests/mytests/q5.sql
                    ;;
                6)
                    echo -e "\n${GREEN}Executing Query 6...${NC}"
                    cargo run --release -- -f tests/mytests/q6.sql
                    ;;
                7)
                    echo -e "\n${GREEN}Executing Query 7...${NC}"
                    cargo run --release -- -f tests/mytests/q7.sql
                    ;;
                8)
                    echo -e "\n${GREEN}Executing Query 8...${NC}"
                    cargo run --release -- -f tests/mytests/q8.sql
                    ;;
                9)
                    echo -e "\n${GREEN}Executing Query 9...${NC}"
                    cargo run --release -- -f tests/mytests/q9.sql
                    ;;
                10)
                    echo -e "\n${GREEN}Executing Query 10...${NC}"
                    cargo run --release -- -f tests/mytests/q10.sql
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
            echo "Select query number (1-10):"
            echo "1. Query 1"
            echo "2. Query 2"
            echo "3. Query 3"
            echo "4. Query 4"
            echo "5. Query 5"
            echo "6. Query 6"
            echo "7. Query 7"
            echo "8. Query 8"
            echo "9. Query 9"
            echo "10. Query 10"
            echo "0. Back"
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 10 ]; then
                input_file="src/planner/outputs/query_data/q${query_choice}_data.csv"
                python3 src/planner/script/extractor.py "$input_file"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        3)
            echo -e "\n${GREEN}=== Generate Histogram ===${NC}"
            echo "Select query number (1-10):"
            echo "1. Query 1"
            echo "2. Query 2"
            echo "3. Query 3"
            echo "4. Query 4"
            echo "5. Query 5"
            echo "6. Query 6"
            echo "7. Query 7"
            echo "8. Query 8"
            echo "9. Query 9"
            echo "10. Query 10"
            echo "0. Back"
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 10 ]; then
                filtered_file="src/planner/outputs/filtered_query_data/q${query_choice}_data_filtered.csv"
                python3 src/planner/script/graphics.py "$filtered_file"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        4)
            echo -e "\n${GREEN}=== Full Analysis ===${NC}"
            echo "Select query number (1-10):"
            echo "1. Query 1"
            echo "2. Query 2"
            echo "3. Query 3"
            echo "4. Query 4"
            echo "5. Query 5"
            echo "6. Query 6"
            echo "7. Query 7"
            echo "8. Query 8"
            echo "9. Query 9"
            echo "10. Query 10"
            echo "0. Back"
            
            read -p "Select query: " query_num
            
            if [ "$query_num" -ge 1 ] && [ "$query_num" -le 10 ]; then
                # Execute Query
                echo -e "1. Executing Query $query_num..."
                cargo run --release -- -f tests/mytests/q${query_num}.sql
                
                # Extract data
                echo -e "\n2. Extracting data..."
                input_file="src/planner/outputs/query_data/q${query_num}_data.csv"
                python3 src/planner/script/extractor.py "$input_file"
                
                # Generate Histogram
                echo -e "\n3. Generating Histogram..."
                filtered_file="src/planner/outputs/filtered_query_data/q${query_num}_data_filtered.csv"
                python3 src/planner/script/graphics.py "$filtered_file"
                
                echo -e "${GREEN}Full analysis completed!${NC}"
            elif [ "$query_num" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number! Please select a number between 1 and 10.${NC}"
            fi
            ;;

        0)
            echo -e "\n${GREEN}Exiting...${NC}"
            exit 0
            ;;

        *)
            echo -e "\n${RED}Invalid option${NC}"
            ;;
    esac

    echo -e "\nPress ENTER to continue"
    read
done
