import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def create_graph(file_path):
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return

    # 📌 Listas para armazenar os valores
    stages = []
    custos = []
    classes_total = []
    relacionais = []
    minimos = []
    maximos = []
    medias = []

    # 📌 Ler o CSV e guardar os valores
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            stages.append(int(row["Stage"]))
            custos.append(float(row["Custo"]))
            classes_total.append(int(row["Classes_Total"]))
            relacionais.append(int(row["Relacionais"]))
            minimos.append(int(row["Min"]))
            maximos.append(int(row["Max"]))
            medias.append(float(row["Media"]))

    # Criar o gráfico de barras agrupadas
    stages = (0, 1, 2, 3)  # seus estágios
    metricas = {
        'Custo': custos,
        'Grupos de Expressões': classes_total,
        'Operadores Relacionais': relacionais,
        'Mínimo de Expressões': minimos,
        'Máximo de Expressões': maximos,
        'Média de Expressões': medias
    }

    x = np.arange(len(stages))  # posições das labels
    width = 0.15  # reduzida a largura das barras para caber mais
    multiplier = 0

    # Configurar o subplot
    fig, ax = plt.subplots(figsize=(15, 8), layout='constrained')

    # Adicionar cor de fundo
    fig.patch.set_facecolor('#478ac9') # Cor de fundo do gráfico
    ax.set_facecolor('#2e353b')  # Cor de fundo do subplot


    # Criar as barras para cada métrica
    colors = ['#FF8C00', '#008B8B', '#FF4500', '#D3D3D3', '#9370DB', '#20B2AA']
    for (attribute, measurement), color in zip(metricas.items(), colors):
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color)
        ax.bar_label(rects, padding=3, rotation=0, color='white', fontsize=8)  # Rotação vertical para caber
        multiplier += 1

    # Configurar labels e título
    ax.set_ylabel('Valores')
    ax.set_xlabel('Stages de Optimização')
    ax.set_title('Métricas')
    ax.set_xticks(x + width, stages)
    ax.legend(
        loc='upper center', 
        bbox_to_anchor=(0.5, 1.15), 
        ncol=3,
        facecolor='#2e353b',  # Cor de fundo da legenda
        edgecolor='#478ac9',  # Cor da borda da legenda
        labelcolor='white'    # Cor do texto da legenda
    )

    # Ajustar escala logarítmica para o eixo Y devido aos valores de custo
    ax.set_yscale('log')

    # Ajustar layout e aumentar o espaço para as labels
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Aumenta o espaço na parte inferior
    plt.show()

def main():
    print("Digite o caminho do arquivo CSV para gerar o gráfico:")
    file_path = input().strip()
    create_graph(file_path)

if __name__ == "__main__":
    main()