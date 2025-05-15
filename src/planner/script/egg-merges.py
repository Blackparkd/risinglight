import os
import csv
import matplotlib.pyplot as plt
import numpy as np

# Creates a histogram visualizing merge operations per stage for a specific query
def create_merge_histogram(query_folder):
    # Remove "_data" from the folder name for output
    output_folder = query_folder.replace("_data", "")
    input_file = f"src/planner/outputs/egg-merges/{query_folder}/egg_merges.csv"
    output_dir = f"src/planner/outputs/graphs/egg-merges/{output_folder}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # Read the header
        if not header or len(header) < 4:
            print(f"⚠️ Invalid or empty file: {input_file}")
            return

        rows = list(reader)
        if len(rows) < 4:
            print(f"⚠️ Not enough data in file: {input_file}")
            return

        last_four = rows[-4:]

    stages = []
    merge_counts = []
    num_classes = []
    unique_nodes = []

    for row in last_four:
        if len(row) < 4:
            print(f"⚠️ Skipping malformed row: {row}")
            continue
        stages.append(int(row[0]))
        merge_counts.append(int(row[1]))
        unique_nodes.append(int(row[2]))      # hc size
        num_classes.append(int(row[3]))       # eclasses

    x = np.arange(len(stages))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    bars1 = ax.bar(x - width, merge_counts, width, label='Number of Merge Operations', color='#4B0082')
    bars2 = ax.bar(x, num_classes, width, label='Equivalence Classes', color="#FC8B00")
    bars3 = ax.bar(x + width, unique_nodes, width, label='Unique Nodes', color='#009E73')

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom',
                    color='black', fontweight='bold', fontsize=10)

    plt.xlabel('Stage', color='black', fontsize=14)
    plt.ylabel('Size', color='black', fontsize=14)
    plt.xticks(x, stages)
    plt.xlim(-0.5, len(stages) - 0.5)

    ax.grid(True, color='gray', alpha=0.3, linestyle='--')
    ax.tick_params(colors='black', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1)

    plt.legend(fontsize=13)
    output_path = os.path.join(output_dir, f"{output_folder}_sizes.png")
    plt.savefig(output_path,
                facecolor=fig.get_facecolor(),
                edgecolor='none',
                bbox_inches='tight',
                dpi=300)
    plt.close()
    print(f"✅ Size comparison plot saved as: {output_path}")


# Process all queries in the directory
def process_all_queries():
    input_dir = "src/planner/outputs/egg-merges"
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return

    for query_folder in os.listdir(input_dir):
        if query_folder.startswith("q"):
            print(f"🔍 Processing egg merges for query {query_folder}...")
            create_merge_histogram(query_folder)


# Main entry point
def main():
    process_all_queries()


if __name__ == "__main__":
    main()