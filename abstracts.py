import csv
import os
import xml.dom.minidom as minidom
import urllib.parse as url
import urllib3
import logging
import time
# import nltk

abstractsFolder = "./abstracts/"
searchResultsFile = "search.xml"

searchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=&retmax=%d&term=%s"
searchTerms = '"%s""adverse effect""skin"'
queryURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=PubMed&retmode=xml&ID="

cosmeticUsesFile = "./data/CosIngs_list-toxic+therapeutic+cosmetic.csv"
CID_COL = 0
NAME_COL = 1
URL_COL = 2

# How many compounds to search from the top of the list
MAX_COMPOUNDS = 10
# How many abstracts to download for each compound
MAX_ABSTRACTS = 10

debugFile = "abstracts-debug.log"
errorFile = "abstracts-error.log"

urllib3.disable_warnings(urllib3.exceptions.HTTPWarning)
http = urllib3.PoolManager()

cosIngsList = []

def loadCosmeticIngredients():
	with open(cosmeticUsesFile, "r") as csvfile:
		readlines = 0
		reader = csv.reader(csvfile, delimiter=",")
		for row in reader:
			readlines += 1
			try:
				cname = str(row[NAME_COL])
				cid = int(row[CID_COL])
				cosIngsList.append((cid, cname))
			except:
				logging.error("Unable to read record line %d", readlines)
			finally:
				if readlines > MAX_COMPOUNDS:
					break

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

def searchAbstracts(searchWords, searchURL):
    searchFile = abstractsFolder
    if not os.path.exists(abstractsFolder):
        os.mkdir(abstractsFolder)

    if len(cosIngsList) > 0:
        for compound in cosIngsList:
            searchFile = abstractsFolder + compound[NAME_COL]
            if not os.path.exists(searchFile):
                os.mkdir(searchFile)
            searchFile += "/" + searchResultsFile
            searchTerms = searchWords % compound[NAME_COL]
            searchTerms = url.quote(searchTerms)
            searchString = searchURL % (MAX_ABSTRACTS,searchTerms)

            results = http.request("GET", searchString)
            if results.status == 200:
                resultsfile = open(searchFile, "wb")
                resultsfile.write(results.data)
                resultsfile.close()
                print("Created file %s" % searchFile)
            else:
                logging.error("PubMed search failed for: %s" % compound[NAME_COL])

            time.sleep(0.3)
    else:
        logging.error("No compounds to search. Load compounds before searching abstracts.")

def downloadAbstracts(searchResultFile, root):
    nodeTypeText = 3
    nodeTypeElement = 1

    doc = minidom.parse(searchResultFile)
    idTags = doc.getElementsByTagName("Id")

    for li in idTags:
        id = li.childNodes[0].data

        getURL = queryURL + id
        print("QUERYING: " + getURL)
        result = http.request("GET", getURL)
        doc = minidom.parseString(result.data)
        abstractElems = doc.getElementsByTagName("AbstractText")

        abstracttext = []
        if len(abstractElems) > 0:
            for elem in abstractElems:
                cn = []
                for n in elem.childNodes:
                    if n.nodeType == nodeTypeText:
                        cn.append(n.data)
                    elif n.nodeType == nodeTypeElement:
                        cn.append(n.childNodes[0].data)

                fulltext = ''.join(cn)
                abstracttext.append(fulltext)
        else:
            abstracttext.append("No abstract available")

        savefile = open(root + "/" + id + ".txt", "w+")
        savefile.write('\n'.join(abstracttext))
        savefile.close()

        print("Created abstract file " + id + ".txt")

setupLogging()

print("Loading PubChem Compounds with Cosmetic Uses...")
loadCosmeticIngredients()

print("Searching PubMed for abstracts from loaded compound data...")
searchAbstracts(searchTerms, searchURL)
print("Finished searching abstracts.")

print("Downloading PubMed abstracts from search results...")
abstracts = os.listdir(abstractsFolder)
for compoundDir in abstracts:
    targetDir = abstractsFolder + compoundDir
    downloadAbstracts(targetDir + "/" + searchResultsFile, targetDir)
print("Finished downloading abstracts for %d compounds." % MAX_COMPOUNDS)
