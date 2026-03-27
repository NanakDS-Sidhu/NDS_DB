import struct
from Pager import Pager
import sys
import os
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
        self.num_rows=num_rows

    def table_start(self):
        is_end = (self.num_rows ==0) 
        return Cursor(table=self,row_num=0,end_of_table=is_end)
    def table_end(self):
        return Cursor(table=self,row_num=self.num_rows,end_of_table=True)
        

def db_open(filename):
    pager=Pager(filename)
    num_rows=pager.file_length // ROW_SIZE
    return Table(pager,num_rows)


def db_close(table):
    pager=table.pager
    num_full_pages= table.num_rows // ROWS_PER_PAGE

    for i in range(num_full_pages):
        if pager.pages[i] is None:
            continue
        pager.page_flush(i,PAGE_SIZE)
        pager.pages[i]=None

    num_addition_rows=table.num_rows%ROWS_PER_PAGE
    if num_addition_rows > 0:
        page_num=num_full_pages
        if pager.pages[page_num] is not None:
            pager.pager_flush(page_num , num_addition_rows * ROW_SIZE)
            pager.pages[page_num] = None

    os.close(pager.file_descriptor)