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
                letterDiv.style.backgroundColor = "rgb(255, 0, 255)";
            })

        }
        document.getElementById("map").appendChild(parent);
    }
    console.log(JSON.stringify(gameData.data))
}

main().catch(console.log);