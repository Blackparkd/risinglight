import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import csv

def create_merge_histogram(query_folder):
    """
    Create histogram showing merge operations per stage for a specific query.
    """
    # Construct input file path
    input_file = f"src/planner/outputs/egg-merges/{query_folder}_data/egg_merges.csv"
    
    # Create output directory if it doesn't exist
    output_dir = f"src/planner/outputs/graphs/egg-merges/{query_folder}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Verify if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    # Read all CSV lines
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Store header
        rows = list(reader)    # Convert rest of file to list
        
        # Get last 4 rows
        last_four = rows[-4:]
    
    # Extract data for plotting
    stages = []
    merge_counts = []
    
    for row in last_four:
        stages.append(int(row[0]))  # First column is Stage
        merge_counts.append(int(row[1]))  # Second column is Merge_Count
    
    # Create figure with custom styling
    fig, ax = plt.subplots(figsize=(12, 6), layout='constrained')
    fig.patch.set_facecolor('#478ac9')
    ax.set_facecolor('#2e353b')
    
    # Plot histogram-style bars
    bars = plt.bar(stages, merge_counts, color='#FF8C00', edgecolor='white', width=0.7)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', 
                color='white', fontweight='bold')
    
    # Configure labels and title
    plt.xlabel('Stage', color='white', fontsize=14)
    plt.ylabel('Number of Merge Operations', color='white', fontsize=14)
    plt.title(f'Egg Merge Operations by Stage - Query {query_folder}',
             color='white', pad=20, fontsize=16)
    
    # Set x-axis to show only stages 0-3
    plt.xticks([0, 1, 2, 3])
    plt.xlim(-0.5, 3.5)
    
    # Add grid for better readability
    ax.grid(True, color='white', alpha=0.2, linestyle='--')
    
    # Style the axes
    ax.tick_params(colors='white', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(2)

             
    # Save the plot
    output_path = os.path.join(output_dir, f"{query_folder}_merge_counts.png")
    plt.savefig(output_path, 
                facecolor=fig.get_facecolor(), 
                edgecolor='none',
                bbox_inches='tight',
                dpi=300)
    
    plt.close()
    print(f"✅ Merge operations plot saved as: {output_path}")

def main():
    if len(sys.argv) <= 1:
        print("❌ Usage: python3 egg-merges.py <query_number>")
        print("Example: python3 egg-merges.py 1")
        return
        
    query_number = sys.argv[1].strip()
    query_folder = f"q{query_number}"

    create_merge_histogram(query_folder)

if __name__ == "__main__":
    main()