import csv
import urllib.parse as url
import urllib3
import xml.etree.ElementTree as ET
import time
import os
import logging

MAX_LINES = 2000

http = urllib3.PoolManager()

compoundRestURL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
compoundURL = "https://pubchem.ncbi.nlm.nih.gov/compound/"
compoundViewURL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/"
datafile = "./data/COSING_Ingredients-Fragrance Inventory_v2-ROWS ONLY.csv"
NAME_COL = 1
debugFile = "debug.log"
errorFile = "errors.log"
outputFile = "results.txt"

foundCosIngs = []
notFoundCosIngs = []
toxicityCosIngs = []
therapeuticCosIngs = []
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

def getCid(cname):
    searchURL = compoundRestURL + "name/" + url.quote(cname) + "/XML"
    results = http.request("GET", searchURL)
    if results.status == 200:
        doc = ET.fromstring(results.data)
        cid = doc.find(".//{http://www.ncbi.nlm.nih.gov}PC-CompoundType_id_cid")
        return int(cid.text)
    else:
        return -1

def searchPubChemForCosIng():
    print("Searching PubChem for Cosmetic Ingredients...")
    with open(datafile, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        lines = -1
        for row in reader:
            lines += 1
            if lines >= MAX_LINES: 
                break
            elif lines == 0:
                continue
            # print(str(lines) + ":: " + ", ".join(row))
            cname = row[NAME_COL]
            cid = getCid(cname)
            if cid > 0:
                foundCosIngs.append((cid, cname, compoundURL + str(cid)))
                print("Compound Found [" + str(len(foundCosIngs)) + "]")
            else:
                notFoundCosIngs.append((lines, cname))
                logging.info("Ingredient not found on PubChem: %s, line %d", cname, lines)
        
def hasToxicityInfo(doc):
    heading = doc.find(".//{http://pubchem.ncbi.nlm.nih.gov/pug_view}TOCHeading[.='Toxicity']")
    return heading != None

def hasTherapeuticUse(doc):
    heading = doc.find(".//{http://pubchem.ncbi.nlm.nih.gov/pug_view}TOCHeading[.='Therapeutic Uses']")
    return heading != None


setupLogging()
searchPubChemForCosIng()

print("Checking Compounds for Toxicity Information...")
for compound in foundCosIngs:
    # print(str(compound[0]) + ", " + compound[1] + ", " + compound[2])
    searchURL = compoundViewURL + str(compound[0]) + "/XML"
    results = http.request("GET", searchURL)
    if results.status == 200:
        try:
            doc = ET.fromstring(results.data)
            if hasToxicityInfo(doc):
                toxicityCosIngs.append(compound)
                print("Toxicity Found [" + str(len(toxicityCosIngs)) + "]")
            if hasTherapeuticUse(doc):
                therapeuticCosIngs.append(compound)
                print("Therapeutic Uses Found [" + str(len(therapeuticCosIngs)) + "]")
        except ET.ParseError as perr:
            logging.error("Unable to parse PubChem view for compound cid %d - %s\n %s", compound[0], compound[1], perr.msg)
    else:
        logging.error("Failed to GET PUG View: " + str(results.status) + " for CID " + str(compound[0]))

totaltime = time.time() - starttime
totalmins = int(totaltime / 60)

if os.path.exists(outputFile):
    os.remove(outputFile)

with open(outputFile, "w") as out:
    out.write("Cosmetic Ingredients Searched: %d\n" % MAX_LINES)
    out.write("Compounds found on PubChem: %d\n" % len(foundCosIngs))
    out.write("Compounds with Toxicity Information: %d\n" % len(toxicityCosIngs))
    out.write("Compounds with Therapeutic Uses: %d\n" % len(therapeuticCosIngs))
    # out.writelines(therapeuticCosIngs) # TypeError: write() argument must be str, not tuple
    for compound in therapeuticCosIngs:
        out.write(" CID [ %d ] %s ( %s )\n" % (compound[0], compound[1], compound[2]))

print("Execution completed in %dm%ds. See %s for the final data." % (totalmins, totaltime % 60, outputFile))