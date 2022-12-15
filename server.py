from flask import Flask, request, jsonify
from threading import Thread
import time
import secrets
import random
from flask_cors import CORS, cross_origin

app = Flask('')

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def main():
    return "under construction"

allLetters = "ABDEFGHIJKLMNOPRSTUVYÄÖ"
weights = (
    19, #A
    5,  #B
    5,  #D
    18, #E
    6,  #F
    8,  #G
    17,  #H
    20,  #I
    19,  #J
    19,  #K
    18,  #L
    19,  #M
    19,  #N
    19,  #O
    17,  #P
    18,  #R
    19,  #S
    19,  #T
    19,  #U
    14,  #V
    3,  #Y
    14,  #Ä
    14,  #Ö

)
def returnNewGrid():
    new = {}
    for row in range(1, 14, 1):
        columnVal = {}
        for column in range(1, 11, 1):
            columnVal[str(column) + "col"] = random.choices(allLetters, weights=weights)
        new[str(row) + "row"] = columnVal
    return new


playersInServer = 0
playerSecrets = []
map = {}
currentTurn = 1
playerHasVoted = [False, False] #index 0 indicates if player voted, index 1 indicates the value of the vote
currentWord = ""
currentWordData = []

@app.route('/getserverstatus', methods=['GET'])
@cross_origin()
def getserverstatus():
    global playerSecrets
    global playersInServer
    if playersInServer == 0:
        playersInServer = 1
        Psecret = str(secrets.token_hex(32))
        playerSecrets.append(Psecret)
    elif playersInServer == 1:
        playersInServer = 2
        Psecret = str(secrets.token_hex(32))
        playerSecrets.append(Psecret)
    else:
        returnData = {"result" : "-1", "error":"Already 2 players in server."}
        return jsonify(returnData)

    print("New player. Secret: " + Psecret)
    returnData = {"result" : "0", "secret": Psecret, "player": str(playersInServer)}
    return jsonify(returnData)
    
@app.route('/getgamedata', methods=['GET'])
@cross_origin()
def getGameData():
    global map
    if request.headers['secret'] == playerSecrets[0]:
        player = 1
    elif request.headers['secret'] == playerSecrets[1]:
        player = 2
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})
    if map == {}:
        map = returnNewGrid()
    while playersInServer != 2:
        time.sleep(0.1)
    return jsonify({"result" : "0", "data": map})

@app.route('/ping', methods=['GET'])
@cross_origin()
def ping():
    return jsonify({"result": "1"})

@app.route('/postword', methods=['POST'])
@cross_origin()
def postword():
    global playerHasVoted
    global currentWord
    global currentTurn
    global currentWordData
    if (request.headers['player'] != str(currentTurn)):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == playerSecrets[0]:
        currentWord = request.json['word']
        currentWordData = request.json['worddata']
        while playerHasVoted[0] == False:
            time.sleep(0.1)
        playerHasVoted[0] = False
        if currentTurn == 1: currentTurn = 2 
        else: currentTurn = 1
        return jsonify({"result":"0", "answer": playerHasVoted[1]})
    elif request.headers['player'] == "2" and request.headers['secret'] == playerSecrets[1]:
        currentWord = request.json['word']
        currentWordData = request.json['worddata']
        while playerHasVoted[0] == False:
            time.sleep(0.1)
        playerHasVoted[0] = False
        if currentTurn == 1: currentTurn = 2 
        else: currentTurn = 1
        return jsonify({"result":"0", "answer": playerHasVoted[1]})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

@app.route('/getnewword', methods=['GET'])
@cross_origin()
def getnewword():
    global currentWord
    if (request.headers['player'] == str(currentTurn)):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == playerSecrets[0]:
        while currentWord == "":
            time.sleep(0.1)
        word = currentWord
        currentWord = ""
        return jsonify({"result":"0", "word": word, "data":currentWordData})
    elif request.headers['player'] == "2" and request.headers['secret'] == playerSecrets[1]:
        while currentWord == "":
            time.sleep(0.1)
        word = currentWord
        currentWord = ""
        return jsonify({"result":"0", "word": word, "data":currentWordData})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

@app.route('/approveword', methods=['POST'])
@cross_origin()
def approveword():
    global playerHasVoted
    if (request.headers['player'] == str(currentTurn)):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == playerSecrets[0]:
        if request.json['result'] == "true":
            playerHasVoted[1] = True
        else:
            playerHasVoted[1] = False
        playerHasVoted[0] = True
        return jsonify({"result":"0"})
    elif request.headers['player'] == "2" and request.headers['secret'] == playerSecrets[1]:
        if request.json['result'] == "true":
            playerHasVoted[1] = True
        else:
            playerHasVoted[1] = False
        playerHasVoted[0] = True
        return jsonify({"result":"0"})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})
    

def run():
    app.run(host="0.0.0.0", port=8080, threaded=True)


def keep_alive():
    server = Thread(target=run)
    server.start()


keep_alive()

print("SERVER STARTED")