import re
import csv
import os

# Caminho do ficheiro de entrada e saída
input_file = "src/planner/outputs/testfile.csv"
output_file = "src/planner/outputs/filtered_data.csv"

# Verificar se o arquivo de entrada existe
if not os.path.exists(input_file):
    print(f"❌ Arquivo de entrada não encontrado: {input_file}")
    exit(1)

# Expressões regex para capturar os valores desejados
regex_custo = re.compile(r"Custo\w+?: ([\d.]+)")  # Captura "CustoI", "Custo1", "Custo2", etc.
regex_relacionais = re.compile(r"Relacionais: (\d+)")
regex_min = re.compile(r"Mínimo: (\d+)")
regex_max = re.compile(r"Máximo: (\d+)")
regex_media = re.compile(r"Média: ([\d.]+)")
regex_classes = re.compile(r"Classes-Total (\d+)")
regex_stage = re.compile(r"Stage (\d+)")

# Lista para armazenar os dados extraídos
dados = []
stage_atual = None
custo_atual = None
relacionais_atual = None
classes_total = None
minimo = None
maximo = None
media = None

# Ler o ficheiro linha por linha
with open(input_file, "r", encoding="utf-8") as infile:
    for linha in infile:
        linha = linha.strip()  # Remover espaços desnecessários
        
        # Detectar mudança de estágio
        match_stage = regex_stage.search(linha)
        if match_stage:
            # Se uma nova Stage começa, salve os dados da Stage anterior (se existirem)
            if stage_atual is not None:
                # Verifique se todos os valores necessários estão presentes
                if custo_atual and relacionais_atual and classes_total and minimo and maximo and media:
                    dados.append([stage_atual, custo_atual, relacionais_atual, classes_total, minimo, maximo, media])
            
            # Reiniciar os valores para a nova Stage
            stage_atual = match_stage.group(1)
            custo_atual = None
            relacionais_atual = None
            classes_total = None
            minimo = None
            maximo = None
            media = None

        # Procurar os valores desejados
        match_custo = regex_custo.search(linha)
        match_relacionais = regex_relacionais.search(linha)
        match_classes = regex_classes.search(linha)
        match_min = regex_min.search(linha)
        match_max = regex_max.search(linha)
        match_media = regex_media.search(linha)

        if match_custo:
            custo_atual = match_custo.group(1)

        if match_relacionais:
            relacionais_atual = match_relacionais.group(1)

        if match_classes:
            classes_total = match_classes.group(1)

        if match_min:
            minimo = match_min.group(1)

        if match_max:
            maximo = match_max.group(1)

        if match_media:
            media = match_media.group(1)

    # Após o loop, salvar os dados da última Stage (se existirem)
    if stage_atual is not None:
            if custo_atual and relacionais_atual and classes_total and minimo and maximo and media:
                dados.append([stage_atual, custo_atual, relacionais_atual, classes_total, minimo, maximo, media])

# Escrever os dados filtrados num novo ficheiro CSV
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    escritor = csv.writer(outfile)
    escritor.writerow(["Stage", "Custo", "Relacionais", "Classes_Total", "Min", "Max", "Media"])  # Cabeçalhos
    escritor.writerows(dados)

print(f"✅ Dados filtrados guardados em {output_file}")


# Caminhos dos ficheiros
input_file1 = "src/planner/outputs/filtered_data.csv"
output_file1 = "src/planner/outputs/query_data.csv"

# Ler todas as linhas do CSV
with open(input_file1, 'r', encoding='utf-8') as file:
    # Usar o DictReader para manter os cabeçalhos
    reader = csv.reader(file)
    header = next(reader)  # Guardar o cabeçalho
    rows = list(reader)    # Converter resto do arquivo em lista
    
    # Pegar as últimas 4 linhas
    last_four = rows[-4:]

# Escrever no novo arquivo
with open(output_file1, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)     # Escrever o cabeçalho
    writer.writerows(last_four) # Escrever as últimas 4 linhas

print(f"✅ Últimas 4 linhas guardadas em {output_file1}")