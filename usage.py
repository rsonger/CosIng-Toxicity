import csv
import urllib3
import xml.etree.ElementTree as ET
import time
import os
import logging

csvOutput = True
outputFile = "usage-results.txt"
if csvOutput:
    outputFile = "./data/CosIngs_list-toxic+therapeutic+cosmetic.csv"
debugFile = "usage-debug.log"
errorFile = "usage-error.log"
dataFile = "./data/CosIngs_list-toxicity+therapeutic_uses.csv"
compoundURL = "https://pubchem.ncbi.nlm.nih.gov/compound/"
compoundViewURL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/"

CID_COL = 0
NAME_COL = 1
URL_COL = 2

foundCosIngs = []
foundCosUses = []
foundNoCosUses = []

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()
namespaces = {"PC": "http://pubchem.ncbi.nlm.nih.gov/pug_view"}

starttime = time.time()

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

def loadCosIngs():
    print("Loading Cosmetic Ingredients with Toxicity + Therapeutic Uses...")
    with open(dataFile, "r") as csvfile:
        readlines = 0
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            readlines += 1
            try:
                cname = str(row[NAME_COL])
                cid = int(row[CID_COL])
                foundCosIngs.append((cid, cname, compoundURL + str(cid)))
            except:
                logging.error("Unable to read record line %d", readlines)

def getCosmeticUses(doc):
    uses = []
    classStrings = doc.findall(".//PC:TOCHeading[.='Use Classification']/../PC:Information/PC:Value/PC:StringWithMarkup/PC:String",
                              namespaces)
    usesStrings = doc.findall(".//PC:TOCHeading[.='Uses']/../PC:Information/PC:Value/PC:StringWithMarkup/PC:String",
                              namespaces)
    infoStrings = classStrings + usesStrings
    for info in infoStrings:
        if info.text.find("cosmetic") > -1 or info.text.find("Cosmetic") > -1:
            uses.append(info.text)
    return uses

setupLogging()
loadCosIngs()

# TEST to find cosmetic usage from XML view data:
# https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/176
# https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/5281224
# foundCosIngs.append((176, "Acetic acid", compoundURL + "176"))
# foundCosIngs.append((5281224, "Astaxanthin", compoundURL + "5281224"))

print("Checking PubChem Compounds for Cosmetic Uses...")
for compound in foundCosIngs:
    searchURL = compoundViewURL + str(compound[CID_COL]) + "/XML"
    results = http.request("GET", searchURL)
    if results.status == 200:
        uses = []
        print("Compound view data downloaded [CID: %d]" % compound[CID_COL])
        try:
            doc = ET.fromstring(results.data)
            uses = getCosmeticUses(doc)
        except ET.ParseError as perr:
            logging.error("Unable to parse PubChem view for compound cid %d - %s\n %s" % (compound[0], compound[1], perr.msg))

        if len(uses) > 0:
            foundCosUses.append((compound,uses))
        else:
            foundNoCosUses.append((compound,"None"))
    else:
        logging.error("Failed to GET PUG View: %d status on CID %d" % (results.status, compound[0]))

totaltime = time.time() - starttime
totalmins = int(totaltime / 60)

if os.path.exists(outputFile):
    os.remove(outputFile)

with open(outputFile, "w") as out:
    if csvOutput:
        out.write("Compound ID,Compound Name,PubChem URL\n")
        for cosUse in foundCosUses:
            comp = cosUse[0]
            out.write("%d,%s,%s\n" % (comp[CID_COL],comp[NAME_COL],comp[URL_COL]))
    else:
        out.write("Cosmetic Ingredients Searched: %d\n" % len(foundCosIngs))
        out.write("Compounds with Cosmetic Uses: %d\n" % len(foundCosUses))
        for compUses in foundCosUses:
            comp = compUses[0]
            out.write(" [CID: %d] %s ( %s )\n" % (comp[CID_COL], comp[NAME_COL], comp[URL_COL]))
            for use in compUses[1]:
                out.write("   %s\n" % use)
        for noCosUses in foundNoCosUses:
            comp = noCosUses[0]
            out.write(" [CID: %d] %s ( %s )\n" % (comp[CID_COL], comp[NAME_COL], comp[URL_COL]))
            out.write("   %s\n" % noCosUses[1])

print("Execution completed in %dm%ds. See %s for the final data." % (totalmins, totaltime % 60, outputFile))