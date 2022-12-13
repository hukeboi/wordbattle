async function fetchAsync(url, headers) {
    if (headers === undefined){
        var response = await fetch(url);
    } else {
        var response = await fetch(url, {"headers": headers});
    }
    let data = await response.json();
    return data;
}

async function main(){
    const startData = await fetchAsync("https://word-battle-server.hugestudios.repl.co/getserverstatus");
    if (startData.result === "-1") {
        alert(startData.error)
        return
    }
    const headers = {'secret': startData.secret}
    const gameData = await fetchAsync("https://word-battle-server.hugestudios.repl.co/getgamedata", headers);
    if (gameData.result === "-1") {
        alert(gameData.error)
        return
    }
    for (const [key, value] of Object.entries(gameData.data)) {
        let parent = document.createElement("div");
        for (const [key, letter] of Object.entries(value)) {
            let letterDiv = document.createElement("div");
            letterDiv.className = "letter";
            let letterChild = document.createElement("p");
            letterChild.className = "letterChild";
            letterChild.innerText = letter;
            letterDiv.appendChild(letterChild)
            parent.appendChild(letterDiv)
        }
        document.getElementById("map").appendChild(parent);
    }
    console.log(JSON.stringify(gameData.data))
}

main().catch(console.log);