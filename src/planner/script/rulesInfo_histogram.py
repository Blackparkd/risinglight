#!/usr/bin/env python3

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
import re

def load_all_rule_files(query_folder, stage=None):
    """
    Load all rule files for a given query and stage.
    If stage is None, load all stages.
    """
    base_dir = f"src/planner/outputs/rules_data/{query_folder}_data"
    pattern = f"stage_{stage if stage else '*'}_iter_*_rules_application.csv"
    all_files = glob.glob(os.path.join(base_dir, pattern))
    
    if not all_files:
        print(f"❌ No files found for pattern: {os.path.join(base_dir, pattern)}")
        return None
    
    # Sort files to process them in order
    all_files.sort(key=lambda x: [int(n) if n.isdigit() else n for n in re.findall(r'\d+|[A-Za-z]+', x)])
    
    all_data = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            # Extract stage and iteration info from the filename
            match = re.search(r'stage_(\d+)_iter_(\d+)', file)
            if match:
                file_stage = match.group(1)
                file_iter = match.group(2)
                # Add columns to identify the source file if they don't exist
                if 'Stage' not in df.columns:
                    df['Stage'] = file_stage
                if 'External_Iteration' not in df.columns:
                    df['External_Iteration'] = file_iter
                
            all_data.append(df)
            print(f"✅ Loaded: {file}")
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
    
    if not all_data:
        return None
    
    # Concatenate all DataFrames
    return pd.concat(all_data, ignore_index=True)

def create_rule_application_heatmap(df, query_folder, stage=None):
    """
    Create a heatmap showing rule applications per iteration.
    """
    # Filter rows with applied rules (not 'None')
    df_rules = df[df['Rule_Name'] != 'None'].copy()
    
    # Create a pivot table with iterations as rows, rules as columns, and applications as values
    pivot = df_rules.pivot_table(
        index=['External_Iteration', 'Internal_Iteration'],
        columns='Rule_Name',
        values='Applications',
        aggfunc='sum',
        fill_value=0
    )
    
    # Configure the heatmap
    plt.figure(figsize=(16, 10))
    ax = sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".0f", linewidths=.5)
    
    plt.title(f"Rule Applications Heatmap - Query {query_folder}, Stage {stage if stage else 'All'}", fontsize=16)
    plt.ylabel("Iteration (External, Internal)")
    plt.xlabel("Rule")
    plt.xticks(rotation=45, ha="right")
    
    # Save the heatmap
    stage_str = f"stage{stage}" if stage else "all_stages"
    output_dir = f"src/planner/outputs/bar_charts/rules_stats/{query_folder}/{stage_str}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/rule_heatmap.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Heatmap saved as: {output_path}")

def process_all_queries():
    """
    Process all queries in the rules_data directory.
    """
    base_dir = "src/planner/outputs/rules_data"
    if not os.path.exists(base_dir):
        print(f"❌ Base directory not found: {base_dir}")
        return

    # Iterate over all query folders
    for query_folder in os.listdir(base_dir):
        if query_folder.endswith("_data") and query_folder.startswith("q"):
            query_name = query_folder.split("_")[0]  # Extract query name (e.g., "q1")
            print(f"\n🔍 Processing query: {query_name}")
            
            # Load all rule files for the query
            df = load_all_rule_files(query_name)
            if df is None:
                print(f"❌ No data found for query: {query_name}")
                continue
            
            # Create heatmaps for all stages
            create_rule_application_heatmap(df, query_name)

def main():
    process_all_queries()

if __name__ == "__main__":
    main()