async function fetchAsync(url, headers) {
    if (headers === undefined){
        var response = await fetch(url);
    } else {
        var response = await fetch(url, {"headers": headers});
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
const selectedColor = "rgb(209, 63, 52)";
const UNselectedColor = "white";

//0 = not a valid move, 1 = valid move, 2 = remove tile
function IsValid(allBoxes, row, col){
    if (allBoxes.length === 0){
        if (row === 1){
            return 1;
        } else {return 0;}
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
        for (let i = 0; i < arr1.length; i++){
            if (JSON.stringify(arr1[i]) !== JSON.stringify(arr2)){
                retVal.push(arr1[i])
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

async function main(){
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
    const headers = {'secret': startData.secret}
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
                if (IsValid(selectedTiles, parseInt(key), parseInt(col)) === 1){
                    letterDiv.style.backgroundColor = selectedColor;
                    selectedTiles.push([parseInt(key), parseInt(col)]);
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
                    if (toRemove.length === 1) {
                        console.log("ok")
                    }
                    selectedTiles = RemoveFromArray(selectedTiles, toRemove)
                    document.getElementsByClassName("word")[0].innerText = word;
                }
                //console.log(selectedTiles)
            })

        }
        document.getElementById("map").appendChild(parent);
    }
    console.log(JSON.stringify(gameData.data))
}

main().catch(console.log);