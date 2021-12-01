
#required packages
import sqlite3
import spacy
import lemminflect
from nltk.corpus import wordnet as wn
from collections import Counter
from string import punctuation
import pandas as pd
nlp = spacy.load('en_core_web_lg')
import re


'''
@param: term: the word which needs it's thesaurus set.
output: the input word's thesaurus set in str format, each term is separated by ";"
'''
def fetch_syns(term):
    con = sqlite3.connect("thesaurus.sqlite")
    df = pd.read_sql(('select "synonyms" from "thesaurus_terms" '
                     'where "word" =:term'),
                   con,params={"term":term})
    con.close()
    busket=[]
    for i in df['synonyms']:
        i=i[1:-1].split(",")
        for term in i:
            busket.append(term[1:-1])
    busket=list(dict.fromkeys(busket))
    return busket


'''
@param: term_group: a list of terms, each of them needs a thesaurus set
output: the input word group's thesaurus set in str format, each term is separated by ";"
'''

def get_syns_set(term_group):
    busket=[]
    for i in term_group:
        bkt=fetch_syns(i)
        for word in bkt:
            busket.append(word)
    busket=list(dict.fromkeys(busket))
    return busket

def generate_csv_output(df):
    df = df.astype(object).fillna(" ")
    for i in range(df.shape[0]):
        hot_v_dic = get_hotwords(df.loc[i, "Description"])
        df.loc[i,"nouns - MUST INCLUDE"]='; '.join(str(item) for item in hot_v_dic["NOUN"])
        df.loc[i, "nouns - Syns"] = get_syns_set(hot_v_dic["NOUN"])
        df.loc[i, "verbs - MUST INCLUDE"] = '; '.join(str(item) for item in hot_v_dic["VERB"])
        df.loc[i, "verbs - Syns"] = get_syns_set(hot_v_dic["VERB"])
    s=df.to_html()
    s=s.replace("<td>","<td contentEditable=\"true\">")
    s = s + "\n <br>\n <br> \n <button>Export to CSV </button>"
    template = """
<!DOCTYPE html>    
<html>
    <head>
    <title>CSV download</title>
    </head>
    <body>
    {}
    <a href="{{ url_for('download', filename="RDAwSyns.csv") }}">File</a>
    </body>
</html>
    """
    s=template.format(s)
    return s


def get_inflects_p(phrase):
    term=" ".join([token.lemma_ for token in nlp(phrase[-1])])
    #term=phrase[-1]
    rtn=[]
    s=lemminflect.getAllInflections(term, upos="NOUN")
    a=list(s.values())
    result = list(dict.fromkeys([x for t in a for x in t]))
    phrase_start=" ".join(str(item) for item in phrase[:-1])
    for i in result:
        rtn.append(phrase_start+" "+i)
    return rtn

def get_inflects(term):
    s=lemminflect.getAllInflections(term, upos=None)
    a=list(s.values())
    result = [x for t in a for x in t]
    return list(dict.fromkeys(result))

def deal_with_input(string):
    sets = string.split(";")
    words = []
    for i in sets:
        ls=[]
        if i.startswith(" "):
            ls=i[1:].split(" ")
        else:
            ls=i.split(" ")
        if len(ls)>1:
            words.append(' '.join(str(item) for item in ls if str(item) != ""))
        else:
            words.append(ls[0])
    return words


def inflect_generator (string):
    sets= string.split(", ")
    words=[]
    result=[]
    for i in sets:
        ls=[]
        if i.startswith(" "):
            ls=i[1:].split(" ")
        else:
            ls=i.split(" ")
        if len(ls)>1:
            words.append(ls)
        else:
            words.append(ls[0])
    print(words)
    for things in words:
        rs=""
        if isinstance(things, str):
            rs='; '.join(str(item) for item in list(dict.fromkeys(get_inflects(things))) )
        else:
            rs='; '.join(str(item) for item in list(dict.fromkeys(get_inflects_p(things))))
        result.append(rs)

    return '; '.join(str(item) for item in result if item != "")
