import struct
from Pager import Pager
import sys
import os

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

    def row_slot(self,row_num):
        page_num=row_num//ROWS_PER_PAGE
        page=self.pager.get_page(page_num)

        row_offset = row_num % ROWS_PER_PAGE
        byte_offset = row_offset * ROW_SIZE
        return page , byte_offset

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