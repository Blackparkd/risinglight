import os
import pandas as pd

def filter_last_4_rows(query):
    input_csv = os.path.join("src", "planner", "outputs", "expressions", query, "expressions.csv")
    output_dir = os.path.join("src", "planner", "outputs", "expressions", "filtered", query)
    output_csv = os.path.join(output_dir, "expressions_filtered.csv")

    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        return

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_csv)
    if df.empty:
        print(f"⚠️ Input file is empty: {input_csv}")
        return

    filtered_df = df.tail(4)
    filtered_df.to_csv(output_csv, index=False)
    print(f"✅ Saved: {output_csv}")


def process_all_queries():
    input_dir = "src/planner/outputs/expressions"
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return

    # Process all query folders in the directory
    for query_folder in os.listdir(input_dir):
        query_path = os.path.join(input_dir, query_folder)
        if os.path.isdir(query_path) and query_folder.startswith("q"):
            print(f"🔍 Processing query: {query_folder}")
            filter_last_4_rows(query_folder)


def main():
    process_all_queries()


if __name__ == "__main__":
    main()