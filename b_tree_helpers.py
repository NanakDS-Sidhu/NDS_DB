import struct

# --- NODE CONSTANTS ---
NODE_TYPE_SIZE = 1
NODE_TYPE_OFFSET = 0
IS_ROOT_SIZE = 1
IS_ROOT_OFFSET = NODE_TYPE_SIZE
PARENT_POINTER_SIZE = 4
PARENT_POINTER_OFFSET = IS_ROOT_OFFSET + IS_ROOT_SIZE
COMMON_NODE_HEADER_SIZE = NODE_TYPE_SIZE + IS_ROOT_SIZE + PARENT_POINTER_SIZE # 6 bytes

# Leaf Node Header
LEAF_NODE_NUM_CELLS_SIZE = 4
LEAF_NODE_NUM_CELLS_OFFSET = COMMON_NODE_HEADER_SIZE
LEAF_NODE_HEADER_SIZE = COMMON_NODE_HEADER_SIZE + LEAF_NODE_NUM_CELLS_SIZE # 10 bytes

# Leaf Node Body
LEAF_NODE_KEY_SIZE = 4
LEAF_NODE_KEY_OFFSET = 0
LEAF_NODE_VALUE_SIZE = ROW_SIZE
LEAF_NODE_VALUE_OFFSET = LEAF_NODE_KEY_OFFSET + LEAF_NODE_KEY_SIZE
LEAF_NODE_CELL_SIZE = LEAF_NODE_KEY_SIZE + LEAF_NODE_VALUE_SIZE
LEAF_NODE_SPACE_FOR_CELLS = PAGE_SIZE - LEAF_NODE_HEADER_SIZE
LEAF_NODE_MAX_CELLS = LEAF_NODE_SPACE_FOR_CELLS // LEAF_NODE_CELL_SIZE

# --- PYTHON POINTER HELPERS ---
# Since we don't have pointers, we use helper functions to get/set bytes.

def get_leaf_node_num_cells(node_bytearray):
    return struct.unpack_from("<I", node_bytearray, LEAF_NODE_NUM_CELLS_OFFSET)

def set_leaf_node_num_cells(node_bytearray, num_cells):
    struct.pack_into("<I", node_bytearray, LEAF_NODE_NUM_CELLS_OFFSET, num_cells)

def initialize_leaf_node(node_bytearray):
    set_leaf_node_num_cells(node_bytearray, 0)

def leaf_node_cell_offset(cell_num):
    return LEAF_NODE_HEADER_SIZE + (cell_num * LEAF_NODE_CELL_SIZE)

def get_leaf_node_key(node_bytearray, cell_num):
    offset = leaf_node_cell_offset(cell_num)
    return struct.unpack_from("<I", node_bytearray, offset)

def set_leaf_node_key(node_bytearray, cell_num, key):
    offset = leaf_node_cell_offset(cell_num)
    struct.pack_into("<I", node_bytearray, offset, key)

def leaf_node_value_offset(cell_num):
    return leaf_node_cell_offset(cell_num) + LEAF_NODE_KEY_SIZE