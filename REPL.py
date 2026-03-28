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

def do_meta_command(user_input, table):
    if user_input == ".exit":
        db_close(table)
        sys.exit(0)
    elif user_input == ".constants":
        print(f"ROW_SIZE: {ROW_SIZE}")
        print(f"COMMON_NODE_HEADER_SIZE: {COMMON_NODE_HEADER_SIZE}")
        print(f"LEAF_NODE_HEADER_SIZE: {LEAF_NODE_HEADER_SIZE}")
        print(f"LEAF_NODE_CELL_SIZE: {LEAF_NODE_CELL_SIZE}")
        print(f"LEAF_NODE_SPACE_FOR_CELLS: {LEAF_NODE_SPACE_FOR_CELLS}")
        print(f"LEAF_NODE_MAX_CELLS: {LEAF_NODE_MAX_CELLS}")
        return "META_COMMAND_SUCCESS"
    elif user_input == ".btree":
        print("Tree:")
        root_node = table.pager.get_page(0)
        num_cells = get_leaf_node_num_cells(root_node)
        print(f"leaf (size {num_cells})")
        for i in range(num_cells):
            key = get_leaf_node_key(root_node, i)
            print(f"  - {i} : {key}")
        return "META_COMMAND_SUCCESS"
    else:
        return "META_COMMAND_UNRECOGNIZED_COMMAND"
    
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

def leaf_node_insert(cursor,key,value_tuple):
    node=cursor.table.pager.get_page(cursor.page_num)
    num_cells = get_leaf_node_num_cells(node)

    if num_cells >= LEAF_NODE_CELL_SIZE:
        print("Need to implement splitting a leaf node.")
        sys.exit(1)
    
    if cursor.cell_num < num_cells:
        for i in range(num_cells,cursor.cell_num ,-1):
            src_offset= leaf_node_cell_offset(i-1)
            dest_offset = leaf_node_cell_offset(i)
            node[dest_offset : dest_offset + LEAF_NODE_CELL_SIZE] = node[src_offset : src_offset + LEAF_NODE_CELL_SIZE]

    # Update cell count, write the key, and write the value
    set_leaf_node_num_cells(node, num_cells + 1)
    set_leaf_node_key(node, cursor.cell_num, key)
    
    # serialize_row writes the value to the specific offset
    _, value_offset = cursor.value()
    serialize_row(value_tuple, node, value_offset)

def execute_insert(statement, table):
    node = table.pager.get_page(table.root_page_num)
    if get_leaf_node_num_cells(node) >= LEAF_NODE_MAX_CELLS:
        return "TABLE_FULL"

    row_data = statement["data"]
    key_to_insert = row_data # ID is the key
    
    cursor = table.table_end()
    leaf_node_insert(cursor, key_to_insert, row_data)
    
    return "SUCCESS"


def execute_select(table):
    cursor= table.table_start()
    while not cursor.end_of_table:
        page, offset = cursor.value()
        row = deserialize_row(page, offset)
        print(f"({row[0]}, {row[1]}, {row[2]})")
        cursor.advance()
 
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
    if len(sys.argv) < 2:
        print("Must supply a database filename.")
        sys.exit(1)

    file_name=sys.argv[1]
    table=db_open(file_name)  
    while True:
        print_prompt()
        user_input = read_input()

        if user_input.startswith('.'):
            result = do_meta_command(user_input,table)
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
