import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define queries and file paths
queries = [2, 5, 6, 7, 8, 9]
base_path = "/home/blackparkd/github/risinglight/src/planner/outputs/rules_stats"
output_dir = "/home/blackparkd/github/risinglight/src/planner/outputs/graphs/rule_mostpop"
os.makedirs(output_dir, exist_ok=True)

# Processar cada query
for query in queries:
    # Processar stage 2 para query 6
    if query == 6:
        file_path = f"{base_path}/q{query}_data/stage_2_rule_stats.csv"
        if os.path.exists(file_path):
            try:
                data = pd.read_csv(file_path)
                top_5_rules = data.sort_values('Total_Applications', ascending=False).head(5)
                plt.figure(figsize=(10, 6))
                sns.set_style("whitegrid")
                bars = sns.barplot(
                    x='Total_Applications', 
                    y='Rule_Name', 
                    data=top_5_rules,
                    palette='viridis'
                )
                for i, v in enumerate(top_5_rules['Total_Applications']):
                    bars.text(v + 10, i, str(v), color='black', va='center')
                plt.xlabel('Number of Applications', fontsize=12)
                plt.ylabel('Rule Name', fontsize=12)
                plt.tight_layout()
                output_file = f"{output_dir}/top_5_rules_stage2_q{query}.png"
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                print(f"Gráfico salvo em {output_file}")
                plt.close()
            except Exception as e:
                print(f"Erro ao processar stage 2 para query {query}: {e}")
        else:
            print(f"Arquivo não encontrado para stage 2: {file_path}")

    # Processar stage 3 para todas as queries, incluindo query 6
    file_path = f"{base_path}/q{query}_data/stage_3_rule_stats.csv"
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path)
            top_5_rules = data.sort_values('Total_Applications', ascending=False).head(5)
            plt.figure(figsize=(10, 6))
            sns.set_style("whitegrid")
            bars = sns.barplot(
                x='Total_Applications', 
                y='Rule_Name', 
                data=top_5_rules,
                palette='viridis'
            )
            for i, v in enumerate(top_5_rules['Total_Applications']):
                bars.text(v + 10, i, str(v), color='black', va='center')
            plt.xlabel('Number of Applications', fontsize=12)
            plt.ylabel('Rule Name', fontsize=12)
            plt.tight_layout()
            output_file = f"{output_dir}/top_5_rules_stage3_q{query}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Gráfico salvo em {output_file}")
            plt.close()
        except Exception as e:
            print(f"Erro ao processar stage 3 para query {query}: {e}")
    else:
        print(f"Arquivo não encontrado para stage 3: {file_path}")

print("Processamento concluído.")