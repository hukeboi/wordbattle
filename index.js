//TODO:
// - add game id to ui so the player can share it
// - fix weird css (scaling and positioning)
// - fix hovering tiles its brook
// - show the word enemy used


async function fetchAsync(url, headers, body) {
    if (headers === undefined){
        hed = {"gameid": gameID}
        var response = await fetch(url, {headers: hed});
    } else if (body === undefined){
        headers["gameid"] = gameID;
        var response = await fetch(url, {headers: headers});
    } else {
        headers["gameid"] = gameID;
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
  
let url = "https://word-battle-server.hugestudios.repl.co";
let selectedTiles = [];
let allTiles = [];
let allEnemyTiles = [];
let word = "";
const selectedColorP1 = "rgb(209, 63, 52)";
const ACTSELECTCOLORP1 = "rgb(189, 85, 77)";
const selectedColorP2 = "rgb(33, 82, 217)";
const ACTSELECTCOLORP2 = "rgb(97, 124, 199)";
let selectedColor = "rgb(0, 0, 0)"
const UNselectedColor = "white";
let IsMyTurn = false;
let secret;
let player;
let gameID = "none";
let isWaitingForGame = false;

//0 = not a valid move, 1 = valid move, 2 = remove tile
function IsValid(allBoxes, row, col){
    if (allBoxes.length === 0){
        for (let i = 0; i < allTiles.length; i++){
            if (JSON.stringify(allTiles[i]) === JSON.stringify([row, col])){
                return 1;
            }
        }
        return 0;
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

function isInList(arr, item){
    for (let i = 0; i < arr.length; i++){
        if (JSON.stringify(arr[i]) === JSON.stringify(item)){
            return true;
        }
    }
    return false;
}

function CheckTile(tiles, tile, visited, player){
    tiles = RemoveFromArray(tiles, visited);
    let retFalse = true;
    for (let i = tiles.length - 1; i > 0; i--){
        
        if ((Math.abs(tile[0] - tiles[i][0]) === 1 || Math.abs(tile[0] - tiles[i][0]) === 0) && (Math.abs(tile[1] - tiles[i][1]) === 1 || Math.abs(tile[1] - tiles[i][1]) === 0)){
            if ((player === "1" && tiles[i][0] === 1) || (player === "2" && tiles[i][0] === 13)){
                return true;
            } else if (isInList(visited, tiles[i]) === false){
                visited.push(tiles[i]);
                if (CheckTile(tiles, tiles[i], visited, player)){
                    retFalse = false;
                }
            }
        }
    }
    if (retFalse === false){return true}
    return false
    

}

function CheckIfValid(tiles, player){
    toRemove = []
    for (let i = 0; i < tiles.length; i++){
        if (player === "1" && (tiles[i][0] === 1 || tiles[i][0] === 2)) {
            continue;
        } else if (player === "2" && (tiles[i][0] === 13 || tiles[i][0] === 12)) {
            continue;
        }
        if (CheckTile(tiles, tiles[i], [], player) === false){
            toRemove.push(tiles[i])
        }

    }
    return RemoveFromArray(tiles, toRemove);
}

function ToggleAllTiles(on){
    for (let x = 1; x <= 13; x++){
        for (let y = 1; y <= 10; y++){
            if (on){
                document.getElementById(x + ":" + y).classList.remove("noturn");
            } else {
                document.getElementById(x + ":" + y).classList.add("noturn");
            }
            
        }
    }
}

function RefreshColors(){
    if (player === "1"){
        var enemyColor = selectedColorP2;
        var friendlyColor = selectedColorP1;
        var selecColor = ACTSELECTCOLORP1;
    } else if (player === "2") {
        var enemyColor = selectedColorP1;
        var friendlyColor = selectedColorP2;
        var selecColor = ACTSELECTCOLORP2;
    } else {
        var enemyColor = "rgb(0, 0, 0)";
        var friendlyColor = "rgb(0, 0, 0)";
        var selecColor = "rgb(0, 0, 0)";
    }
    for (let x = 1; x <= 13; x++){
        for (let y = 1; y <= 10; y++){
            let isFreeTile = true;
            for (let i = 0; i < allEnemyTiles.length; i++){
                if (JSON.stringify(allEnemyTiles[i]) === JSON.stringify([x, y])){
                    isFreeTile = false;
                    document.getElementById(x + ":" + y).style.backgroundColor = enemyColor;
                }
            }
            for (let i = 0; i < allTiles.length; i++){
                if (JSON.stringify(allTiles[i]) === JSON.stringify([x, y])){
                    isFreeTile = false;
                    document.getElementById(x + ":" + y).style.backgroundColor = friendlyColor;
                }
            }
            for (let i = 0; i < selectedTiles.length; i++){
                if (JSON.stringify(selectedTiles[i]) === JSON.stringify([x, y])){
                    isFreeTile = false;
                    document.getElementById(x + ":" + y).style.backgroundColor = selecColor;
                }
            }
            if (isFreeTile){
                document.getElementById(x + ":" + y).style.backgroundColor = UNselectedColor;
            } 
            
        }
    }
}


async function GameplayLoop(){
    if (IsMyTurn === false){
        ToggleAllTiles(IsMyTurn);
        const newWord = await fetchAsync(url + "/api/getnewword", {"secret": secret, "player": player});
        if (newWord.result === "-1") {
            alert(newWord.error);
            document.location.reload();
        }
        for (let i = 0; i < newWord.data.length; i++){
            if (isInList(allEnemyTiles, newWord.data[i]) === false){
                allEnemyTiles.push(newWord.data[i])
            }
        }
        allTiles = RemoveFromArray(allTiles, allEnemyTiles);
        
        allTiles = CheckIfValid(allTiles, player);
        for (let i = 0; i < allEnemyTiles.length; i++){
            if (player === "1" && allEnemyTiles[i][0] === 1)
            {
                alert("You lost");
                document.location.reload();
            } else if (player === "2" && allEnemyTiles[i][0] === 13) {
                alert("You lost");
                document.location.reload();
            }
        }
        RefreshColors();
        IsMyTurn = true;
        document.getElementById("sendBtn").style.visibility = "visible";
        word = "";
        document.getElementsByClassName("word")[0].innerText = word;
        ToggleAllTiles(IsMyTurn);
    }
}


async function main(){
    document.getElementsByClassName("searchMatch")[0].style.display = "none";
    let ping = await fetch(url + "/api/ping").catch(function() {
        alert("Failed to connect to server")
        document.location.reload();
    });

    
    const startData = await fetchAsync(url + "/api/getserverstatus")
    if (startData.result === "-1") {
        alert(startData.error)
        document.location.reload();
    }
    if (startData.player === "1"){
        IsMyTurn = true;
        selectedColor = selectedColorP1;
        allTiles = [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [1, 10]];
        allEnemyTiles = [[13, 1], [13, 2], [13, 3], [13, 4], [13, 5], [13, 6], [13, 7], [13, 8], [13, 9], [13, 10]];
    } else {
        IsMyTurn = false;
        document.getElementById("sendBtn").style.visibility = "hidden";
        selectedColor = selectedColorP2;
        allTiles = [[13, 1], [13, 2], [13, 3], [13, 4], [13, 5], [13, 6], [13, 7], [13, 8], [13, 9], [13, 10]];
        allEnemyTiles = [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [1, 10]];
    }
    
    player = startData.player
    secret = startData.secret;
    const headers = {'secret': secret}
    document.getElementById("waiting").style.display = "inherit";
    document.getElementById("code").innerText = "Your lobby code: " + gameID;
    const gameData = await fetchAsync(url + "/api/getgamedata", headers);
    if (gameData.result === "-1") {
        alert(gameData.error)
        document.location.reload();
    }
    document.getElementById("placeholderMap").style.display = "none";
    document.getElementById("underBoard").style.display = "inherit";

    document.getElementById("waiting").style.display = "none";

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
                    if (selectedTiles.length >= 9) {
                        alert("You cant have more than 9 letters.");
                        return;
                    }
                    //letterDiv.style.backgroundColor = selectedColor;
                    selectedTiles.push([parseInt(key), parseInt(col)]);
                    RefreshColors();
                    word = word + letterChild.innerText;
                    document.getElementsByClassName("word")[0].innerText = word;
                } else if (IsValid(selectedTiles, parseInt(key), parseInt(col)) === 2){
                    let toRemove = [];
                    for (let i = selectedTiles.length - 1; i >= 0; i--){
                        let LastToRemove = false;
                        if (selectedTiles[i][0] === parseInt(key) && selectedTiles[i][1] === parseInt(col)){
                            LastToRemove = true;
                        }
                        toRemove.push(selectedTiles[i]);
                        
                        //document.getElementById(selectedTiles[i][0] + ":" + selectedTiles[i][1]).style.backgroundColor = UNselectedColor;
                        word = word.substring(0, word.length - 1);
                        if (LastToRemove){
                            break;
                        }
                    }
                    
                    selectedTiles = RemoveFromArray(selectedTiles, toRemove)
                    RefreshColors();
                    document.getElementsByClassName("word")[0].innerText = word;
                }
                //console.log(selectedTiles)
            })

        }
        document.getElementById("map").appendChild(parent);
        //document.getElementById("map").appendChild(document.getElementById("underBoard"))
    }
    document.getElementById("map").appendChild(document.getElementById("underBoard"))
    RefreshColors();
    GameplayLoop();
}
document.getElementById("underBoard").style.display = "none";
document.getElementById("sendBtn").addEventListener("click", async (event) => {
    if (selectedTiles.length >= 2 && selectedTiles.length <= 9){
        document.getElementById("sendBtn").style.visibility = "hidden";
        IsMyTurn = false;
        const postData = await fetchAsync(url + "/api/postword", {"secret": secret, "player": player, "content-type":"application/json"}, {"word": word, "worddata": selectedTiles})
        if (postData.result === "-1") {
            alert(postData.error)
            document.location.reload();
        } else if (postData.result === "1"){
            alert("Not a word. (" + word + ")");
            IsMyTurn = true;
            document.getElementById("sendBtn").style.visibility = "visible";
            selectedTiles = [];
            RefreshColors();
            word = "";
            document.getElementsByClassName("word")[0].innerText = word;
            return
        }

        for (let i = 0; i < selectedTiles.length; i++){
            if (isInList(allTiles, selectedTiles[i]) === false){
                allTiles.push(selectedTiles[i]);
            }
        }
        selectedTiles = [];
        allEnemyTiles = RemoveFromArray(allEnemyTiles, allTiles);
        let p;
        if (player === "1") {p = "2"} else {p = "1"}
        allEnemyTiles = CheckIfValid(allEnemyTiles, p);
        for (let i = 0; i < allTiles.length; i++){
            if (player === "1" && allTiles[i][0] === 13)
            {
                alert("You won");
                quitGame();
                document.location.reload();
            } else if (player === "2" && allTiles[i][0] === 1) {
                alert("You won");
                quitGame();
                document.location.reload();
            }
        }
        RefreshColors();
        GameplayLoop();
    } else {
        alert("Too short word.")
    }
});
document.getElementById("id").value = "";
document.getElementById("waiting").style.display = "none";

//join
document.getElementById("joingame").style.display = "none";
document.getElementById("join1").addEventListener("click", (clic) => {
    document.getElementById("create").style.display = "none";
    document.getElementById("joingame").style.display = "inherit";
    document.getElementById("join1").style.display = "none";

})

document.getElementById("create").addEventListener("click", async (click) => {
    if (isWaitingForGame) {return;}
    isWaitingForGame = true;
    let resp = await fetch(url + "/api/makenewgame")
    let data = await resp.json();
    if (data.result === "-1"){
        alert(data.error);
        document.location.reload();
    }
    gameID = data.gameid;

    document.getElementById("create").style.display = "none";
    document.getElementById("join1").style.display = "none";
    
    main().catch(console.log);
});
document.getElementById("join2").addEventListener("click", (cl) => {
    if (isWaitingForGame) {return;}
    isWaitingForGame = true;
    gameID = document.getElementById("id").value;
    document.getElementById("create").style.display = "none";
    document.getElementById("id").style.display = "none";
    document.getElementById("join2").style.display = "none";
    
    main().catch(console.log);
})

async function quitGame(){
    await fetch(url + "/api/quit?id=" + gameID)
}
window.addEventListener('beforeunload', async () => {
    await quitGame();
    return "Do you want to exit??";
})

//main().catch(console.log);