#!/bin/bash

# Cores para output
ORANGE='\033[0;33m'  # Alterado de GREEN para ORANGE
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

while true; do
    clear
    echo -e "${BLUE}RisingLight Query Analyzer =======================${NC}"
    echo -e "${ORANGE}1.${NC} Execute Query"
    echo -e "${ORANGE}2.${NC} Extract Query Data"
    echo -e "${ORANGE}3.${NC} Generate Histogram"
    echo -e "${ORANGE}4.${NC} Extract Classes Data"
    echo -e "${ORANGE}5.${NC} Generate Classes Stem Plot"
    echo -e "${ORANGE}6.${NC} Generate Egg Merge Histograms"
    echo -e "${ORANGE}7.${NC} Full Analysis (Execute + Extract + All Histograms)"
    echo -e "${ORANGE}0.${NC} Exit"
    echo -e "${BLUE}================================================== ${NC}"

    read -p "Choose an option: " option

    case $option in
        1)
            echo -e "\n${ORANGE}=== Execute Query ===${NC}"
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
                    echo -e "\n${ORANGE}Executing Query 1...${NC}"
                    cargo run --release -- -f tests/mytests/q1.sql
                    ;;
                2)
                    echo -e "\n${ORANGE}Executing Query 2...${NC}"
                    cargo run --release -- -f tests/mytests/q2.sql
                    ;;
                3)
                    echo -e "\n${ORANGE}Executing Query 3...${NC}"
                    cargo run --release -- -f tests/mytests/q3.sql
                    ;;
                4)
                    echo -e "\n${ORANGE}Executing Query 4...${NC}"
                    cargo run --release -- -f tests/mytests/q4.sql
                    ;;
                5)
                    echo -e "\n${ORANGE}Executing Query 5...${NC}"
                    cargo run --release -- -f tests/mytests/q5.sql
                    ;;
                6)
                    echo -e "\n${ORANGE}Executing Query 6...${NC}"
                    cargo run --release -- -f tests/mytests/q6.sql
                    ;;
                7)
                    echo -e "\n${ORANGE}Executing Query 7...${NC}"
                    cargo run --release -- -f tests/mytests/q7.sql
                    ;;
                8)
                    echo -e "\n${ORANGE}Executing Query 8...${NC}"
                    cargo run --release -- -f tests/mytests/q8.sql
                    ;;
                9)
                    echo -e "\n${ORANGE}Executing Query 9...${NC}"
                    cargo run --release -- -f tests/mytests/q9.sql
                    ;;
                10)
                    echo -e "\n${ORANGE}Executing Query 10...${NC}"
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
            echo -e "\n${ORANGE}=== Extract Last 4 Lines ===${NC}"
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
            echo -e "\n${ORANGE}=== Generate Histogram ===${NC}"
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
            echo -e "\n${ORANGE}=== Extract Classes Data ===${NC}"
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
                echo -e "${ORANGE}Classes data extracted!${NC}"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;        
        
        5)
            echo -e "\n${ORANGE}=== Generate Node Information: Total and Relational ===${NC}"
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
                echo -e "\n${ORANGE}Generating Node information for all stages...${NC}"
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
            echo -e "\n${ORANGE}=== Generate Egg Merge Histograms ===${NC}"
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
                echo -e "\n${ORANGE}Generating Egg Merge Histogram for Query ${query_choice}...${NC}"
                python3 src/planner/script/egg-merges.py "$query_choice"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        7)
            echo -e "\n${ORANGE}=== Full Analysis ===${NC}"
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
                echo -e "\n${ORANGE}Executing Query ${query_choice}...${NC}"
                cargo run --release -- -f tests/mytests/q${query_choice}.sql
                
                echo -e "\n${ORANGE}Extracting data...${NC}"
                input_file="src/planner/outputs/query_data/q${query_choice}_data.csv"
                python3 src/planner/script/extractor.py "$input_file"
                
                echo -e "\n${ORANGE}Generating histogram...${NC}"
                filtered_file="src/planner/outputs/filtered_query_data/q${query_choice}_data_filtered.csv"
                python3 src/planner/script/graphics.py "$filtered_file"
                
                echo -e "\n${ORANGE}Extracting classes data...${NC}"
                python3 src/planner/script/classes_data_extractor.py "q${query_choice}"
                
                echo -e "\n${ORANGE}Generating classes plots for all stages...${NC}"
                for stage in {0..3}; do
                    echo -e "${BLUE}Stage ${stage}...${NC}"
                    python3 src/planner/script/classes_histogram.py "q${query_choice}" "$stage"
                done
                
                echo -e "\n${ORANGE}Generating Egg Merge Histogram...${NC}"
                python3 src/planner/script/egg-merges.py "$query_choice"
                
                echo -e "\n${ORANGE}Full analysis completed!${NC}"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        0)
            echo -e "\n${ORANGE}Exiting...${NC}"
            exit 0
            ;;

        *)
            echo -e "\n${RED}Invalid option${NC}"
            ;;
    esac

    echo -e "\nPress ENTER to continue"
    read
done
