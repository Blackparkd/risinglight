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

        # Special case for query 15
        if "15" in input_base:
            # Remove last 4 rows, then get the next 4 (the query costs)
            rows = rows[:-4]
            last_rows = rows[-4:]
        else:
            # Default: get last 4 rows
            last_rows = rows[-4:]

    # Write to new file
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)     # Write header
        writer.writerows(last_rows) # Write selected rows

    print(f"✅ Data saved to {output_file}")


def process_all_queries():
    # Base directory for input files
    input_dir = "src/planner/outputs/query_data"
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return

    # Process all query files in the directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith("_data.csv"):
            input_file = os.path.join(input_dir, file_name)
            print(f"Processing file: {input_file}")
            extract_last_four(input_file)


def main():
    process_all_queries()


if __name__ == "__main__":
    main()