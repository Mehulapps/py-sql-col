import csv
import re

def parse_from_clause(from_clause):
    """
    Parses the FROM clause to extract table names and their aliases.
    :param from_clause: The FROM clause as a string.
    :return: Dictionary mapping aliases to table names.
    """
    table_alias_map = {}
    # Split the FROM clause by commas to handle multiple tables
    tables = [table.strip() for table in from_clause.split(",")]
    for table in tables:
        parts = table.split()
        if len(parts) == 2:  # Table with alias
            table_name, alias = parts
            table_alias_map[alias] = table_name
        elif len(parts) == 1:  # Table without alias
            table_name = parts[0]
            table_alias_map[table_name] = table_name
    return table_alias_map
    

def parse_select_statement(query):
    """
    Parses a SQL SELECT statement to extract column aliases, original columns, and source tables.
    :param query: SQL query string.
    :return: List of tuples (output_column, source_column, source_table).
    """
    result = []
    
    # Normalize line endings for Windows compatibility
    query = query.replace('\r\n', ' ').replace('\n', ' ').strip()

    # Extract SELECT and FROM parts
    select_match = re.search(r"SELECT(.*?)FROM", query, re.IGNORECASE | re.DOTALL)
    from_match = re.search(r"FROM(.*?)(WHERE|GROUP BY|ORDER BY|$)", query, re.IGNORECASE | re.DOTALL)

    if not select_match or not from_match:
        return result

    select_part = select_match.group(1).strip()
    from_part = from_match.group(1).strip()

    # Parse FROM clause to get table and alias mappings
    table_alias_map = parse_from_clause(from_part)

    # Parse SELECT columns
    # Match columns, including those with functions like TO_DATE(), TO_CHAR(), etc.
    columns = re.split(r",(?![^(]*\))", select_part)  # Split by commas not inside parentheses
    for col in columns:
        col = col.strip()
        if " AS " in col.upper():
            source_column, output_column = map(str.strip, re.split(r" AS ", col, flags=re.IGNORECASE))
        else:
            source_column = output_column = col.strip()

        # Determine if the source_column contains a function
        if "(" in source_column and ")" in source_column:
            # It's a function, keep it intact
            column = source_column
            source_table = "Unknown"  # Table detection for functions is ambiguous
        elif "." in source_column:
            # It's in the form alias.column
            alias, column = source_column.split(".", 1)
            source_table = table_alias_map.get(alias, "Unknown")
        else:
            # No alias, assume it's just a column name
            column = source_column
            source_table = next(iter(table_alias_map.values()), "Unknown")  # Default to the first table

        result.append((output_column, column, source_table))
    
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
