#!/usr/bin/env python3
# filepath: /home/blackparkd/github/risinglight/src/planner/script/calculate_cost_reductions.py

import os
import glob
import pandas as pd
import re
import math
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def calculate_cost_differences():
    """
    Calcula a diferença de custos entre o estágio inicial e final para todas as queries.
    """
    print("\n🔍 Calculando a redução de custos para todas as queries...\n")
    
    # Passo 1: Carregar os custos iniciais (estágio 1)
    initial_costs = {}
    stage2_costs = {}  # Adicionado para armazenar custos do estágio 2
    initial_cost_dir = "src/planner/outputs/filtered_query_data/"
    all_data_files = glob.glob(os.path.join(initial_cost_dir, "q*_data_filtered.csv"))
    
    print("Carregando custos iniciais:")
    for file in all_data_files:
        try:
            # Extrair o número da query do nome do arquivo
            query_match = re.search(r'q(\d+)_', os.path.basename(file))
            if not query_match:
                continue
                
            query_num = int(query_match.group(1))
            query_name = f"Q{query_num}"
            
            # Ler o arquivo CSV
            df = pd.read_csv(file)
            
            # Filtrar para os estágios 1 e 2
            stage1_data = df[df['Stage'] == 1]
            stage2_data = df[df['Stage'] == 2]  # Adicionado para estágio 2
            
            # Processar estágio 1
            if len(stage1_data) > 0:
                initial_cost = pd.to_numeric(stage1_data['Custo'].iloc[0], errors='coerce')
                
                if initial_cost > 1e30:
                    print(f"  {query_name}: Valor de custo inicial muito alto ({initial_cost}), tratando como indisponível")
                    continue
                
                initial_cost = 0.0 if pd.isna(initial_cost) else initial_cost
                initial_costs[query_num] = initial_cost
                print(f"  {query_name}: Custo estágio 1 = {initial_cost:.2f}")
            
            # Processar estágio 2 (adicionado)
            if len(stage2_data) > 0:
                stage2_cost = pd.to_numeric(stage2_data['Custo'].iloc[0], errors='coerce')
                
                if stage2_cost > 1e30:
                    print(f"  {query_name}: Valor de custo estágio 2 muito alto ({stage2_cost}), tratando como indisponível")
                    continue
                
                stage2_cost = 0.0 if pd.isna(stage2_cost) else stage2_cost
                stage2_costs[query_num] = stage2_cost
                print(f"  {query_name}: Custo estágio 2 = {stage2_cost:.2f}")
        
        except Exception as e:
            print(f"  Erro ao processar custo inicial em {file}: {e}")
    
    # Passo 2: Carregar os custos finais (do último estágio)
    final_costs = {}
    final_cost_dir = "src/planner/outputs/total_costs/"
    total_cost_files = glob.glob(os.path.join(final_cost_dir, "q*_total_cost.csv"))
    
    print("\nCarregando custos finais:")
    for file in total_cost_files:
        try:
            # Extrair o número da query do nome do arquivo
            query_match = re.search(r'q(\d+)_', os.path.basename(file))
            if not query_match:
                continue
                
            query_num = int(query_match.group(1))
            query_name = f"Q{query_num}"
            
            # Ler o arquivo CSV
            df = pd.read_csv(file)
            
            # Verificar as colunas disponíveis
            print(f"  Arquivo {os.path.basename(file)} tem colunas: {', '.join(df.columns)}")
            
            if len(df) > 0:
                if 'Stage_3_Cost' in df.columns:
                    final_cost = pd.to_numeric(df['Stage_3_Cost'].iloc[0], errors='coerce')
                    if not pd.isna(final_cost):
                        final_costs[query_num] = final_cost
                        print(f"  {query_name}: Custo final = {final_cost:.2f} (da coluna Stage_3_Cost)")
                        continue
                
            
                # Se chegamos aqui, não conseguimos encontrar o custo final
                print(f"  {query_name}: Não foi possível determinar o custo final")
        
        except Exception as e:
            print(f"  Erro ao processar custo final em {file}: {e}")
            import traceback
            traceback.print_exc()
    
    # Passo 3: Calcular as diferenças de custo
    print("\nCalculando diferenças de custo:")
    
    # Lista para armazenar os resultados
    cost_differences = []
    
    # Obter todos os números de query únicos (de ambos os dicionários)
    all_query_nums = sorted(set(list(initial_costs.keys()) + list(final_costs.keys())))
    
    for query_num in all_query_nums:
        query_name = f"Q{query_num}"
        
        # Obter os custos, se disponíveis
        initial = initial_costs.get(query_num, None)
        stage2 = stage2_costs.get(query_num, None)  # Adicionado
        final = final_costs.get(query_num, None)
        
        # Calcular diferença apenas se inicial e final estiverem disponíveis
        if initial is not None and final is not None:
            difference = initial - final
            percent_reduction = (difference / initial * 100) if initial > 0 else 0
            
            # Determinar a magnitude do custo final
            if final > 0:
                magnitude = int(math.log10(final))
            else:
                magnitude = 0
                
            result = {
                'query_num': query_num,
                'query_name': query_name,
                'initial_cost': initial,
                'stage2_cost': stage2,  # Adicionado
                'final_cost': final,
                'absolute_reduction': difference,
                'percent_reduction': percent_reduction,
                'magnitude': magnitude
            }
            
            cost_differences.append(result)
            
            print(f"  {query_name}: {initial:.2f} → {final:.2f} = {difference:.2f} ({percent_reduction:.2f}%)")
        else:
            if initial is None:
                print(f"  {query_name}: Custo inicial indisponível")
            if final is None:
                print(f"  {query_name}: Custo final indisponível")
    
    return cost_differences

def plot_cost_reduction(cost_differences):
    """
    Gera um gráfico de redução de custo para todas as queries e uma tabela separada 
    com informações detalhadas.
    """
    if not cost_differences:
        print("⚠️ Nenhum dado de redução de custo disponível para gerar o gráfico.")
        return
    
    # Criar o diretório de saída se não existir
    output_dir = "src/planner/outputs/graphs/cost_reduction"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n📊 Gerando gráfico de redução de custo para todas as queries...")
    
    # Extrair dados para o gráfico, ordenados por número da query
    sorted_data = sorted(cost_differences, key=lambda x: x['query_num'])
    
    query_names = [item['query_name'] for item in sorted_data]
    initial_costs = [item['initial_cost'] for item in sorted_data]
    stage2_costs = [item.get('stage2_cost', None) for item in sorted_data]  # Adicionado, com fallback para None
    final_costs = [item['final_cost'] for item in sorted_data]
    reductions = [item['absolute_reduction'] for item in sorted_data]
    percentages = [item['percent_reduction'] for item in sorted_data]
    
    # PARTE 1: GRÁFICO DE BARRAS
    # =========================
    
    # Configurar o gráfico
    fig, ax = plt.subplots(figsize=(15, 8))  # Aumentei ligeiramente a largura
    
    # Posições das barras
    x = np.arange(len(query_names))
    bar_width = 0.25  # Reduzido para acomodar 3 barras
    
    # Criar barras para Stage 1
    p1 = ax.bar(x - bar_width, initial_costs, bar_width, label='Stage 1', color='#0072B2', alpha=0.8)
    
    # Criar barras para Stage 2
    # Converter None para 0 para evitar erros ao plotar
    stage2_values = [0 if v is None else v for v in stage2_costs]
    p2 = ax.bar(x, stage2_values, bar_width, label='Stage 2', color='#D55E00', alpha=0.8)
    
    # Criar barras para Final Stage
    p3 = ax.bar(x + bar_width, final_costs, bar_width, label='Final Stage', color='#009E73', alpha=0.8)
    
    # Adicionar valores nas barras (somente se não forem muito pequenos)
    max_cost = max(max(initial_costs), max(stage2_values), max(final_costs))
    
    # Configurar eixos e legendas
    ax.set_title('Cost Reduction by Query', fontsize=16)
    ax.set_xlabel('Query', fontsize=14)
    ax.set_ylabel('Cost', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(query_names)
    ax.legend(fontsize=12)
    
    # Adicionar grid no eixo y
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Considerar usar escala logarítmica se houver grande variação nos valores
    max_val = max(initial_costs + stage2_values + final_costs)
    min_val = min([v for v in (initial_costs + stage2_values + final_costs) if v > 0])
    
    if max_val / min_val > 100:  # Se a razão entre máx e mín for grande
        ax.set_yscale('log')
        print("  Usando escala logarítmica devido à grande variação nos valores")
    
    # Ajustar layout
    plt.tight_layout()
    
    # Salvar gráfico
    output_path = f"{output_dir}/cost_reduction_all_queries.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    # Também criar versão em log independente da razão calculada acima
    ax.set_yscale('log')
    output_path_log = f"{output_dir}/cost_reduction_all_queries_log.png"
    plt.savefig(output_path_log, dpi=300, bbox_inches='tight')
    
    plt.close()
    
    print(f"✅ Gráfico de redução de custo salvo como: {output_path}")
    print(f"✅ Versão com escala logarítmica salva como: {output_path_log}")
    
    # PARTE 2: TABELA DETALHADA
    # =========================
    
    print("\n📋 Gerando tabela de informações detalhadas...")
    
    # Criar uma figura separada e maior para a tabela
    fig_table = plt.figure(figsize=(20, 10))  # Aumentado para acomodar mais uma coluna
    ax_table = fig_table.add_subplot(111)
    ax_table.axis('off')  # Ocultar eixos para a tabela
    
    # Função simplificada - apenas formata com 3 casas decimais
    def format_number(num):
        if num is None:
            return "N/A"
        return f"{num:.3f}"
    
    # Preparar dados para a tabela (agora com coluna para estágio 2)
    table_data = []
    for q, init, stage2, fin, red, pct in zip(query_names, initial_costs, stage2_costs, final_costs, reductions, percentages):
        table_data.append([
            q,                      # Nome da query
            format_number(init),    # Custo estágio 1
            format_number(stage2),  # Custo estágio 2 (adicionado)
            format_number(fin),     # Custo final
            format_number(red),     # Redução absoluta
        ])
    
    # Ordenar a tabela por número da query
    table_data_sorted = sorted(table_data, key=lambda x: int(x[0].replace('Q', '')))
    
    # Adicionar o cabeçalho da tabela com nomes atualizados
    column_labels = ['Query', 'Stage 1', 'Stage 2', 'Final Stage', 'Absolute Reduction']
    
    # Criar a tabela
    table = ax_table.table(
        cellText=table_data_sorted,
        colLabels=column_labels,
        loc='center',
        cellLoc='center',
        colColours=['#B0E0E6'] * 5,  # Agora são 5 colunas
        colWidths=[0.05, 0.24, 0.24, 0.24, 0.23]  # Ajustado para 5 colunas
    )
    
    # Estilizar a tabela
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1.5, 2.2)
    
    # Aplicar estilo às células
    for i, row in enumerate(table_data_sorted):
        for j in range(5):  # Agora são 5 colunas
            cell = table[i+1, j]  # +1 para pular o cabeçalho
            cell.set_facecolor('#FFFFFF')  # Branco para todas as células
            cell.set_edgecolor('#000000')
            # Centralizar os números
            if j > 0:  # Colunas numéricas
                cell.set_text_props(ha='center')
            
            # Alinhar à direita os nomes das queries
            if j == 0:  # Coluna de nome da query
                cell.set_text_props(ha='center')
                
            # Destacar células com "N/A"
            if row[j] == "N/A":
                cell.set_facecolor('#f2f2f2')  # Cinza claro para valores faltantes
    
    # Remover título
    # plt.title('Detalhes de Redução de Custo por Query', fontsize=16)  # Esta linha foi removida
    
    # Ajustar layout
    plt.tight_layout()
    
    # Salvar tabela como imagem separada
    table_output_path = f"{output_dir}/cost_reduction_table.png"
    plt.savefig(table_output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Tabela detalhada salva como: {table_output_path}")
    
    # PARTE 3: SALVAR OS DADOS EM CSV
    # ===============================
    
    # Criar DataFrame para salvar como CSV
    csv_data = {
        'Query': query_names,
        'Custo_Inicial': initial_costs,
        'Custo_Final': final_costs,
        'Reducao_Absoluta': reductions,
        'Reducao_Percentual': percentages
    }
    
    df = pd.DataFrame(csv_data)
    
    # Salvar para CSV
    csv_output_path = f"{output_dir}/cost_reduction_data.csv"
    df.to_csv(csv_output_path, index=False)
    
    print(f"✅ Dados de redução de custo salvos em CSV: {csv_output_path}")

if __name__ == "__main__":
    # Obter os dados de redução de custo
    cost_differences = calculate_cost_differences()
    
    # Gerar o gráfico
    plot_cost_reduction(cost_differences)