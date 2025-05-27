import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Base paths
base_path = "src/planner/outputs/rules_stats"
output_dir = "src/planner/outputs/bar_charts/rule_mostpop"
os.makedirs(output_dir, exist_ok=True)

def process_query(query):
    for stage in [2, 3]:  # Process stages 2 and 3
        file_path = f"{base_path}/{query}_data/stage_{stage}_rule_stats.csv"
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue

        try:
            # Read the CSV file
            data = pd.read_csv(file_path)

            # Sort by 'Total_Applications' and get the top 5 rules
            top_5_rules = data.sort_values('Total_Applications', ascending=False).head(5)

            fig_width = max(10, len(top_5_rules) * 2)  # Largura mínima de 10, ajustada pelo número de barras
            plt.figure(figsize=(fig_width, 6))
           
            # Create the plot with a fixed larger figure size
            sns.set_style("whitegrid")
            bars = sns.barplot(
                x='Total_Applications', 
                y='Rule_Name', 
                data=top_5_rules,
                palette=["#4B0082", "#FC8B00", "#009E73", "#94004FFF", "#0A9D9B"]
            )
            color=["#4B0082", "#FC8B00", "#009E73", "#94004FFF"],
            # Add labels to the bars
            for i, v in enumerate(top_5_rules['Total_Applications']):
                bars.text(v + (0.05 * max(top_5_rules['Total_Applications'])), i, str(v), color='black', va='center')

            # Configure plot labels and title
            plt.xlabel('Number of Applications', fontsize=12)
            plt.ylabel(None)  # Remove a label do eixo Y
            

            # Dynamically adjust the X-axis limits to ensure all numbers fit
            max_value = max(top_5_rules['Total_Applications'])
            plt.xlim(0, max_value * 1.2)  # Adicionar 20% de margem ao limite máximo

            # Save the plot
            output_file = f"{output_dir}/top_5_rules_stage{stage}_{query}.png"
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Plot saved: {output_file}")
            plt.close()

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

def process_all_queries():
    # Process all query folders in the base path
    for query_folder in os.listdir(base_path):
        if query_folder.startswith("q") and query_folder.endswith("_data"):
            query = query_folder.split("_")[0]  # Extract query name (e.g., "q1")
            print(f"🔍 Processing query: {query}")
            process_query(query)

def main():
    process_all_queries()

if __name__ == "__main__":
    main()