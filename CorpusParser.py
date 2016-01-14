'''
corpus_parser.py
created 2016-1-10 by Sam Kamenetz
s
Class handles processing the texts, and organizing them into a SQLLITE database.
'''
from bs4 import BeautifulSoup

from epub_conversion.utils import *

def epub_to_txt(infile, outfile):
    #convert epub into list of html strings
    epub = open_book(infile)
    lines = convert_epub_to_lines(epub)

    #Remove HTML tags and keep raw text
    beautiful_soup = BeautifulSoup("".join(lines), "html.parser")
    out = beautiful_soup.get_text(" ")
    with open(outfile, 'w') as f:
        f.write(out)
        print(outfile+" written to file")

def main():
    epub_to_txt("EPUBS/Metamorphosis-jackson.epub","output_test.txt")
main()