import csv
import urllib3
import xml.etree.ElementTree as ET
import time

http = urllib3.PoolManager()
compoundRestURL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
compoundURL = "https://pubchem.ncbi.nlm.nih.gov/compound/"
compoundViewURL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/"
datafile = "./data/COSING_Ingredients-Fragrance Inventory_v2-ROWS ONLY.csv"
NAME_COL = 1
MAX_LINES = 100

foundCosIngs = []
notFoundCosIngs = []
toxicityCosIngs = []

def getCid(cname):
    searchURL = compoundRestURL + "name/" + cname + "/XML"
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
                notFoundCosIngs.append((cid, cname))

            time.sleep(0.3)
        
def hasToxicityInfo(cid):
    searchURL = compoundViewURL + str(cid) + "/XML"
    results = http.request("GET", searchURL)
    if results.status == 200:
        doc = ET.fromstring(results.data)
        heading = doc.find(".//{http://pubchem.ncbi.nlm.nih.gov/pug_view}TOCHeading[.='Toxicity']")
        if heading != None:
            return True
        else:
            return False
    else:
        print("PUG View GET failed: " + str(results.status) + " for cid " + str(cid))
        return False

searchPubChemForCosIng()

print("Checking Compounds for Toxicity Information...")
for compound in foundCosIngs:
    # print(str(compound[0]) + ", " + compound[1] + ", " + compound[2])
    if hasToxicityInfo(compound[0]):
        toxicityCosIngs.append(compound)
        print("Toxicity Found [" + str(len(toxicityCosIngs)) + "]")

print("Cosmetic Ingredients Searched: " + str(MAX_LINES))
print("Compounds found on PubChem: " + str(len(foundCosIngs)))
print("Compounds with Toxicity Information: " + str(len(toxicityCosIngs)))
print("Execution complete.")