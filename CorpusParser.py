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
    db = WebDB.WebDB(db_name)
    for fimficID in json_dict.keys():
        data = json_dict[fimficID]
        auth_dic = data["author"]
        if db.lookup_author_by_fimficid(auth_dic["id"]) == None:
            auth_query="INSERT INTO Authors(fimficID, name) VALUES (?,?)"#.format(auth_dic["id"],auth_dic["name"])
            res = db.execute(auth_query,params=(auth_dic["id"],auth_dic["name"]))
        tag_dic = data["categories"]
        #problem: fixed, but handle more elegantly with regex
        #build docs to tags query
        tag_keys_string = ( ",".join(tag_dic.keys()) ).replace(" ","_").replace("-","_").replace("2","")
        question_marks = ("?,"* len(tag_dic.keys())).rstrip(",")
        tag_query = "INSERT INTO DocumentToTags (docfimficID,{}) VALUES({id},{});".format(tag_keys_string, question_marks, id =fimficID)
        #tag_values_string = ",".join(tag_dic.values())
        #tag_query = '''''''INSERT INTO DocumentsToTags (docfimficID,{keys}) VALUES({fimfic},{values})'''
        #tag_query = tag_query.format(keys=tag_keys_string, values=tag_values_string,fimfic=fimficID)
        db.execute(tag_query, tuple(tag_dic.values()))

        #remove items we don't care about to make my life easeir
        data.pop("author")
        data.pop("categories")
        data.pop("chapters")
        doc_keys_string = ",".join(data.keys())
        question_marks = ("?,"* len(data.keys())).rstrip(",")
        doc_query = "INSERT INTO Documents (fimficID,{}) VALUES({id},{});".format(doc_keys_string, question_marks, id =fimficID)
        doc_params = tuple(data.values())
        db.execute(doc_query,params=doc_params)
        ATD_query = "INSERT INTO AuthorToDocument (authorfimficID,docfimficID) VALUES (?,?);"
        ATD_params = (auth_dic['id'],fimficID)
        db.execute(ATD_query,params=ATD_params)
        #finally, authors to documennts
    print("successfully entered metadata into database")
def main():
    #epub_to_txt("EPUBS/Metamorphosis-jackson.epub","output_test.txt")
    populate_DB("test_data.json", "data.db")
main()