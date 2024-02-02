import csv
from rdflib import URIRef, Literal, BNode, Graph, ConjunctiveGraph
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
TMP = Namespace("http://purl.bdrc.io/ontology/tmp/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")

NSM = NamespaceManager(ConjunctiveGraph())
NSM.bind("bdr", BDR)
NSM.bind("bdo", BDO)
NSM.bind("tmp", TMP)
NSM.bind("bda", BDA)
NSM.bind("adm", ADM)
NSM.bind("skos", SKOS)
NSM.bind("rdfs", RDFS)

FACTORS = {
    "workHasInstance": 3,
    "workHasParallelsIn": 2,
    "agent": 1,
    "workIsAbout": 20,
    "workGenre": 3,
    "eventWhere": 2,
    "eventWho": 2,
    "placeLocatedIn": 3,
    "hasSourcePrintery": 5,
    "personTeacherOf": 4
}

def main():
    scores = {}
    with open("workHasInstance.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            e = row[0]
            if not e.startswith("http://purl.bdrc.io/resource/WA"):
                continue
            elname = e[29:]
            escore = 0 if not elname in scores else scores[elname]
            scores[elname] = escore + int(row[1])*FACTORS["workHasInstance"]
    with open("merged.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            e = row[0]
            if not e.startswith("http://purl.bdrc.io/resource/"):
                continue
            elname = e[29:]
            escore = 0 if not elname in scores else scores[elname]
            if not row[1].startswith("http://purl.bdrc.io/ontology/core/"):
                continue
            prop = row[1][34:]
            if prop not in FACTORS:
                print("%s not in factors!" % prop)
                continue
            scores[elname] = escore + int(row[2])*FACTORS[prop]
    g = Graph()
    g.bind("bdr", BDR)
    g.bind("tmp", TMP)
    for elname, escore in scores.items():
        g.add((BDR[elname], TMP.entityScore, Literal(escore)))
    g.serialize("entityScores.ttl", format="turtle")

if __name__ == "__main__":
    main()