import os
import xml.etree.ElementTree as ET
import numpy as np

module_path = os.path.dirname(__file__)
tree = ET.parse(module_path+'/od_generated.rou.xml')
root = tree.getroot()
trips = root.findall(".//trip")

ODMatrix = {"%02d" % y :{"%02d" % x :0  for x in range(14)}for y in range(14)}
ODFlatValues = {("%02d" % x,"%02d" % y):0 for x in range(14) for y in range(14) if not ( (x==3 and y==10) or (x==10 and y==3) )}

for trip in trips:
    fromTaz = trip.get("fromTaz")
    toTaz = trip.get("toTaz")
    ODMatrix[fromTaz][toTaz] += 1
    if not ( (fromTaz=="03" and toTaz=="10") or (fromTaz=="10" and toTaz=="03") ):
        ODFlatValues[(fromTaz,toTaz)] +=1

keys = [str(x) for x in list(ODFlatValues.keys())]



def randomize():
    randomized = np.array(list(ODFlatValues.values())) * np.random.rand(len(ODFlatValues.values()))
    #randomized = np.random.rand(len(ODFlatValues.values()))
    probs = randomized / np.sum(randomized)

    for trip in trips:
        fromTaz = trip.get("fromTaz")
        toTaz = trip.get("toTaz")
        if not ( (fromTaz=="03" and toTaz=="10") or (fromTaz=="10" and toTaz=="03") ):
            od = eval(np.random.choice(keys, p=probs))
            trip.set("fromTaz",od[0])
            trip.set("toTaz",od[1])

    tree.write(open(module_path+'/od_randomized.rou.xml', 'wb'))
