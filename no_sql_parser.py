import csv
import re

def parse_select_statement(query):
    """
    Parses a SQL SELECT statement to extract column aliases, original columns, and source tables.
    :param query: SQL query string.
    :return: List of tuples (output_column, source_column, source_table).
    """
    result = []
    
    # Extract SELECT and FROM parts
    select_match = re.search(r"SELECT(.*?)FROM", query, re.IGNORECASE | re.DOTALL)
    from_match = re.search(r"FROM(.*?)(WHERE|GROUP BY|ORDER BY|$)", query, re.IGNORECASE | re.DOTALL)

    if not select_match or not from_match:
        return result

    select_part = select_match.group(1).strip()
    from_part = from_match.group(1).strip()

    # Get the first table from the FROM part
    source_table = from_part.split()[0]

    # Parse SELECT columns
    columns = [col.strip() for col in select_part.split(",")]
    for col in columns:
        if " AS " in col.upper():
            source_column, output_column = map(str.strip, re.split(r" AS ", col, flags=re.IGNORECASE))
        else:
            source_column = output_column = col

        result.append((output_column, source_column, source_table))
    
    return result

def process_csv(input_file, output_file):
    """
    Reads a CSV file and processes SQL queries to extract column and table information.
    :param input_file: Path to input CSV.
    :param output_file: Path to output CSV.
    """
    rows = []
    try:
        with open(input_file, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                logical_name = row['logical_name']
                select_statement = row['select_statement']

                parsed_columns = parse_select_statement(select_statement)
                for output_column, source_column, source_table in parsed_columns:
                    rows.append({
                        "logical_name": logical_name,
                        "output_column_name": output_column,
                        "source_column_name": source_column,
                        "source_table_name": source_table
                    })

        # Write results to output CSV
        with open(output_file, mode='w', newline='', encoding='utf-8') as csv_out:
            writer = csv.DictWriter(csv_out, fieldnames=[
                "logical_name",
                "output_column_name",
                "source_column_name",
                "source_table_name"
            ])
            writer.writeheader()
            writer.writerows(rows)

        print(f"Output successfully written to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# File paths
input_csv_path = "/mnt/data/sql_column_export_testdata - Sheet1.csv"  # Input file
output_csv_path = "/mnt/data/output_parsed_columns.csv"  # Output file

# Process the CSV file
process_csv(input_csv_path, output_csv_path)