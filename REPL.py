import sys
from enum import Enum
from Table import *

#insert statements are now going to look like this:

# insert 1 cstack foo@bar.com

class MetaCommandResult(Enum):
    SUCCESS = 1
    UNRECOGNIZED_COMMAND = 2

class PrepareResult(Enum):
    SUCCESS = 1
    UNRECOGNIZED_STATEMENT = 2

class Statement:
    def __init__(self):
        self.type = None

def do_meta_command(user_input):
    if user_input == ".exit":
        sys.exit(0)
    else:
        return MetaCommandResult.UNRECOGNIZED_COMMAND

def prepare_insert(user_input):
    parts=user_input.split()
    if len(parts)!=4:
        return "PREPARE_SYNTAX_ERROR",None
    try:
        id_val=int(parts[1])
    except ValueError:
        return "PREPARE_SYNTAX_ERROR", None
        
    if id_val < 0:
        return "PREPARE_NEGATIVE_ID", None

    username=parts[2]
    email=parts[3]
    username_bytes = username.encode('utf-8')
    email_bytes = email.encode('utf-8')
    
    if len(username_bytes) > COLUMN_USERNAME_SIZE:
        return "PREPARE_STRING_TOO_LONG", None
    if len(email_bytes) > COLUMN_EMAIL_SIZE:
        return "PREPARE_STRING_TOO_LONG", None
        
    # We can pass the original strings forward since our serialize_row 
    # function handles the encoding, or pass the bytes to avoid double-encoding.
    return "PREPARE_SUCCESS", {"type": "insert", "data": (id_val, username, email)}

def prepare_statement(user_input):
    if user_input.startswith("insert"):
        return prepare_insert(user_input)
    if user_input == "select":
        return "PREPARE_SUCCESS", {"type": "select"}

    return "PREPARE_UNRECOGNIZED_STATEMENT", None

def execute_insert(statement, table):
    if table.num_rows >= TABLE_MAX_ROWS:
        return "TABLE_FULL"
    
    page, offset = table.row_slots(table.num_rows)
    serialize_row(statement["data"], page, offset)
    table.num_rows += 1
    return "SUCCESS"

def execute_select(table):
    for i in range(table.num_rows):
        page, offset = table.row_slots(i)
        row = deserialize_row(page, offset)
        print(f"({row[0]}, {row[1]}, {row[2]})")
    return "SUCCESS"

def print_prompt():
    print("db > ", end="", flush=True)

def read_input():
    try:
        return input().strip()
    except EOFError:
        print()
        return ".exit"
    except Exception as e:
        print(f"Error reading input: {e}")
        sys.exit(1)

def serialize_row(row_tuple, destination_bytearray, offset):
    id_val, username, email = row_tuple
    packed_data = struct.pack(ROW_FORMAT, id_val, username.encode('utf-8'), email.encode('utf-8'))
    destination_bytearray[offset:offset + ROW_SIZE] = packed_data

def deserialize_row(source_bytearray, offset):
    data = source_bytearray[offset:offset + ROW_SIZE]
    id_val, username_bytes, email_bytes = struct.unpack(ROW_FORMAT, data)
    return (id_val, username_bytes.decode('utf-8').strip('\x00'), email_bytes.decode('utf-8').strip('\x00'))


def main():
    table=Table()
    while True:
        print_prompt()
        user_input = read_input()

        if user_input.startswith('.'):
            result = do_meta_command(user_input)
            if result == MetaCommandResult.SUCCESS:
                continue
            elif result == MetaCommandResult.UNRECOGNIZED_COMMAND:
                print(f"Unrecognized command '{user_input}'")
                continue

        # 2. Prepare Statement
        result_code,statement = prepare_statement(user_input)
        
        
        if result_code == "PREPARE_SYNTAX_ERROR":
            print("Syntax error. Could not parse statement.")
            continue
        elif result_code == "PREPARE_STRING_TOO_LONG":
            print("String is too long.")
            continue
        elif result_code == "PREPARE_NEGATIVE_ID":
            print("ID must be positive.")
            continue
        elif result_code == "PREPARE_UNRECOGNIZED_STATEMENT":
            print(f"Unrecognized keyword at start of '{user_input}'.")
            continue
        
# Execution
        if statement["type"] == "insert":
            result = execute_insert(statement, table)
            if result == "TABLE_FULL":
                print("Error: Table full.")
            else:
                print("Executed.")
        
        elif statement["type"] == "select":
            execute_select(table)
            print("Executed.")

if __name__ == "__main__":
    main()
