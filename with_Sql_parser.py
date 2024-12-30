import csv
import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function
from sqlparse.tokens import Keyword, DML

def extract_tables(parsed_tokens):
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
                break
        elif token.ttype is Keyword and token.value.upper() == "FROM":
            from_seen = True
    return tables

def extract_table_alias(identifier):
    alias = identifier.get_alias() or identifier.get_real_name()
    table_name = identifier.get_real_name()
    return table_name, alias

def extract_columns(parsed_tokens, tables):
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
                break
            else:
                print(f"Unexpected token in SELECT clause: {token}")
        elif token.ttype is DML and token.value.upper() == "SELECT":
            select_seen = True
    return columns

def parse_column(identifier, tables):
    if not isinstance(identifier, (Identifier, Function)):
        return None

    try:
        output_column = identifier.get_alias() or identifier.get_real_name()
        source_column = identifier.get_real_name()

        source_table = "Unknown"
        if isinstance(identifier, Function):
            source_column = str(identifier)
        elif "." in source_column:
            alias, column_name = source_column.split(".", 1)
            source_table = tables.get(alias, "Unknown")
            source_column = column_name
        else:
            source_table = next(iter(tables.values()), "Unknown")

        return output_column, source_column, source_table

    except Exception as e:
        print(f"Error processing column: {identifier}, error: {e}")
        return None

def split_union_queries(query):
    queries = []
    parsed = sqlparse.parse(query)

    for stmt in parsed:
        if stmt.get_type() == "SELECT":
            queries.append(str(stmt).strip())
        else:
            union_parts = re.split(r"\bUNION(?: ALL)?\b", str(stmt), flags=re.IGNORECASE)
            queries.extend([part.strip() for part in union_parts])

    return queries

def parse_select_statement(query):
    queries = split_union_queries(query)
    all_columns = []

    for subquery in queries:
        parsed = sqlparse.parse(subquery)[0]  # Parse the query into tokens
        tables = extract_tables(parsed.tokens)
        columns = extract_columns(parsed.tokens, tables)
        all_columns.extend(columns)

    return all_columns

def process_csv(input_file, output_file):
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

if __name__ == "__main__":
    input_csv_path = "input.csv"
    output_csv_path = "output.csv"
    process_csv(input_csv_path, output_csv_path)




if __name__ == "__main__":
    input_csv_path = "input.csv"  # Replace with your input file path
    output_csv_path = "output.csv"  # Replace with your desired output file path

    process_csv(input_csv_path, output_csv_path)
