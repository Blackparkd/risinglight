import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
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
    

## MAIN ##
def main():
    if len(sys.argv) <= 2:
        print("❌ Usage: python3 class_histogram.py <query_folder> <stage>")
        print("Example: python3 class_histogram.py q1 3")
        return
        
    query_folder = sys.argv[1].strip()
    stage = sys.argv[2].strip()
    create_histogram(query_folder, stage)

if __name__ == "__main__":
    main()