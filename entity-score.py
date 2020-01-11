import glob
import pathlib
from rdflib import URIRef, Literal, BNode, Graph
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
TMP = Namespace("http://purl.bdrc.io/ontology/tmp/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")

NSM = NamespaceManager(Graph())
NSM.bind("bdr", BDR)
NSM.bind("bdo", BDO)
NSM.bind("tmp", TMP)
NSM.bind("bda", BDA)
NSM.bind("adm", ADM)
NSM.bind("skos", SKOS)
NSM.bind("rdfs", RDFS)


GITDIRS = "../xmltoldmigration/tbrc-ttl/"

ENTITIES = {}

def get_all_type(basedir, typeT):
    i = 0
    global ENTITIES
    print("walk ", basedir)
    for trig_file in pathlib.Path(basedir).glob('*/*.trig'):
        i += 1
        if i > 4:
            return
        model = Graph()
        model.parse(str(trig_file), format="trig")
        print(model)
        print(model.serialize(format='trig'))
        main = BDR[trig_file.stem]
        if main not in ENTITIES:
            ENTITIES[main] = {"type": typeT}
        if (typeT == "work"):
            nb_instances = 0
            for s, p, o in model.triples((None, None, None)):
                print("toto")
            for s,p,o in model.triples( (None,  BDO.workHasInstance, None) ):
                print("test")
                nb_instances += 1
            ENTITIES[main]["nbInstances"] = nb_instances
            for s,p,o in model.triples( (None,  BDO.workHasTranslation, None) ):
                if "translations" not in ENTITIES[s]:
                    ENTITIES[s]["translations"] = []
                ENTITIES[s]["translations"].append(o)
                if o not in ENTITIES:
                    ENTITIES[o] = {}
                if "translationOf" not in ENTITIES[o]:
                    ENTITIES[o]["translations"] = []
                ENTITIES[o]["translations"].append(s)
            for e,p,person in model.triples( (None,  BDO.agent, None) ):
                for e,ep,role in model.triples( (e,  BDO.role, None) ):
                    for r,rp,e in model.triples( (None,  BDO.workEvent, e) ):
                        # R0ER0011 = attributed author
                        # R0ER0014 = commentator
                        # R0ER0016 = contributing author
                        # R0ER0017 = head translator
                        # R0ER0018 = Source Language Scholar
                        # R0ER0019 = main author
                        # R0ER0025 = terton
                        # R0ER0026 = translator
                        rgroup = "group4"
                        if role == BDR.R0ER0025 or role == R0ER0011 or role == R0ER0019:
                            rgroup = "group1"
                        elif role == BDR.R0ER0014:
                            rgroup = "group2"
                        elif role == BDR.R0ER0017 or role == BDR.R0ER0018 or BDR.R0ER0026:
                            rgroup = "group3"
                        if person not in ENTITIES:
                            ENTITIES[person] = {}
                        if rgroup not in ENTITIES[person]:
                            ENTITIES[person][rgroup] = []
                        ENTITIES[person][rgroup].append(r)
            for s,p,o in model.triples( (None,  BDO.workIsAbout, None) ):
                if o not in ENTITIES:
                    ENTITIES[o] = {"nbAbout": 0}
                ENTITIES[o]["nbAbout"] += 1
        for s,p,o in model.triples( (None,  None, None) ):
            if p == BDO.eventWhere or p == BDO.eventWho or p == BDO.placeLocatedIn or p == instanceHasSourcePrintery:
                if o not in ENTITIES:
                    ENTITIES[o] = {"nbRefs": 0}
                ENTITIES[o]["nbRefs"] += 1

GROUP_FACTORS = {
    "group1": 6,
    "group2": 4,
    "group3": 2,
    "group4": 1
}

def main():
    global ENTITIES
    get_all_type(GITDIRS+"works/", "work")
    print(ENTITIES)
    # we need to make a few passes, first works:
    for einfo in ENTITIES.values():
        if einfo["type"] != "work":
            continue
        selfscore = 0
        if "nbInstances" in einfo:
            selfscore += einfo["nbInstances"]
        if "nbRefs" in einfo:
            selfscore += einfo["nbRefs"]
        if "nbAbout" in einfo:
            selfscore += einfo["nbAbout"]*2
        if "translations" in einfo:
            selfscore += len(einfo["translations"])
            for t in einfo["translations"]:
                te = ENTITIES[t]
                if "selfscore" not in te:
                    te["selfscore"] = 0
                te["selfscore"] += selfscore
        if "translationOf" in einfo:
            for t in einfo["translationOf"]:
                te = ENTITIES[t]
                if "selfscore" not in te:
                    te["selfscore"] = 0
                te["selfscore"] += selfscore
        einfo["selfscore"] = selfscore
    get_all_type(GITDIRS+"places/", "place")
    get_all_type(GITDIRS+"persons/", "person")
    for einfo in ENTITIES.values():
        if einfo["type"] == "work":
            continue
        selfscore = 0
        if "selfscore" in einfo:
            selfscore = einfo["selfscore"]
        else:
            if "nbRefs" in einfo:
                selfscore += einfo["nbRefs"]
            if "nbAbout" in einfo:
                selfscore += einfo["nbAbout"]*2
        for gname, gfactor in GROUP_FACTORS.items():
            if gname in einfo:
                for workR in einfo[gname]:
                    work = ENTITIES[workR]
                    if "selfscore" in work:
                        selfscore += work["selfscore"]*gfactor
    g = Graph()
    g.bind("bdr", BDR)
    g.bind("tmp", TMP)
    for e, einfo in ENTITIES.items():
        selfscore = einfo["selfscore"] if "selfscore" in einfo else 0
        g.add((e, TMP.entityScore, Literal(selfscore)))
    g.serialize("entityScores.ttl", format="turtle")

if __name__ == "__main__":
    main()