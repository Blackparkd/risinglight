import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import re
from collections import Counter

# utilizar plt.hist para fazer histograma
# ver tipos de nós mais populares -> apenas para nós relacionais - já se tem a informação no csv


def create_histogram(query_folder, stage):
    # Construct input file path
    input_file = f"src/planner/outputs/filtered_class_data/query_{query_folder}/stage{stage}_filtered.csv"

    # Create output directory if it doesn't exist
    output_dir = "src/planner/outputs/graphs/node_distribution"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Verify if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    # Lists to store values
    class_ids = []
    node_counts = []

    # Read CSV and store values
    with open(input_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            class_ids.append(int(row["Class_ID"]))
            node_counts.append(int(row["Node_Count"]))

    # Print some statistics
    # plt.hist(node_counts, len(class_ids)) # 
    # plt.show()

    node_distribution = Counter(node_counts)
    min_nodos = min(node_counts)
    max_nodos = max(node_counts)

    ##########################################
    # BAR PLOT START - Node Distribution
    ##########################################
    
    # Create histogram
    fig, ax = plt.subplots(figsize=(12, 6), layout='constrained')

    # Add background color
    fig.patch.set_facecolor('#478ac9')
    ax.set_facecolor('#2e353b')

    # Create bar plot
    ax.bar(node_distribution.keys(), node_distribution.values(), 
        color='#FF8C00', edgecolor='white')

    # Add value labels on bars
    for x, y in node_distribution.items():
        ax.text(x, y, str(y), ha='center', va='bottom', color='white')

    # Configure labels and title
    ax.set_xlabel('Nodes per class', color='white')
    ax.set_ylabel('Classes', color='white')
    ax.set_title(f'Node distribution - Query {query_folder}, Stage {stage}',
                color='white', pad=20)

    # Style the axes
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    # Add statistics text
    stats_text = (f'Total Classes: {len(class_ids)}\n'
                 f'Min Nodes: {min(node_counts)}\n'
                 f'Max Nodes: {max(node_counts)}\n'
                 f'Avg Nodes: {np.mean(node_counts):.2f}')
    
    plt.text(0.95, 0.95, stats_text,
             transform=ax.transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(facecolor='#2e353b', edgecolor='#478ac9'),
             color='white')

    ##########################################
    # BAR PLOT END
    ##########################################

    # Save the plot
    query_output_dir = os.path.join(output_dir, query_folder)
    if not os.path.exists(query_output_dir):
        os.makedirs(query_output_dir)
    
    output_path = os.path.join(query_output_dir, f"{query_folder}_stage{stage}_histogram.png")

    plt.savefig(output_path, 
                facecolor=fig.get_facecolor(), 
                edgecolor='none',
                bbox_inches='tight',
                dpi=300)
    
    plt.close()
    print(f"✅ Plot saved as: {output_path}")
    

##########################################
# RELATIONAL FLAGS PLOT START #
##########################################

# Gathering data #

def create_relational_histogram(query_folder, stage):
    """Create histogram of relational operations"""
    # Construct input file path for original classes data with Nodes column
    input_file = f"src/planner/outputs/data_classes/{query_folder}/stage_{stage}_classes.csv"
    
    # Create output directory
    output_dir = "src/planner/outputs/graphs/relational_ops"
    query_output_dir = os.path.join(output_dir, query_folder)
    if not os.path.exists(query_output_dir):
        os.makedirs(query_output_dir)
    
    # Verify if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
        
    # Extract operation types from Nodes column
    node_types = []
    with open(input_file, 'r') as file:
        # Skip the first line if it contains a comment
        first_line = file.readline()
        if '//' in first_line:
            # File has comment line, reset to beginning and skip it
            file.seek(0)
            next(file)
        else:
            # No comment, reset to beginning
            file.seek(0)
            
        # Read CSV data
        reader = csv.DictReader(file)
        for row in reader:
            if 'Nodes' in row:  # Make sure Nodes column exists
                node_text = row['Nodes']
                # Extract the operator name (before parentheses or brackets)
                match = re.match(r'^([A-Za-z]+)', node_text)
                if match:
                    node_types.append(match.group(1))
    
    # Define relational operations to focus on
    relational_ops = [
        "Join", "Filter", "Proj", "HashAgg", "Order", "Scan",
        "HashJoin", "IndexScan", "SeqScan", "MergeJoin",
        "Values", "TopN",
    ]
    
    # Count occurrences of each node type
    all_counts = Counter(node_types)
    
    # Filter to only include relational operations
    rel_counts = {op: all_counts[op] for op in all_counts if op in relational_ops}
    sorted_items = sorted(rel_counts.items(), key=lambda x: x[1], reverse=True)
    
    if not sorted_items:
        print(f"⚠️ No relational operations found in {input_file}")
        return
    
    # Prepare data for plotting
    operators = [item[0] for item in sorted_items]
    frequencies = [item[1] for item in sorted_items]
    

    ### Create the histogram ###
    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor('#478ac9')
    ax.set_facecolor('#2e353b')
    
    # Plot the bars
    bars = ax.bar(operators, frequencies, color='#FF8C00', edgecolor='white', alpha=0.7)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', color='white')
    
    # Configure plot
    ax.set_xlabel('Relational Operators', color='white', fontsize=14)
    ax.set_ylabel('Frequency', color='white', fontsize=14)
    ax.set_title(f'Popular Relational Operators\n{query_folder}, Stage {stage}',
                 color='white', fontsize=16, pad=20)
    
    # Add styling
    ax.tick_params(colors='white', labelsize=12)
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, color='white', alpha=0.2, linestyle='--')
    
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(2)
    
    # Add statistics
    stats_text = (f'Total Operators: {sum(frequencies)}\n'
                 f'Unique Operators: {len(operators)}\n'
                 f'Most Common: {operators[0]} ({frequencies[0]} occurrences)')
    
    plt.text(0.95, 0.95, stats_text,
             transform=ax.transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(facecolor='#2e353b', edgecolor='#478ac9'),
             color='white',
             fontsize=12)
    
    # Save plot
    output_file = os.path.join(query_output_dir, f"{query_folder}_stage{stage}_relational_ops.png")
    plt.tight_layout()
    plt.savefig(output_file, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', dpi=300)
    plt.close()
    print(f"✅ Relational operators histogram saved as: {output_file}")





## MAIN ##
def main():
    if len(sys.argv) <= 2:
        print("❌ Usage: python3 class_histogram.py <query_folder> <stage>")
        print("Example: python3 class_histogram.py q1 3")
        return
        
    query_folder = sys.argv[1].strip()
    stage = sys.argv[2].strip()

    create_histogram(query_folder, stage)
    create_relational_histogram(query_folder, stage)

if __name__ == "__main__":
    main()