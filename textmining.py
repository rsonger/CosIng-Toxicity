import os
import nltk
import logging
from nltk import text

from nltk.probability import FreqDist

nltk.download('punkt')
nltk.download('stopwords')
sentence_detector = nltk.data.load("tokenizers/punkt/english.pickle")

skin_words = ["skin","dermal","epidermis"]
mystopwords = [".", ",", "(", ")","side","water","bee","target","due","life","%"]
TOP_WORDS = 10

abstractsFolder = "./abstracts/"
outputFile = "./data/Pubmed_abstracts-cosing+toxicity+skin.csv"
csvheaders = "Compound Name, Abstract ID, CName Frequency, Skin Freq, Compound-Skin Collocations"
CNAME_COL = 0
ABSID_COL = 1
CNAME_FREQ_COL = 2
SKIN_FREQ_COL = 3
COLLOCATIONS_COL = 4

debugFile = "textmining-debug.log"
errorFile = "textmining-error.log"

def setupLogging():
    if os.path.exists(debugFile):
        os.remove(debugFile)
    if os.path.exists(errorFile):
        os.remove(errorFile)
    logging.basicConfig(filename=debugFile,level=logging.DEBUG)
    errors = logging.FileHandler(filename=errorFile)
    errors.setLevel(logging.ERROR)
    errors.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.getLogger("").addHandler(errors)

# searches the root folder for TXT files and returns a list of tuples
# each tuple is (abstract ID, full abstract text, tokenized sentences list)
def tokenizeAllAbstracts(root):
    abstractWords = []
    for f in os.listdir(root):
        filename, fileext = os.path.splitext(f)
        if fileext == ".txt":
            abstractFile = open(root + "/" + f)
            abstractText = abstractFile.read()
            # words = nltk.word_tokenize(abstractFile.read())
            # words = [w.lower() for w in words]
            sentences = sentence_detector.tokenize(abstractText.strip())
            abstractWords.append((filename, abstractText, sentences))
    return abstractWords

def countCompoundName(cname, text):
    return text.lower().count(cname.lower())

def countSkinWords(text):
    count = 0
    text = text.lower()
    for w in skin_words:
        count += text.count(w)
    return count

def getSkinAndCNameCollocations(cname, sentences):
    collocations = 0
    for sent in sentences:
        sent = sent.lower()
        skin_found = False
        for w in skin_words:
            if sent.find(w) > -1:
                skin_found = True
                break
        if skin_found and sent.find(cname.lower()) > -1:
            collocations += 1
    
    return collocations / len(sentences)

setupLogging()

outputlist = []

for f in os.listdir(abstractsFolder):
    abstracttokens = tokenizeAllAbstracts(abstractsFolder + "/" + f)
    for abstract in abstracttokens:
        abstext = abstract[1]
        row = []
        row.insert(CNAME_COL, f)
        row.insert(ABSID_COL, abstract[0])
        row.insert(CNAME_FREQ_COL, countCompoundName(f, abstext))
        row.insert(SKIN_FREQ_COL, countSkinWords(abstext))
        row.insert(COLLOCATIONS_COL, getSkinAndCNameCollocations(f, abstract[2]))

        outputlist.append(row)

with open(outputFile, "w") as out:
    out.write(csvheaders + "\n")
    for r in outputlist:
        out.write(','.join(str(v) for v in r) + "\n")