import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import os


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
    # Create query-specific directory
    query_output_dir = os.path.join(output_dir, query_folder)
    if not os.path.exists(query_output_dir):
        os.makedirs(query_output_dir)
    
    
    # Show the plot
    # plt.show() -> Para já so quero guardar a imagem

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(15, 8), layout='constrained')
    fig.patch.set_facecolor('#478ac9')
    ax.set_facecolor('#2e353b')

    # Create scatter plot with connected lines
    ax.plot(class_ids, node_counts, 
            color='white', 
            alpha=0.3, 
            linestyle='-', 
            linewidth=0.5)
    ax.scatter(class_ids, node_counts,
              color='white',
              alpha=0.7,
              s=50)  # size of points

    # Improve x-axis readability
    if len(class_ids) > 50:
        plt.xticks(rotation=45)
        # Show fewer x-axis labels when there are many points
        ax.xaxis.set_major_locator(plt.MaxNLocator(20))

    # Add grid for better readability
    ax.grid(True, color='white', alpha=0.1)

    # Configure plot
    ax.set_xlabel('Class ID', color='white')
    ax.set_ylabel('Number of Nodes', color='white')
    ax.set_title(f'Distribution of Nodes per Class\nQuery {query_folder}, Stage {stage}',
                 color='white', pad=20)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    # Save plot
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