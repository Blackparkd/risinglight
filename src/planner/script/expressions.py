#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')

def plot_expression_groups(csv_file, output_dir):
    query_name = os.path.basename(csv_file).split('_')[0]
    try:
        df = pd.read_csv(csv_file)
        if 'Stage' not in df.columns or 'Classes_Total' not in df.columns:
            print(f"❌ Required columns not found in {csv_file}")
            return

        # Sort by Stage to ensure correct order in the plot
        df = df.sort_values('Stage')
        stages = df['Stage'].astype(str)
        classes = df['Classes_Total']

        # Customize color scheme and add black border
        plt.figure(figsize=(8, 6))
        bars = plt.bar(
            stages,
            classes,
            color=["#4B0082", "#FC8B00", "#009E73", "#94004FFF"],
            edgecolor='black',
            linewidth=1.2
        )
        plt.xlabel('Stage', fontsize=12)
        plt.ylabel('Expression Groups', fontsize=12)

        # Add values on top of the bars
        for i, v in enumerate(classes):
            plt.text(i, v + max(classes) * 0.01, str(v), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{query_name}_expression_groups.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"✅ Plot saved at {output_path}")

    except Exception as e:
        print(f"❌ Error processing {csv_file}: {e}")

def main():
    base_dir = os.path.join("src", "planner", "outputs", "filtered_query_data")
    output_dir = os.path.join("src", "planner", "outputs", "graphs", "expression_groups")

    if not os.path.exists(base_dir):
        print(f"❌ Base directory not found: {base_dir}")
        return

    # Process all query files in the directory
    for file_name in os.listdir(base_dir):
        if file_name.endswith("_data_filtered.csv"):
            csv_file = os.path.join(base_dir, file_name)
            print(f"🔍 Processing file: {csv_file}")
            plot_expression_groups(csv_file, output_dir)
        else:
            print(f"⚠️ Skipping non-matching file: {file_name}")

if __name__ == "__main__":
    main()