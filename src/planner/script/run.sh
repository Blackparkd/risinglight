#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

while true; do
    clear
    echo -e "${BLUE}RisingLight Query Analyzer =======================${NC}"
    echo -e "${GREEN}1.${NC} Execute Query"
    echo -e "${GREEN}2.${NC} Extract Query Data"
    echo -e "${GREEN}3.${NC} Generate Histogram"
    echo -e "${GREEN}4.${NC} Extract Classes Data"
    echo -e "${GREEN}5.${NC} Generate Classes Stem Plot"
    echo -e "${GREEN}6.${NC} Full Analysis (Execute + Extract + Histogram)"
    echo -e "${GREEN}0.${NC} Exit"
    echo -e "${BLUE}================================================== ${NC}"

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
            echo -e "\n${GREEN}=== Extract Classes Data ===${NC}"
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
                python3 src/planner/script/classes_data_extractor.py "$input_file"
                echo -e "${GREEN}Classes data extracted!${NC}"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;        
        
        5)
            echo -e "\n${GREEN}=== Generate Node Information: Total and Relational ===${NC}"
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
                echo -e "\n${GREEN}Generating Node information for all stages...${NC}"
                for stage in {0..3}; do
                    echo -e "${BLUE}Stage ${stage}...${NC}"
                    python3 src/planner/script/classes_histogram.py "q${query_choice}" "$stage"
                done
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        6)
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
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 10 ]; then
                echo -e "\n${GREEN}Executing Query ${query_choice}...${NC}"
                cargo run --release -- -f tests/mytests/q${query_choice}.sql
                
                echo -e "\n${GREEN}Extracting data...${NC}"
                input_file="src/planner/outputs/query_data/q${query_choice}_data.csv"
                python3 src/planner/script/extractor.py "$input_file"
                
                echo -e "\n${GREEN}Generating histogram...${NC}"
                filtered_file="src/planner/outputs/filtered_query_data/q${query_choice}_data_filtered.csv"
                python3 src/planner/script/graphics.py "$filtered_file"
                
                echo -e "\n${GREEN}Extracting classes data...${NC}"
                python3 src/planner/script/classes_data_extractor.py "q${query_choice}"
                
                echo -e "\n${GREEN}Generating classes plots for all stages...${NC}"
                for stage in {0..3}; do
                    echo -e "${BLUE}Stage ${stage}...${NC}"
                    python3 src/planner/script/classes_histogram.py "q${query_choice}" "$stage"
                done
                
                echo -e "\n${GREEN}Full analysis completed!${NC}"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
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
