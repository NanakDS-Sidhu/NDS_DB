from Pager import *
class Cursor:
    def __init__(self,table,row_num,end_of_table):
        self.table=table
        self.row_num=row_num
        self.end_of_table=end_of_table

    def value(self):
        page_num=self.row_num//ROWS_PER_PAGE
        page=self.table.pager.get_page(page_num)
        
        row_offset = self.row_num % ROWS_PER_PAGE
        byte_offset = row_offset * ROW_SIZE

        return page , byte_offset

    def advance(self):
        self.row_num+=1
        if self.row_num >= self.table.num_rows:
            self.end_of_table=True
