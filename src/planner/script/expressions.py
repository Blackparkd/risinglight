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
            print(f"Colunas necessárias não encontradas em {csv_file}")
            return

        # Ordenar por Stage para garantir ordem correta no gráfico
        df = df.sort_values('Stage')
        stages = df['Stage'].astype(str)
        classes = df['Classes_Total']

        plt.figure(figsize=(8, 6))
        plt.bar(stages, classes, color='skyblue', edgecolor='black')
        plt.xlabel('Stage')
        plt.ylabel('Expression Groups')
        for i, v in enumerate(classes):
            plt.text(i, v + max(classes)*0.01, str(v), ha='center', va='bottom', fontsize=10)
        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{query_name}_expression_groups.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Gráfico salvo em {output_path}")

    except Exception as e:
        print(f"Erro ao processar {csv_file}: {e}")

def main():
    base_dir = os.path.join("src", "planner", "outputs", "filtered_query_data")
    output_dir = os.path.join("src", "planner", "outputs", "graphs", "expression_groups")
    queries = ['q2', 'q5', 'q7', 'q8', 'q9']

    for query in queries:
        csv_file = os.path.join(base_dir, f"{query}_data_filtered.csv")
        if os.path.exists(csv_file):
            plot_expression_groups(csv_file, output_dir)
        else:
            print(f"Arquivo não encontrado: {csv_file}")

if __name__ == "__main__":
    main()