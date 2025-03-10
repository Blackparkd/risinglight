import csv
import os
import sys

def extract_last_four(input_file):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    # Create output filename
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = "src/planner/outputs/filtered_query_data"
    output_file = f"{output_dir}/{input_base}_filtered.csv"

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read all CSV lines
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Store header
        rows = list(reader)    # Convert rest of file to list
        
        # Get last 4 rows
        last_four = rows[-4:]

    # Write to new file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)     # Write header
        writer.writerows(last_four) # Write last 4 rows

    print(f"✅ Data saved to {output_file}")



def main():
    if len(sys.argv) <= 1:
        print("❌ No file path provided")
        return
        
    file_path = sys.argv[1].strip()
    extract_last_four(file_path)

if __name__ == "__main__":
    main()