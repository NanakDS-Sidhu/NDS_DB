import struct
from Pager import Pager
import sys
import os
from b_tree_helpers import *
from Cursor import Cursor

COLUMN_USERNAME_SIZE = 32
COLUMN_EMAIL_SIZE = 255

ROW_FORMAT = f"<I{COLUMN_USERNAME_SIZE}s{COLUMN_EMAIL_SIZE}s"
ROW_SIZE = struct.calcsize(ROW_FORMAT)

PAGE_SIZE = 4096
TABLE_MAX_PAGES = 100
ROWS_PER_PAGE = PAGE_SIZE // ROW_SIZE
TABLE_MAX_ROWS = ROWS_PER_PAGE * TABLE_MAX_PAGES

class Table:
    def __init__(self,pager,num_rows):
        self.pager=pager
        self.root_page_num=0

    def table_start(self):
        root_node = self.pager.get_page(self.root_page_num)
        num_cells=get_leaf_node_num_cells(root_node)
        return Cursor(table=self, page_num =self.root_page_num, cell_num = 0, end_of_table=(num_cells==0))

    def table_end(self):
        root_node = self.pager.get_page(self.root_page_num)
        num_cells=get_leaf_node_num_cells(root_node)
        return Cursor(table=self, page_num =self.root_page_num, cell_num = num_cells, end_of_table=True)
        
def db_open(filename):
    pager = Pager(filename)
    table = Table(pager)

    if pager.num_pages == 0:
        # New database file. Initialize page 0 as a leaf node.
        root_node = pager.get_page(0)
        initialize_leaf_node(root_node)

    return table

def db_close(table):
    pager = table.pager
    
    # Only flush pages we actually allocated/touched
    for i in range(pager.num_pages):
        if pager.pages[i] is None:
            continue
        pager.pager_flush(i)
        pager.pages[i] = None

    os.close(pager.file_descriptor)