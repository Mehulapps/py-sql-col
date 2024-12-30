import csv
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

def extract_table_name(from_clause):
    """
    Extracts table names from the FROM clause.
    :param from_clause: Parsed SQL token representing the FROM clause.
    :return: List of table names.
    """
    tables = []
    for token in from_clause.tokens:
        if isinstance(token, Identifier):
            tables.append(token.get_real_name())
    return tables

def parse_sql_query(query):
    """
    Parses a SQL SELECT statement to extract column aliases, original columns, and source tables.
    :param query: SQL query string.
    :return: List of tuples (output_column, source_column, source_table).
    """
    parsed = sqlparse.parse(query)[0]  # Parse the query
    columns = []
    tables = []

    # Process SELECT and FROM parts
    in_select = False
    in_from = False

    for token in parsed.tokens:
        if token.ttype is DML and token.value.upper() == 'SELECT':
            in_select = True
            continue
        if token.ttype is Keyword and token.value.upper() == 'FROM':
            in_select = False
            in_from = True
            continue

        if in_select:
            # Extract columns
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    alias = identifier.get_alias() or identifier.get_real_name()
                    source = identifier.get_real_name()
                    columns.append((alias, source))
            elif isinstance(token, Identifier):
                alias = token.get_alias() or token.get_real_name()
                source = token.get_real_name()
                columns.append((alias, source))

        if in_from:
            # Extract tables
            if isinstance(token, IdentifierList):
                tables.extend([table.get_real_name() for table in token.get_identifiers()])
            elif isinstance(token, Identifier):
                tables.append(token.get_real_name())

    # Assume all columns belong to the first table for simplicity
    if tables:
        source_table = tables[0]
        return [(col[0], col[1], source_table) for col in columns]

    return []

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

                parsed_columns = parse_sql_query(select_statement)
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
