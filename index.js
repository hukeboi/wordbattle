//TODO:
// - make the opponent client reflect new changes (words)
// - update valid tile check (it breaks after first turn)
// - reset the "word" after each turn

async function fetchAsync(url, headers, body) {
    if (headers === undefined){
        var response = await fetch(url);
    } else if (body === undefined){
        var response = await fetch(url, {"headers": headers});
    } else {
        var response = await fetch(url, {method:"POST", headers: headers, body: JSON.stringify(body)});
    }
    let data = await response.json();
    return data;
}
function compare( a, b ) {
    if ( parseInt(a[0]) < parseInt(b[0]) ){
      return -1;
    }
    if ( parseInt(a[0]) > parseInt(b[0]) ){
      return 1;
    }
    return 0;
}
  
const url = "https://word-battle-server.hugestudios.repl.co";
let selectedTiles = [];
let word = "";
const selectedColorP1 = "rgb(209, 63, 52)";
const selectedColorP2 = "rgb(33, 82, 217)";
let selectedColor = "rgb(0, 0, 0)"
const UNselectedColor = "white";
let IsMyTurn = false;
let secret;
let player;

//0 = not a valid move, 1 = valid move, 2 = remove tile
function IsValid(allBoxes, row, col){
    if (allBoxes.length === 0){
        if (player === "1"){
            if (row === 1){
                return 1;
            } else {return 0;}
        } else if (player === "2"){
            if (row === 13){
                return 1;
            } else {return 0;}
        } 
    }

    for (let i = 0; i < allBoxes.length; i++){
        if (JSON.stringify(allBoxes[i]) === JSON.stringify([row, col])){
            return 2;
        }
    }

    let lastTile = allBoxes[allBoxes.length - 1];
    if (Math.abs(lastTile[0] - row) === 1 || Math.abs(lastTile[0] - row) === 0 ){
        if (Math.abs(lastTile[1] - col) === 1 || Math.abs(lastTile[1] - col) === 0 ){
            return 1;
        }
    }
    return 0;
}

//returns the arr1 but deletes arr2 values from it
function RemoveFromArray(arr1, arr2){
    let retVal = [];
    if (arr2.length === 1){
        arr2 = arr2[0];
        for (let i = 0; i < arr1.length; i++){
            console.log(JSON.stringify(arr1[i]), JSON.stringify(arr2))
            if (JSON.stringify(arr1[i]) !== JSON.stringify(arr2)){
                retVal.push(arr1[i]);
            }
        }
        return retVal;
    }
    for (let i = 0; i < arr1.length; i++){
        let isValid = true;
        for (let e = 0; e < arr2.length; e++){
            if (JSON.stringify(arr1[i]) === JSON.stringify(arr2[e])){
                isValid = false;
            }
        }
        if (isValid){
            retVal.push(arr1[i]);
        }
    }
    return retVal;
}

function ToggleAllTiles(on){
    for (let x = 1; x <= 13; x++){
        for (let y = 1; y <= 10; y++){
            console.log(x, y)
            if (on){
                document.getElementById(x + ":" + y).classList.remove("noturn");
            } else {
                document.getElementById(x + ":" + y).classList.add("noturn");
            }
            
        }
    }
}


async function GameplayLoop(){
    if (IsMyTurn === false){
        ToggleAllTiles(IsMyTurn);
        const newWord = await fetchAsync(url + "/getnewword", {"secret": secret, "player": player});
        if (newWord.result === "-1") {
            alert(newWord.error)
            return
        }
        let answer = confirm('New word: Do you confirm it? "' + newWord.word + '"')
        if (answer){
            const newWord = await fetchAsync(url + "/approveword", {"secret": secret, "player": player, "content-type":"application/json"}, {"result": "true"});
            if (newWord.result === "-1") {
                alert(newWord.error)
                return
            }
            //TODO: show enemys word
        } else {
            const newWord = await fetchAsync(url + "/approveword", {"secret": secret, "player": player, "content-type":"application/json"}, {"result": "false"});
            if (newWord.result === "-1") {
                alert(newWord.error)
                return
            }
        }
        IsMyTurn = true;
        document.getElementById("sendBtn").style.visibility = "visible";
        ToggleAllTiles(IsMyTurn);
    }
}


async function main(){
    //await fetchAsync(url + "/postword", {'secret': "1234", "content-type":"application/json"}, {'word': "testilol"})
    document.getElementById("placeholderMap").style.display = "none";
    document.getElementById("underBoard").style.display = "inherit";
    

    let ping = await fetch(url + "/ping")
    if (ping.status !== 200){
        alert("Failed to connect to server")
        return
    }

    const startData = await fetchAsync(url + "/getserverstatus")
    if (startData.result === "-1") {
        alert(startData.error)
        return
    }
    if (startData.player === "1"){
        IsMyTurn = true;
        selectedColor = selectedColorP1;
    } else {
        IsMyTurn = false;
        document.getElementById("sendBtn").style.visibility = "hidden";
        selectedColor = selectedColorP2;
    }
    player = startData.player
    secret = startData.secret;
    console.log(startData.player)
    const headers = {'secret': secret}
    const gameData = await fetchAsync(url + "/getgamedata", headers);
    if (gameData.result === "-1") {
        alert(gameData.error)
        return
    }
    for (const [key, value] of Object.entries(gameData.data).sort(compare)) {
        let parent = document.createElement("div");
        parent.className = "letterParent";
        for (const [col, letter] of Object.entries(value).sort(compare)) {
            let letterDiv = document.createElement("div");
            letterDiv.className = "letter";
            let letterChild = document.createElement("p");
            letterChild.className = "letterChild";
            letterChild.innerText = letter;
            letterDiv.appendChild(letterChild)
            parent.appendChild(letterDiv)
            letterDiv.id = parseInt(key) + ":" + parseInt(col)
            letterDiv.addEventListener("click", (click) => {
                if (IsMyTurn === false) {return;}
                if (IsValid(selectedTiles, parseInt(key), parseInt(col)) === 1){
                    if (selectedTiles.length >= 8) {
                        alert("You cant have more than 8 letters.");
                        return;
                    }
                    letterDiv.style.backgroundColor = selectedColor;
                    selectedTiles.push([parseInt(key), parseInt(col)]);
                    if (word === " ") {word = ""}
                    word = word + letterChild.innerText;
                    document.getElementsByClassName("word")[0].innerText = word;
                } else if (IsValid(selectedTiles, parseInt(key), parseInt(col)) === 2){
                    let toRemove = [];
                    for (let i = selectedTiles.length - 1; i >= 0; i--){
                        let LastToRemove = false;
                        if (selectedTiles[i][0] === parseInt(key) && selectedTiles[i][1] === parseInt(col)){
                            LastToRemove = true;
                        }
                        toRemove.push(selectedTiles[i])
                        document.getElementById(selectedTiles[i][0] + ":" + selectedTiles[i][1]).style.backgroundColor = UNselectedColor;
                        word = word.substring(0, word.length - 1);
                        if (LastToRemove){
                            break;
                        }
                    }
                    selectedTiles = RemoveFromArray(selectedTiles, toRemove)
                    if (word === "") {word = " "}
                    document.getElementsByClassName("word")[0].innerText = word;
                }
                //console.log(selectedTiles)
            })

        }
        document.getElementById("map").appendChild(parent);
        //document.getElementById("map").appendChild(document.getElementById("underBoard"))
    }
    GameplayLoop();
}
document.getElementById("underBoard").style.display = "none";
document.getElementById("sendBtn").addEventListener("click", async (event) => {
    if (selectedTiles.length >= 2 && selectedTiles.length < 8){
        document.getElementById("sendBtn").style.visibility = "hidden";
        IsMyTurn = false;
        const startData = await fetchAsync(url + "/postword", {"secret": secret, "player": player, "content-type":"application/json"}, {"word": word, "worddata": selectedTiles})
        if (startData.result === "-1") {
            alert(startData.error)
            return
        }
        GameplayLoop()
    } else {
        alert("Too short word.")
        return
    }
});
main().catch(console.log);