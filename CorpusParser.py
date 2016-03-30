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
import os.path
import codecs
import epub
import pywin32_system32

def epub_to_string(infile):
    out = ""
    with epub.open_epub(infile) as book:
        #opf is file that contains info and structure on all other files in epub zip
        for item in book.opf.manifest.values():
            out += book.read_item(item)
    return out

def epub_to_txt(infile, outfile):
    #Convert epub into list of HTML strings
    #epub = open_book(infile)
    #lines = convert_epub_to_lines(epub)
    lines = epub_to_string(infile)
    #Remove HTML tags and keep raw text
    beautiful_soup = BeautifulSoup("".join(lines), "html.parser")
    out = beautiful_soup.get_text(" ")
    #Write to file
    with codecs.open(outfile, 'w',encoding="utf-16") as f:
        f.write(out)
        print(outfile+" written to file")

def populate_DB(infile, db_name):

    with open(infile, 'r') as f:
        json_dict = json.load(f)
    db = WebDB.WebDB(db_name)
    for fimficID in json_dict.keys():
        data = json_dict[fimficID]
        auth_dic = data["author"]
        if db.lookup_author_by_authorID(auth_dic["id"]) == None:
            auth_query="INSERT INTO Authors(fimficID, name) VALUES (?,?)"#.format(auth_dic["id"],auth_dic["name"])
            res = db.execute(auth_query,params=(auth_dic["id"],auth_dic["name"]))
        tag_dic = data["categories"]
        #problem: fixed, but handle more elegantly with regex
        #build docs to tags query
        tag_keys_string = ( ",".join(tag_dic.keys()) ).replace(" ","_").replace("-","_").replace("2","")
        question_marks = ("?,"* len(tag_dic.keys())).rstrip(",")
        tag_query = "INSERT INTO DocumentToTags (docfimficID,{}) VALUES({id},{});".format(tag_keys_string, question_marks, id =fimficID)
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
def convert_epubs(epub_folder,output_folder):
    os.mkdir(output_folder)
    db = WebDB.WebDB("data.db")
    list_of_ids = db.get_all_docIDs()
    for id in list_of_ids:
        infile = epub_folder + db.get_any_by_doc_ID("path",id)
        outfile = output_folder+"\\"+str(id)+".txt"
        print("converting "+infile)
        epub_to_txt(infile,outfile)
def main():
    if not os.path.isfile("data.db"):
        populate_DB("test_data.json", "data.db")
    else:
        if not os.path.isdir("raw_texts"):
            epub_directory = "C:\\Users\samka\Downloads\misc documents\\fimfarchive-20151125\\"
            convert_epubs(epub_directory,"raw_texts")
main()