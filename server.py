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

allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"
def returnNewGrid():
    new = {}
    for row in range(1, 14, 1):
        columnVal = {}
        for column in range(1, 11, 1):
            columnVal["col" + str(column)] = random.choice(allLetters)
        new["row" + str(row)] = columnVal
    return new


playersInServer = 0
playerSecrets = []
@app.route('/getserverstatus', methods=['GET'])
@cross_origin()
def getserverstatus():
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
    if request.headers['secret'] == playerSecrets[0]:
        player = 1
    elif request.headers['secret'] == playerSecrets[1]:
        player = 2
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})
    while playersInServer != 2:
        time.sleep(0.1)


def run():
    app.run(host="0.0.0.0", port=8080, threaded=True)


def keep_alive():
    server = Thread(target=run)
    server.start()


keep_alive()