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

class StatementType(Enum):
    INSERT = 1
    SELECT = 2

class Statement:
    def __init__(self):
        self.type = None

def do_meta_command(user_input):
    if user_input == ".exit":
        sys.exit(0)
    else:
        return MetaCommandResult.UNRECOGNIZED_COMMAND

def prepare_statement(user_input, statement):
    if user_input.startswith("insert"):
        statement.type = StatementType.INSERT
        return PrepareResult.SUCCESS
    if user_input == "select":
        statement.type = StatementType.SELECT
        return PrepareResult.SUCCESS
    
    return PrepareResult.UNRECOGNIZED_STATEMENT

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


def execute_statement(statement):
    if statement.type == StatementType.INSERT:
        print("This is where we would do an insert.")
    elif statement.type == StatementType.SELECT:
        print("This is where we would do a select.")

def main():
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
        statement = Statement()
        result = prepare_statement(user_input, statement)
        
        if result == PrepareResult.UNRECOGNIZED_STATEMENT:
            print(f"Unrecognized keyword at start of '{user_input}'.")
            continue
        
        # 3. Execute Statement
        execute_statement(statement)
        print("Executed.")

if __name__ == "__main__":
    main()
