'''
corpus_parser.py
created 2016-1-10 by Sam Kamenetz
s
Class handles processing the texts, and organizing them into a SQLLITE database.
'''
from bs4 import BeautifulSoup
from epub_conversion.utils import *

import json
import sqlite3
import WebDB


def epub_to_txt(infile, outfile):
    #Convert epub into list of HTML strings
    epub = open_book(infile)
    lines = convert_epub_to_lines(epub)

    #Remove HTML tags and keep raw text
    beautiful_soup = BeautifulSoup("".join(lines), "html.parser")
    out = beautiful_soup.get_text(" ")

    #Write to file
    with open(outfile, 'w') as f:
        f.write(out)
        print(outfile+" written to file")

def populate_DB(infile, db_name):

    with open(infile, 'r') as f:
        json_dict = json.load(f)
        print(json_dict)
    db = WebDB.WebDB(db_name)

    for fimficID, data in iter(json_dict.values()):
        auth_dic = data["author"]
        auth_query="INSERT INTO Authors(fimficID, name) VALUES ({},{})".format(auth_dic["id"],auth_dic["name"])
        res = db.execute(auth_query)
        print(res)
        tag_dic = data["categories"]
        #problem: tag names don't necessarily match sql names for tags
        tag_query = '''INSERT INTO DocumentsToTags (docfimficID,{keys}) VALUES({fimfic},{values})'''
        tag_query = tag_query.format(keys=",".join(tag_dic.keys()), values=",".join(tag_dic.values(),fimfic=fimficID) )
        db.execute(tag_query)

        #remove items we don't care about to make my life easeir
        data.pop("author")
        data.pop("categories")
        data.pop("chapters")
        doc_query = "INSERT INTO Documents(fimficID,{keys}) VALUES({fimfic},{values})"
        doc_query = doc_query.format(fimfic=fimficID,keys=",".join(data.keys()),values=",".join(data.values()))
        db.execute(doc_query)

def main():
    #epub_to_txt("EPUBS/Metamorphosis-jackson.epub","output_test.txt")
    populate_DB("index.json", "")
main()