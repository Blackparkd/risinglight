#!/bin/bash

# Colors for output
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to run all steps for all queries
run_all_steps() {
    echo -e "\n${ORANGE}Running all steps for all queries...${NC}"
    start_time=$(date +%s)

    # Execute all steps for all queries
    echo -e "\n${ORANGE}Executing queries...${NC}"
    for query_num in {1..22}; do
        echo -e "${BLUE}Executing Query ${query_num}...${NC}"
        cargo run --release -- -f tests/mytests/q${query_num}.sql
    done

    echo -e "\n${ORANGE}Extracting data...${NC}"
    python3 src/planner/script/extractor.py

    echo -e "\n${ORANGE}Generating histograms...${NC}"
    python3 src/planner/script/graphics.py

    echo -e "\n${ORANGE}Extracting class data...${NC}"
    python3 src/planner/script/classes_data_extractor.py

    echo -e "\n${ORANGE}Generating class histograms for all stages...${NC}"
    python3 src/planner/script/classes_histogram.py

    echo -e "\n${ORANGE}Generating Egg Merge histograms...${NC}"
    python3 src/planner/script/egg-merges.py

    echo -e "\n${ORANGE}Generating most popular rules graphs...${NC}"
    python3 src/planner/script/rule_mostpop.py

    echo -e "\n${ORANGE}Generating rule application heatmaps...${NC}"
    python3 src/planner/script/rulesInfo_histogram.py

    echo -e "\n${ORANGE}Generating global query cost reduction graphs...${NC}"
    python3 src/planner/script/global_query.py

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    hours=$((duration / 3600))
    minutes=$(( (duration % 3600) / 60 ))
    seconds=$((duration % 60))

    echo -e "\n${GREEN}==============================================${NC}"
    echo -e "${GREEN}All queries processed! Total time: ${hours}h ${minutes}m ${seconds}s${NC}"
    echo -e "${GREEN}==============================================${NC}"
}

# Function to execute a single query in the optimizer
run_single_query() {
    read -p "Enter the query number (e.g., 1 for q1): " query_num
    if [[ ! $query_num =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Invalid query number!${NC}"
        return
    fi

    query_file="tests/mytests/q${query_num}.sql"
    if [[ ! -f $query_file ]]; then
        echo -e "${RED}Query file not found: ${query_file}${NC}"
        return
    fi

    echo -e "\n${BLUE}Executing Query ${query_num}...${NC}"
    cargo run --release -- -f "$query_file"
}

# Function to execute all queries in the optimizer (only)
run_optimizer_only() {
    echo -e "\n${ORANGE}Executing all queries${NC}"
    start_time=$(date +%s)

    for query_num in {1..22}; do
        echo -e "${BLUE}Executing Query ${query_num}...${NC}"
        cargo run --release -- -f tests/mytests/q${query_num}.sql
    done

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    hours=$((duration / 3600))
    minutes=$(( (duration % 3600) / 60 ))
    seconds=$((duration % 60))

    echo -e "\n${GREEN}==============================================${NC}"
    echo -e "${GREEN}All queries executed in the optimizer! Total time: ${hours}h ${minutes}m ${seconds}s${NC}"
    echo -e "${GREEN}==============================================${NC}"
}

# Main menu
while true; do
    clear
    echo -e "${BLUE}RisingLight Query Analyzer =======================${NC}"
    echo -e "${ORANGE}1.${NC} Execute + Histograms: Query 1-22 "
    echo -e "${ORANGE}2.${NC} Execute a single query"
    echo -e "${ORANGE}3.${NC} Execute all queries"
    echo -e "${ORANGE}0.${NC} Exit"
    echo -e "${BLUE}================================================== ${NC}"

    read -p "Choose an option: " option

    case $option in
        1)
            run_all_steps
            ;;
        2)
            run_single_query
            ;;
        3)
            run_optimizer_only
            ;;
        0)
            echo -e "\n${ORANGE}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option!${NC}"
            ;;
    esac

    echo -e "\nPress ENTER to continue"
    read
done
