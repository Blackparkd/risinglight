#!/bin/bash

# Cores para output
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Função para mostrar a lista completa de queries
show_query_list() {
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
    echo "11. Query 11"
    echo "12. Query 12"
    echo "13. Query 13"
    echo "14. Query 14"
    echo "15. Query 15"
    echo "16. Query 16"
    echo "17. Query 17"
    echo "18. Query 18"
    echo "19. Query 19"
    echo "20. Query 20"
    echo "21. Query 21"
    echo "22. Query 22"
    echo "0. Back"
}

# Função para executar análise completa para uma query
run_full_analysis() {
    query_num=$1
    echo -e "\n${GREEN}===============================================${NC}"
    echo -e "${GREEN}=== Iniciando análise completa da Query $query_num ===${NC}"
    echo -e "${GREEN}===============================================${NC}"
    
    echo -e "\n${ORANGE}Executando Query ${query_num}...${NC}"
    cargo run --release -- -f tests/mytests/q${query_num}.sql
    
    echo -e "\n${ORANGE}Extraindo dados...${NC}"
    input_file="src/planner/outputs/query_data/q${query_num}_data.csv"
    python3 src/planner/script/extractor.py "$input_file"
    
    echo -e "\n${ORANGE}Gerando histograma...${NC}"
    filtered_file="src/planner/outputs/filtered_query_data/q${query_num}_data_filtered.csv"
    python3 src/planner/script/graphics.py "$filtered_file"
    
    echo -e "\n${ORANGE}Extraindo dados das classes...${NC}"
    python3 src/planner/script/classes_data_extractor.py "q${query_num}"
    
    echo -e "\n${ORANGE}Gerando gráficos de classes para todos os estágios...${NC}"
    for stage in {0..3}; do
        echo -e "${BLUE}Estágio ${stage}...${NC}"
        python3 src/planner/script/classes_histogram.py "q${query_num}" "$stage"
    done
    
    echo -e "\n${ORANGE}Gerando histograma Egg Merge...${NC}"
    python3 src/planner/script/egg-merges.py "$query_num"
    
    echo -e "\n${GREEN}Análise completa da Query $query_num finalizada!${NC}"
}

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
    echo -e "${ORANGE}8.${NC} Batch Analysis (Run multiple queries)"
    echo -e "${ORANGE}0.${NC} Exit"
    echo -e "${BLUE}================================================== ${NC}"

    read -p "Choose an option: " option

    case $option in
        1)
            echo -e "\n${ORANGE}=== Execute Query ===${NC}"
            show_query_list
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
                echo -e "\n${ORANGE}Executing Query ${query_choice}...${NC}"
                cargo run --release -- -f tests/mytests/q${query_choice}.sql
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        2)
            echo -e "\n${ORANGE}=== Extract Last 4 Lines ===${NC}"
            echo "Select query number (1-22):"
            show_query_list
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
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
            echo "Select query number (1-22):"
            show_query_list
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
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
            echo "Select query number (1-22):"
            show_query_list

            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
                echo -e "\n${ORANGE}Extraindo dados das classes para Query ${query_choice}...${NC}"
                python3 src/planner/script/classes_data_extractor.py "q${query_choice}"
                echo -e "${GREEN}Classes data extracted!${NC}"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;        
        
        5)
            echo -e "\n${ORANGE}=== Generate Node Information: Total and Relational ===${NC}"
            echo "Select query number (1-22):"
            show_query_list
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
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
            echo "Select query number (1-22):"
            show_query_list
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
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
            echo "Select query number (1-22):"
            show_query_list
            
            read -p "Select query: " query_choice
            
            if [ "$query_choice" -ge 1 ] && [ "$query_choice" -le 22 ]; then
                run_full_analysis "$query_choice"
            elif [ "$query_choice" -eq 0 ]; then
                continue
            else
                echo -e "${RED}Invalid query number!${NC}"
            fi
            ;;

        8)
            echo -e "\n${ORANGE}=== Batch Analysis ===${NC}"
            echo "1. Run Full Analysis for ALL queries (1-22)"
            echo "2. Run Full Analysis for a range of queries"
            echo "3. Run Full Analysis for specific queries"
            echo "0. Back"
            
            read -p "Choose an option: " batch_option
            
            case $batch_option in
                1)
                    echo -e "\n${ORANGE}Running full analysis for ALL queries (1-22)...${NC}"
                    start_time=$(date +%s)
                    
                    for q in {1..22}; do
                        run_full_analysis $q
                    done
                    
                    end_time=$(date +%s)
                    duration=$((end_time - start_time))
                    hours=$((duration / 3600))
                    minutes=$(( (duration % 3600) / 60 ))
                    seconds=$((duration % 60))
                    
                    echo -e "\n${GREEN}==============================================${NC}"
                    echo -e "${GREEN}All queries processed! Total time: ${hours}h ${minutes}m ${seconds}s${NC}"
                    echo -e "${GREEN}==============================================${NC}"
                    ;;
                    
                2)
                    read -p "Enter start query (1-22): " start_query
                    read -p "Enter end query (1-22): " end_query
                    
                    if [[ $start_query -ge 1 && $start_query -le 22 && $end_query -ge 1 && $end_query -le 22 && $start_query -le $end_query ]]; then
                        echo -e "\n${ORANGE}Running full analysis for queries $start_query to $end_query...${NC}"
                        start_time=$(date +%s)
                        
                        for ((q=start_query; q<=end_query; q++)); do
                            run_full_analysis $q
                        done
                        
                        end_time=$(date +%s)
                        duration=$((end_time - start_time))
                        hours=$((duration / 3600))
                        minutes=$(( (duration % 3600) / 60 ))
                        seconds=$((duration % 60))
                        
                        echo -e "\n${GREEN}=================================================${NC}"
                        echo -e "${GREEN}Range processed! Total time: ${hours}h ${minutes}m ${seconds}s${NC}"
                        echo -e "${GREEN}=================================================${NC}"
                    else
                        echo -e "${RED}Invalid range! Please use numbers between 1 and 22.${NC}"
                    fi
                    ;;
                    
                3)
                    echo -e "\n${ORANGE}Enter query numbers separated by space (e.g., 1 2 3):${NC}"
                    read -p "Query numbers: " -a query_numbers
                    
                    if [ ${#query_numbers[@]} -eq 0 ]; then
                        echo -e "${RED}No queries specified!${NC}"
                    else
                        start_time=$(date +%s)
                        valid_count=0
                        
                        for query_num in "${query_numbers[@]}"; do
                            if [ "$query_num" -ge 1 ] && [ "$query_num" -le 22 ]; then
                                run_full_analysis "$query_num"
                                valid_count=$((valid_count+1))
                            else
                                echo -e "${RED}Invalid query number: $query_num (skipping)${NC}"
                            fi
                        done
                        
                        end_time=$(date +%s)
                        duration=$((end_time - start_time))
                        hours=$((duration / 3600))
                        minutes=$(( (duration % 3600) / 60 ))
                        seconds=$((duration % 60))
                        
                        echo -e "\n${GREEN}==========================================${NC}"
                        echo -e "${GREEN}Processed $valid_count queries! Total time: ${hours}h ${minutes}m ${seconds}s${NC}"
                        echo -e "${GREEN}==========================================${NC}"
                    fi
                    ;;
                    
                0)
                    continue
                    ;;
                    
                *)
                    echo -e "${RED}Invalid option!${NC}"
                    ;;
            esac
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
