import csv
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function
from sqlparse.tokens import Keyword, DML

def extract_tables(parsed_tokens):
    """
    Extracts table names and aliases from the FROM clause.
    :param parsed_tokens: Tokens parsed from the SQL query.
    :return: Dictionary mapping aliases to table names.
    """
    tables = {}
    from_seen = False

    for token in parsed_tokens:
        if from_seen:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    table_name, alias = extract_table_alias(identifier)
                    tables[alias] = table_name
            elif isinstance(token, Identifier):
                table_name, alias = extract_table_alias(token)
                tables[alias] = table_name
            elif token.ttype is Keyword and token.value.upper() in ("WHERE", "GROUP BY", "ORDER BY"):
                break  # End of FROM clause
        elif token.ttype is Keyword and token.value.upper() == "FROM":
            from_seen = True
    return tables

def extract_table_alias(identifier):
    """
    Extracts the table name and its alias from an identifier.
    :param identifier: A sqlparse Identifier object.
    :return: Tuple of (table_name, alias).
    """
    alias = identifier.get_alias() or identifier.get_real_name()
    table_name = identifier.get_real_name()
    return table_name, alias

def extract_columns(parsed_tokens, tables):
    """
    Extracts columns, aliases, and their corresponding tables from the SELECT clause.
    :param parsed_tokens: Tokens parsed from the SQL query.
    :param tables: Dictionary mapping aliases to table names.
    :return: List of tuples (output_column, source_column, source_table).
    """
    columns = []
    select_seen = False

    for token in parsed_tokens:
        if select_seen:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    column_data = parse_column(identifier, tables)
                    if column_data:
                        columns.append(column_data)
            elif isinstance(token, (Identifier, Function)):
                column_data = parse_column(token, tables)
                if column_data:
                    columns.append(column_data)
            elif token.ttype is Keyword and token.value.upper() == "FROM":
                break  # End of SELECT clause
        elif token.ttype is DML and token.value.upper() == "SELECT":
            select_seen = True
    return columns

def parse_column(identifier, tables):
    """
    Parses an individual column to extract its alias, source column, and table.
    :param identifier: A sqlparse Identifier or Function object.
    :param tables: Dictionary mapping aliases to table names.
    :return: Tuple (output_column, source_column, source_table).
    """
    output_column = identifier.get_alias() or identifier.get_real_name()
    source_column = identifier.get_real_name()

    # Determine the source table
    source_table = "Unknown"
    if isinstance(identifier, Function):
        # It's a function, keep it intact
        source_column = str(identifier)  # Keep the entire function as the source column
        source_table = "Unknown"
    elif "." in source_column:
        # It's in the form alias.column
        alias, column_name = source_column.split(".", 1)
        source_table = tables.get(alias, "Unknown")
        source_column = column_name
    else:
        # No alias, assume it's just a column name
        source_table = next(iter(tables.values()), "Unknown")  # Default to the first table

    return output_column, source_column, source_table

def parse_select_statement(query):
    """
    Parses a SQL SELECT statement to extract column aliases, original columns, and source tables.
    :param query: SQL query string.
    :return: List of tuples (output_column, source_column, source_table).
    """
    parsed = sqlparse.parse(query)[0]  # Parse the query into tokens
    tables = extract_tables(parsed.tokens)
    columns = extract_columns(parsed.tokens, tables)
    return columns

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
