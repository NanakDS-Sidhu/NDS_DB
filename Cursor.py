from Pager import *
from b_tree_helpers import *
class Cursor:
    def __init__(self,table,page_num,cell_num,end_of_table):
        self.table=table
        self.page_num=page_num
        self.cell_num=cell_num
        self.end_of_table=end_of_table

    def value(self):
        page=self.table.pager.get_page(self.page_num)
        return page , leaf_node_cell_offset(self.cell_num)

    def advance(self):
        page=self.table.pager.get_page(self.page_num)
        self.cell_num+=1
        if self.cell_num >= get_leaf_node_num_cells(page):
            self.end_of_table=True
        
