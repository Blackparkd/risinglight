import re
import csv

# Já consegue ler o ficheiro de input e escrever o ficheiro de output
# Falta apenas filtrar os dados corretamente
# VER DEPOIS 

# Caminho do ficheiro de entrada e saída
input_file = "src/planner/outputs/testfile.csv"
output_file = "src/planner/outputs/filtered_data.csv"

# Expressões regex para capturar os valores desejados
regex_custo = re.compile(r"Custo (?:inicial|atual|final): ([\d.]+)")
regex_relacionais = re.compile(r"Relacionais: (\d+)")
regex_min = re.compile(r"Mínimo: (\d+)")
regex_max = re.compile(r"Máximo: (\d+)")
regex_media = re.compile(r"Média: ([\d.]+)")
regex_classes = re.compile(r"Classes-Total (\d+)")
regex_stage = re.compile(r"Stage (\d+)")
regex_iteracao = re.compile(r"Iteração: (\d+)")

# Lista para armazenar os dados extraídos
dados = []
stage_atual = None
iteracao_atual = None
custo_atual = None
relacionais_atual = None
classes_total = None
minimo = None
maximo = None
media = None
stage_atual = None

# Ler o ficheiro linha por linha
with open(input_file, "r", encoding="utf-8") as infile:
    for linha in infile:
        linha = linha.strip()  # Remover espaços desnecessários
        
        # Detectar mudança de estágio
        match_stage = regex_stage.search(linha)
        if match_stage:
            stage_atual = match_stage.group(1)
            iteracao_atual = None  # Reset para garantir que as iterações de cada estágio sejam capturadas

        # Detectar mudança de iteração
        match_iteracao = regex_iteracao.search(linha)
        if match_iteracao:
            iteracao_atual = match_iteracao.group(1)

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

        # **Salvar os dados de cada iteração corretamente**
        if stage_atual and iteracao_atual is not None and custo_atual and relacionais_atual and classes_total and minimo and maximo and media:
            print(f"Stage: {stage_atual}, Iteração: {iteracao_atual}, Custo: {custo_atual}, Relacionais: {relacionais_atual}, Classes: {classes_total}, Min: {minimo}, Max: {maximo}, Média: {media}")  # Debug
            dados.append([stage_atual, iteracao_atual, custo_atual, relacionais_atual, classes_total, minimo, maximo, media])
            
            # Reset dos valores **APENAS** depois de salvar os dados para garantir que não sejam sobrescritos
            iteracao_atual = None
            custo_atual = None
            relacionais_atual = None
            classes_total = None
            minimo = None
            maximo = None
            media = None

# Escrever os dados filtrados num novo ficheiro CSV
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    escritor = csv.writer(outfile)
    escritor.writerow(["Stage", "Iteração", "Custo", "Relacionais", "Classes_Total", "Min", "Max", "Media"])  # Cabeçalhos
    escritor.writerows(dados)

print(f"✅ Dados filtrados guardados em {output_file}")
