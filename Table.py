import struct
import sys

COLUMN_USERNAME_SIZE = 32
COLUMN_EMAIL_SIZE = 255

ROW_FORMAT = f"<I{COLUMN_USERNAME_SIZE}s{COLUMN_EMAIL_SIZE}s"
ROW_SIZE = struct.calcsize(ROW_FORMAT)

PAGE_SIZE = 4096
TABLE_MAX_PAGES = 100
ROWS_PER_PAGE = PAGE_SIZE // ROW_SIZE
TABLE_MAX_ROWS = ROWS_PER_PAGE * TABLE_MAX_PAGES

class Table:
    def __init__(self):
        self.num_rows=0
        self.pages=[None] * TABLE_MAX_PAGES

    def row_slots(self,row_num):
        page_num=row_num//ROWS_PER_PAGE
        if self.pages[page_num]==None:
            self.pages[page_num]=bytearray(PAGE_SIZE)

        row_offset = row_num % ROWS_PER_PAGE
        byte_offset = row_offset * ROW_SIZE
        return self.pages[page_num], byte_offset

