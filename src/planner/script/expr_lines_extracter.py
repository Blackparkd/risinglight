import os
import pandas as pd

def filter_last_4_rows(query):
    input_csv = os.path.join("src", "planner", "outputs", "expressions", query, "expressions.csv")
    output_dir = os.path.join("src", "planner", "outputs", "expressions", "filtered", query)
    output_csv = os.path.join(output_dir, "expressions_filtered.csv")

    if not os.path.exists(input_csv):
        print(f"Input file not found: {input_csv}")
        return

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_csv)
    filtered_df = df.tail(4)
    filtered_df.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")

def main():
    queries = ['q2', 'q5', 'q7', 'q8', 'q9']
    for query in queries:
        filter_last_4_rows(query)

if __name__ == "__main__":
    main()