import random
weights = (
    27,  #A
    2,   #B
    0,   #C
    2,   #D
    24,  #E
    2,   #F
    4,   #G
    17,  #H
    26,  #I
    19,  #J
    19,  #K
    18,  #L
    19,  #M
    19,  #N
    24,  #O
    17,  #P
    0,   #Q
    18,  #R
    19,  #S
    20,  #T
    24,  #U
    14,  #V
    0,   #W
    0,   #X
    1,   #Y
    0,   #Z
    0,   #Å
    6,  #Ä
    5,  #Ö
)
allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"
vocals = ["A", "E", "I", "O", "U", "Y", "Å", "Ä", "Ö"]
consonants = ["B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "X", "Z"]
width = 10
height = 13
map = []
for y in range(0, height, 1):
    thisRow = []
    for x in range(0, width, 1):
        thisRow.append(random.choices(allLetters, weights=weights))
    map.append(thisRow)

def CalcHeatMap(map):
    most = [0, 0]
    calculated = 0
    for x in range(0, width, 1):
        for y in range(0, height, 1):
            if map[y][x][0] not in vocals:
                calculated += 1
                most[0] += x
                most[1] += y
    most[0] = most[0] / calculated
    most[1] = most[1] / calculated
    return most


def getStringFromMap(map):
    string = ""
    for i in range(0, len(map), 1):
        for f in range(0, width, 1):
            string += "[" + map[i][f][0] + "]"
        string += "\n"
    return string
def SafeAddHeight(original, amount):
    newAmt = original + amount
    if newAmt <= 0:
        newAmt = 1
    elif newAmt >= height:
        newAmt = height - 1
    return newAmt
def SafeAddWidth(original, amount):
    newAmt = original + amount
    if newAmt <= 0:
        newAmt = 1
    elif newAmt >= width:
        newAmt = width - 1
    return newAmt

def breakConsonants(map):
    for x in range(0, width, 1):
        for y in range(0, height, 1):
            if map[y][x][0] not in vocals:
                if map[SafeAddHeight(y, -1)][x][0] not in vocals and map[SafeAddHeight(y, 1)][x][0] not in vocals and map[y][SafeAddWidth(y, -1)][0] not in vocals and map[y][SafeAddWidth(y, 1)][0] not in vocals:
                    map[y][x] = random.choices(vocals, weights=vocalWeights)

    return map
def breakVocals(map):
    for x in range(0, width, 1):
        for y in range(0, height, 1):
            if map[y][x][0] not in vocals:
                if (map[SafeAddHeight(y, -1)][x][0] not in consonants and map[SafeAddHeight(y, 1)][x][0] not in consonants) or (map[y][SafeAddWidth(y, -1)][0] not in consonants and map[y][SafeAddWidth(y, 1)][0] not in consonants):
                    map[y][x] = random.choices(consonants, weights=consonantWeights)

    return map
def ParseWeights():
    vocalWeights = []
    consonantWeights = []
    for i in range(0, len(weights), 1):
        if allLetters[i] in vocals:
            vocalWeights.append(weights[i])
        elif allLetters[i] in consonants:
            consonantWeights.append(weights[i])
        else:
            print("Warning: Invalid alphabet")
    return [vocalWeights, consonantWeights]
def ListToDict(map):
    new = {}
    for row in range(0, height, 1):
        columnVal = {}
        for column in range(0, width, 1):
            columnVal[str(column) + "col"] = map[row][column][0]
        new[str(row) + "row"] = columnVal
    return new
def RemoveSameTiles(map):
    for x in range(0, width, 1):
        for y in range(0, height, 1):
            if map[y][SafeAddWidth(x, 1)][0] == map[y][x][0] and map[y][SafeAddWidth(x, -1)][0] == map[y][x][0]:
                if map[y][x][0] in consonants:
                    map[y][x] = random.choices(vocals, weights=vocalWeights)
                    print("yes")
                else:
                    print("nope")
                    map[y][x] = random.choices(consonants, weights=consonantWeights)
            elif map[SafeAddHeight(y, 1)][x][0] == map[y][x][0] and map[SafeAddHeight(y, -1)][x][0] == map[y][x][0]:
                if map[y][x][0] in consonants:
                    map[y][x] = random.choices(vocals, weights=vocalWeights)
                else:
                    map[y][x] = random.choices(consonants, weights=consonantWeights)
    return map

w = ParseWeights()
vocalWeights = tuple(w[0])
consonantWeights = tuple(w[1])
map = breakConsonants(map)
map = breakVocals(map)
heat = CalcHeatMap(map)
heat[0] = int(heat[0])
heat[1] = int(heat[1])
map[heat[1]][heat[0]][0] = "*"
map = RemoveSameTiles(map)
print(map[0][0])
print(map[0][0][0])
#print(ListToDict(map))
print(getStringFromMap(map))