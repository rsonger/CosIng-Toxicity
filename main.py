import csv
import urllib.parse as url
import urllib3
import xml.etree.ElementTree as ET
import time

urllib3.disable_warnings()
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
therapeuticCosIngs = []

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
                notFoundCosIngs.append((cid, cname))

            # time.sleep(0.3)
        
def hasToxicityInfo(doc):
    heading = doc.find(".//{http://pubchem.ncbi.nlm.nih.gov/pug_view}TOCHeading[.='Toxicity']")
    return heading != None

def hasTherapeuticUse(doc):
    heading = doc.find(".//{http://pubchem.ncbi.nlm.nih.gov/pug_view}TOCHeading[.='Therapeutic Uses']")
    return heading != None


searchPubChemForCosIng()

print("Checking Compounds for Toxicity Information...")
for compound in foundCosIngs:
    # print(str(compound[0]) + ", " + compound[1] + ", " + compound[2])
    searchURL = compoundViewURL + str(compound[0]) + "/XML"
    results = http.request("GET", searchURL)
    if results.status == 200:
        doc = ET.fromstring(results.data)
        if hasToxicityInfo(doc):
            toxicityCosIngs.append(compound)
            print("Toxicity Found [" + str(len(toxicityCosIngs)) + "]")
        if hasTherapeuticUse(doc):
            therapeuticCosIngs.append(compound)
            print("Therapeutic Uses Found [" + str(len(therapeuticCosIngs)) + "]")
    else:
        print("PUG View GET failed: " + str(results.status) + " for cid " + str(cid))


print("Cosmetic Ingredients Searched: " + str(MAX_LINES))
print("Compounds found on PubChem: " + str(len(foundCosIngs)))
print("Compounds with Toxicity Information: " + str(len(toxicityCosIngs)))
print("Compounds with Therapeutic Uses: " + str(len(therapeuticCosIngs)))
print("Execution complete.")