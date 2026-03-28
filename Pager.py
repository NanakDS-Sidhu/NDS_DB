import os
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

class Pager:
    def __init__(self,filename):
        self.filename=filename
        self.file_descriptor=os.open(filename,os.O_RDWR | os.O_CREAT)

        self.file_length=os.lseek(self.file_descriptor,0,os.SEEK_END)
        if self.file_length %PAGE_SIZE!=0:
            print("Db file is not a whole number of pages. Corrupt file.")
            sys.exit(1)
        
        self.num_pages=self.file_length // PAGE_SIZE
        self.pages=[None]*TABLE_MAX_PAGES
    
    def get_page(self,page_num):
        if page_num >= TABLE_MAX_PAGES:
            print(f"Tried to fetch page number out of bounds. {page_num} >= {TABLE_MAX_PAGES}")
            sys.exit(1)
        
        if self.pages[page_num] is None:
            page=bytearray(PAGE_SIZE)
        
            if page_num < self.num_pages:
                os.lseek(self.file_descriptor,page_num*PAGE_SIZE,os.SEEK_SET)
                bytes_read=os.read(self.file_descriptor,PAGE_SIZE)
                page[:len(bytes_read)]=bytes_read
            
            self.pages[page_num]=page

            if page_num >= page.num_pages:
                self.num_pages=page_num+1

        return self.pages[page_num]

    def pager_flush(self,page_num,size):
        if self.pages[page_num] is None:
            print("Tried to flush null page")
            sys.exit(1)

        os.lseek(self.file_descriptor, page_num * PAGE_SIZE, os.SEEK_SET)
        os.write(self.file_descriptor, self.pages[page_num][:size])