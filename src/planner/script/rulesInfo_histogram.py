#!/usr/bin/env python3
# filepath: /home/blackparkd/github/risinglight/src/planner/script/rulesInfo_histogram.py

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
import re

def load_all_rule_files(query_folder, stage=None):
    """
    Carrega todos os arquivos de regras para uma determinada consulta e estágio.
    Se stage for None, carrega todos os estágios.
    """
    base_dir = f"src/planner/outputs/rules_data/{query_folder}_data"
    pattern = f"stage_{stage if stage else '*'}_iter_*_rules_application.csv"
    all_files = glob.glob(os.path.join(base_dir, pattern))
    
    if not all_files:
        print(f"Nenhum arquivo encontrado para o padrão: {os.path.join(base_dir, pattern)}")
        return None
    
    # Ordena os arquivos para processá-los em ordem
    all_files.sort(key=lambda x: [int(n) if n.isdigit() else n for n in re.findall(r'\d+|[A-Za-z]+', x)])
    
    all_data = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            # Extrai informações do nome do arquivo
            match = re.search(r'stage_(\d+)_iter_(\d+)', file)
            if match:
                file_stage = match.group(1)
                file_iter = match.group(2)
                # Adiciona colunas para identificar o arquivo de origem, se não existirem
                if 'Stage' not in df.columns:
                    df['Stage'] = file_stage
                if 'External_Iteration' not in df.columns:
                    df['External_Iteration'] = file_iter
                
            all_data.append(df)
            print(f"Carregado: {file}")
        except Exception as e:
            print(f"Erro ao carregar {file}: {e}")
    
    if not all_data:
        return None
    
    # Concatena todos os DataFrames
    return pd.concat(all_data, ignore_index=True)

def create_rule_application_heatmap(df, query_folder, stage=None):
    """
    Cria um heatmap mostrando a aplicação de regras por iteração.
    """
    # Filtra apenas as linhas com regras aplicadas (não 'None')
    df_rules = df[df['Rule_Name'] != 'None'].copy()
    
    # Cria uma tabela pivot com iteração nas linhas, regras nas colunas, e aplicações nos valores
    pivot = df_rules.pivot_table(
        index=['External_Iteration', 'Internal_Iteration'],
        columns='Rule_Name',
        values='Applications',
        aggfunc='sum',
        fill_value=0
    )
    
    # Configura o gráfico
    plt.figure(figsize=(16, 10))
    ax = sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".0f", linewidths=.5)
    
    plt.title(f"Rule Applications Heatmap - Query {query_folder}, Stage {stage}", fontsize=16)
    plt.ylabel("Iteration (External, Internal)")
    plt.xlabel("Rule")
    plt.xticks(rotation=45, ha="right")
    
    # Salva o gráfico
    stage_str = f"stage{stage}" if stage else "all_stages"
    output_dir = f"src/planner/outputs/graphs/rules_stats/{query_folder}/{stage_str}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/rule_heatmap.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Heatmap saved as: {output_path}")

def create_growth_chart(df, query_folder, stage=None):
    """
    Cria um gráfico mostrando o crescimento de classes e nós ao longo das iterações.
    """
    # Agrupa por iteração e obtém o máximo de classes e nós
    growth_df = df.groupby(['External_Iteration', 'Internal_Iteration']).agg({
        'Class_Count': 'max', 
        'Node_Count': 'max',
        'Rule_Name': lambda x: ', '.join(set([r for r in x if r != 'None']))
    }).reset_index()
    
    # Calcula a taxa de crescimento
    growth_df['Node_per_Class'] = growth_df['Node_Count'] / growth_df['Class_Count']
    growth_df['Sequential_ID'] = range(len(growth_df))
    
    # Configura o gráfico
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Linha para classes e nós
    color = 'tab:blue'
    ax1.set_xlabel('Iteração')
    ax1.set_ylabel('Contagem', color=color)
    ax1.plot(growth_df['Sequential_ID'], growth_df['Class_Count'], color='tab:blue', marker='o', label='Classes')
    ax1.plot(growth_df['Sequential_ID'], growth_df['Node_Count'], color='tab:red', marker='s', label='Nós')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Linha secundária para a taxa nós/classe
    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Nós por Classe', color=color)
    ax2.plot(growth_df['Sequential_ID'], growth_df['Node_per_Class'], color=color, linestyle='--', marker='^', label='Nós/Classe')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Adiciona legendas e título
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.title(f"Crescimento do E-Graph - Query {query_folder}, Stage {stage}", fontsize=16)
    
    # Adiciona rótulos para iterações
    plt.xticks(growth_df['Sequential_ID'], [f"({row['External_Iteration']},{row['Internal_Iteration']})" 
                                           for _, row in growth_df.iterrows()], rotation=45)
    
    # Salva o gráfico
    stage_str = f"stage{stage}" if stage else "all_stages"
    output_dir = f"src/planner/outputs/{query_folder}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{query_folder}_{stage_str}_growth_chart.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Growth chart saved as: {output_path}")

def create_rule_frequency_chart(df, query_folder, stage=None):
    """
    Cria um gráfico de barras mostrando a frequência de aplicação de cada regra.
    """
    # Filtra apenas as linhas com regras aplicadas (não 'None')
    df_rules = df[df['Rule_Name'] != 'None'].copy()
    
    # Agrupa por regra e soma as aplicações
    rule_counts = df_rules.groupby('Rule_Name')['Applications'].sum().reset_index()
    rule_counts = rule_counts.sort_values('Applications', ascending=False)
    
    # Configura o gráfico
    plt.figure(figsize=(14, 8))
    bars = plt.bar(rule_counts['Rule_Name'], rule_counts['Applications'], color='skyblue')
    
    # Adiciona os valores em cima das barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f"{int(height)}",
                 ha='center', va='bottom')
    
    plt.title(f"Frequência de Aplicação de Regras - Query {query_folder}, Stage {stage}", fontsize=16)
    plt.xlabel('Regra')
    plt.ylabel('Número de Aplicações')
    plt.xticks(rotation=45, ha='right')
    
    # Salva o gráfico
    stage_str = f"stage{stage}" if stage else "all_stages"
    output_dir = f"src/planner/outputs/{query_folder}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{query_folder}_{stage_str}_rule_frequency.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Rule frequency chart saved as: {output_path}")

def analyze_rule_patterns(df, query_folder, stage=None):
    """
    Identifica padrões na aplicação de regras e cria uma visualização.
    """
    if df is None or len(df) == 0:
        return
    
    # Filtra apenas as linhas com regras aplicadas (não 'None')
    df_rules = df[df['Rule_Name'] != 'None'].copy()
    
    # Agrupa regras por iteração
    iter_rules = df_rules.groupby(['External_Iteration', 'Internal_Iteration'])['Rule_Name'].unique().apply(list)
    
    # Cria um grafo de co-ocorrência
    rule_pairs = defaultdict(int)
    for rules in iter_rules:
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                pair = tuple(sorted([rule1, rule2]))
                rule_pairs[pair] += 1
    
    # Converte para DataFrame
    pairs_df = pd.DataFrame([(r1, r2, count) for (r1, r2), count in rule_pairs.items()], 
                           columns=['Rule1', 'Rule2', 'Count'])
    pairs_df = pairs_df.sort_values('Count', ascending=False).head(20)  # Top 20 pares
    
    # Configura o gráfico
    plt.figure(figsize=(14, 10))
    plt.barh(pairs_df.apply(lambda x: f"{x['Rule1']} + {x['Rule2']}", axis=1), pairs_df['Count'], color='lightgreen')
    plt.title(f"Top Pares de Regras Co-ocorrentes - Query {query_folder}, Stage {stage}", fontsize=16)
    plt.xlabel('Número de Co-ocorrências')
    plt.ylabel('Par de Regras')
    
    # Salva o gráfico
    stage_str = f"stage{stage}" if stage else "all_stages"
    output_dir = f"src/planner/outputs/{query_folder}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{query_folder}_{stage_str}_rule_pairs.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Rule pairs chart saved as: {output_path}")

def analyze_query_rules(query_folder, stage=None):
    """
    Função principal para analisar regras para uma consulta e estágio.
    """
    print(f"\n🔍 Analisando regras para Query {query_folder}, Stage {stage if stage else 'todos'}...")
    
    # Carrega todos os arquivos de regras
    df = load_all_rule_files(query_folder, stage)
    
    if df is None:
        print(f"❌ Nenhum dado encontrado para Query {query_folder}, Stage {stage if stage else 'todos'}")
        return
    
    # Mostra estatísticas básicas
    total_rules = df[df['Rule_Name'] != 'None']['Applications'].sum()
    unique_rules = df[df['Rule_Name'] != 'None']['Rule_Name'].nunique()
    max_classes = df['Class_Count'].max()
    max_nodes = df['Node_Count'].max()
    
    print(f"\n📊 Estatísticas:")
    print(f"Total de aplicações de regras: {total_rules}")
    print(f"Regras únicas aplicadas: {unique_rules}")
    print(f"Máximo de classes: {max_classes}")
    print(f"Máximo de nós: {max_nodes}")
    print(f"Taxa nós/classe final: {max_nodes/max_classes:.2f}")
    
    # Cria os gráficos
    create_rule_frequency_chart(df, query_folder, stage)
    create_growth_chart(df, query_folder, stage)
    create_rule_application_heatmap(df, query_folder, stage)
    analyze_rule_patterns(df, query_folder, stage)
    
    print(f"\n✅ Análise completa para Query {query_folder}, Stage {stage if stage else 'todos'}")

def main():
    """
    Função principal que processa argumentos da linha de comando.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Analisa e visualiza dados de aplicação de regras')
    parser.add_argument('query', help='Pasta da consulta para analisar (ex: q1)')
    parser.add_argument('--stage', type=int, help='Estágio específico para analisar (se omitido, analisa todos)')
    
    args = parser.parse_args()
    analyze_query_rules(args.query, args.stage)

if __name__ == "__main__":
    main()