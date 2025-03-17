import pandas as pd
import os
import glob
import csv
import sys

def extract_stage3_classes(query_folder):
    # Construct input file path
    input_file = f"src/planner/outputs/data_classes/{query_folder}/stage_3_classes.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return

    # Create output filename
    output_dir = "src/planner/outputs/filtered_class_data"
    output_file = f"{output_dir}/{query_folder}_stage3_filtered.csv"

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read CSV file
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Store header
        
        # Extract only Class_ID and Node_Count columns
        class_data = []
        class_id_idx = header.index('Class_ID')
        node_count_idx = header.index('Node_Count')
        
        for row in reader:
            class_data.append([row[class_id_idx], row[node_count_idx]])

    # Write filtered data to new file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Class_ID', 'Node_Count'])  # Write new header
        writer.writerows(class_data)

    print(f"✅ Class data saved to {output_file}")

def main():
    if len(sys.argv) <= 1:
        print("❌ No query folder provided (e.g., q1, q2)")
        return
        
    query_folder = sys.argv[1].strip()
    extract_stage3_classes(query_folder)

if __name__ == "__main__":
    main()