import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import csv

# Creates a histogram visualizing merge operations per stage for a specific query
def create_merge_histogram(query_folder):
    input_file = f"src/planner/outputs/egg-merges/{query_folder}_data/egg_merges.csv"
    
    output_dir = f"src/planner/outputs/graphs/egg-merges/{query_folder}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = list(reader)
        
        last_four = rows[-4:]
    
    stages = []
    merge_counts = []
    
    for row in last_four:
        stages.append(int(row[0]))
        merge_counts.append(int(row[1]))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    bar_colors = ['#4B0082', '#0072B2', '#009E73', '#D55E00']
    bars = plt.bar(stages, merge_counts, color=bar_colors, width=0.6)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', 
                color='black', fontweight='bold')
    
    plt.xlabel('Stage', color='black', fontsize=14)
    plt.ylabel('Number of Merge Operations', color='black', fontsize=14)
    
    plt.xticks([0, 1, 2, 3])
    plt.xlim(-0.5, 3.5)
    
    ax.grid(True, color='gray', alpha=0.3, linestyle='--')
    
    ax.tick_params(colors='black', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1)
             
    output_path = os.path.join(output_dir, f"{query_folder}_merge_counts.png")
    plt.savefig(output_path, 
                facecolor=fig.get_facecolor(), 
                edgecolor='none',
                bbox_inches='tight',
                dpi=300)
    
    plt.close()
    print(f"✅ Merge operations plot saved as: {output_path}")

# Main entry point - processes command line arguments and calls the histogram function
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