import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def create_histogram(query_folder, stage):
    # Construct input file path
    input_file = f"src/planner/outputs/data_classes/{query_folder}/stage_{stage}_classes.csv"
    
    # Create output directory if it doesn't exist
    output_dir = "src/planner/outputs/graphs/histograms"
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

    # Create histogram
    fig, ax = plt.subplots(figsize=(12, 6), layout='constrained')

    # Add background color
    fig.patch.set_facecolor('#478ac9')  # Graph background color
    ax.set_facecolor('#2e353b')  # Subplot background color

    # Create histogram bars
    n_bins = min(20, len(set(node_counts)))  # Adjust number of bins based on data
    counts, bins, patches = ax.hist(node_counts, bins=n_bins, 
                                  color='#FF8C00', edgecolor='white')
    
    # Add value labels on top of each bar
    for count, patch in zip(counts, patches):
        if count > 0:  # Only show labels for non-empty bins
            ax.text(patch.get_x() + patch.get_width()/2., count,
                   int(count), ha='center', va='bottom', color='white')

    # Configure labels and title
    ax.set_xlabel('Number of Nodes per Class', color='white')
    ax.set_ylabel('Number of Classes', color='white')
    ax.set_title(f'Distribution of Nodes per Class - Query {query_folder}, Stage {stage}',
                 color='white', pad=20)

    # Style the axes
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    # Add some statistics as text
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

    # Save the plot as PNG file
    output_path = os.path.join(output_dir, f"query{query_folder}_stage{stage}_histogram.png")
    plt.savefig(output_path, 
                bbox_inches='tight',
                facecolor=fig.get_facecolor(),
                edgecolor='none',
                dpi=300)
    print(f"✅ Histogram saved as: {output_path}")
    
    # Show the plot
    plt.show()

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