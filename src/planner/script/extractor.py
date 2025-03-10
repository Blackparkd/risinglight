import csv
import os

def extract_last_four(input_file):
    # Verificar se o arquivo de entrada existe
    if not os.path.exists(input_file):
        print(f"❌ Arquivo não encontrado: {input_file}")
        return

    # Criar nome do arquivo de saída
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = "src/planner/outputs/filtered_query_data"
    output_file = f"{output_dir}/{input_base}_filtered.csv"

    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Ler todas as linhas do CSV
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Guardar o cabeçalho
        rows = list(reader)    # Converter resto do arquivo em lista
        
        # Pegar as últimas 4 linhas
        last_four = rows[-4:]

    # Escrever no novo arquivo
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)     # Escrever o cabeçalho
        writer.writerows(last_four) # Escrever as últimas 4 linhas

    print(f"✅ Últimas 4 linhas guardadas em {output_file}")

def main():
    print("Digite o caminho do arquivo CSV para extrair as últimas 4 linhas:")
    input_file = input().strip()
    extract_last_four(input_file)

if __name__ == "__main__":
    main()