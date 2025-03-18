import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def create_graph(file_path):
    # Get query number from file path
    query_num = os.path.basename(file_path).split('_')[0][1:]
    
    # Create output directory if it doesn't exist
    output_dir = "src/planner/outputs/graphs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Verify if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # 📌 Lists to store values
    stages = []
    costs = []
    total_classes = []
    relationals = []
    minimums = []
    maximums = []
    averages = []

    # 📌 Read CSV and store values
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            stages.append(int(row["Stage"]))
            costs.append(float(row["Custo"]))
            total_classes.append(int(row["Classes_Total"]))
            relationals.append(int(row["Relacionais"]))
            minimums.append(int(row["Min"]))
            maximums.append(int(row["Max"]))
            averages.append(float(row["Media"]))

    # Create grouped bar chart
    stages = (0, 1, 2, 3)  # your stages
    metrics = {
        'Cost': costs,
        'Expression Groups': total_classes,
        'Relational Operators': relationals,
        'Minimum Expressions': minimums,
        'Maximum Expressions': maximums,
        'Average Expressions': averages
    }

    x = np.arange(len(stages))  # label positions
    width = 0.15 # width of the bars
    multiplier = 0 # multiplier to adjust bar position

    # Configure subplot
    fig, ax = plt.subplots(figsize=(15, 8), layout='constrained')

    # Add background color
    fig.patch.set_facecolor('#478ac9')  # Graph background color
    ax.set_facecolor('#2e353b')  # Subplot background color

    # Create bars for each metric
    colors = ['#FF8C00', '#72266D', '#FF4500', '#D3D3D3', '#9370DB', '#20B2AA']
    for (attribute, measurement), color in zip(metrics.items(), colors):
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=3, rotation=0, color='white', fontsize=8)
        multiplier += 1

    # Configure labels and title
    ax.set_ylabel('Values')
    ax.set_xlabel('Optimization Stages')
    ax.set_title('Metrics')
    ax.set_xticks(x + width, stages)
    ax.legend(
        loc='upper center', 
        bbox_to_anchor=(0.5, 1.15), 
        ncol=3,
        facecolor='#2e353b',
        edgecolor='#478ac9',
        labelcolor='white'
    )

    # Adjust logarithmic scale for Y axis due to cost values
    ax.set_yscale('log')

    # Adjust layout and increase space for labels
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)

    # Save the plot as PNG file
    output_path = os.path.join(output_dir, f"query{query_num}_graph.png")
    plt.savefig(output_path, 
                bbox_inches='tight',
                facecolor=fig.get_facecolor(),
                edgecolor='none',
                dpi=300)
    print(f"✅ Graph saved as: {output_path}")
    
    # Show the plot
    #plt.show() -> Para já so quero guardar a imagem

def main():
    if len(sys.argv) <= 1:
        print("❌ No file path provided")
        return
        
    file_path = sys.argv[1].strip()
    create_graph(file_path)

if __name__ == "__main__":
    main()
