import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define queries and file paths
queries = [2, 5, 7, 8, 9]
base_path = "/home/blackparkd/github/risinglight/src/planner/outputs/rules_stats"
output_dir = "/home/blackparkd/github/risinglight/src/planner/outputs/graphs/rule_mostpop"
os.makedirs(output_dir, exist_ok=True)

# Processar cada query
for query in queries:
    # Define file path for current query
    file_path = f"{base_path}/q{query}_data/stage_3_rule_stats.csv"
    
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        continue
        
    # Ler o arquivo CSV
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        continue
    
    # Ordenar por número de aplicações (descendente) e pegar as top 5
    top_5_rules = data.sort_values('Total_Applications', ascending=False).head(5)
    
    # Configurar o estilo do gráfico
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Criar o gráfico de barras horizontal
    bars = sns.barplot(
        x='Total_Applications', 
        y='Rule_Name', 
        data=top_5_rules,
        palette='viridis'
    )
    
    # Adicionar rótulos nas barras com o número de aplicações
    for i, v in enumerate(top_5_rules['Total_Applications']):
        bars.text(v + 10, i, str(v), color='black', va='center')
    
    # Adicionar títulos e rótulos
    plt.xlabel('Number of Applications', fontsize=12)
    plt.ylabel('Rule Name', fontsize=12)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Salvar o gráfico
    output_file = f"{output_dir}/top_5_rules_stage3_q{query}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    print(f"Gráfico salvo em {output_file}")
    
    # Fechar a figura para evitar sobreposição nos próximos gráficos
    plt.close()

print("Processamento concluído.")