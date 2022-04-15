navigator.mediaDevices.getUserMedia({audio:true})
    .then(stream => {handlerFunction(stream)})

function handlerFunction(stream) {
    rec = new MediaRecorder(stream);
    rec.ondataavailable = e => {
        audioChunks.push(e.data);
        if (rec.state === "inactive"){
            let blob = new Blob(audioChunks,{type:'audio/mp3'});
            let audioUrl = URL.createObjectURL(blob);
            let recordedAudio = document.getElementById('recordedAudio')
            recordedAudio.src = audioUrl;
            recordedAudio.controls=true;
            recordedAudio.autoplay=true;
            sendData(blob, btn_record.innerText.toLowerCase())
        }
    }
}

let loading_eigenschappen = document.getElementById('loading_eigenschappen');
const btn_record = document.getElementById('btn-record');
const picture = document.getElementById('picture');
const tekst_bij_foto = document.getElementById('tekst_bij_foto');
const text_under_pic = document.getElementById('saved');
const big_content = document.getElementById('big-content');
const small_content = document.getElementById('small-content');

//normal parameters
let pitch_normal = 0;
let loudness_normal = 0;


function sendData(blob, kind) {
  let data_to_send = new FormData();
  data_to_send.append('audio_data', blob);
  if (kind.toLowerCase().includes("saved")){
    data_to_send.append('extra_data', [pitch_normal, loudness_normal])
    fetch('http://127.0.0.1:5000/receive_elderspeak', {
        method: 'POST',
        body: data_to_send
    }).then(response => {
        console.log("||||||||||||||||||||||||||||||||||")
        console.log(response)
        return response.json();
    }).then(json => {
        console.log("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        console.log(json)
        big_content.insertAdjacentHTML("beforeend", `<div><h4>Wat heb je gezegd?</h4><p>${json['speech_recognition']}</p></div>`);
        big_content.insertAdjacentHTML("beforeend", `<div><h4>Verkleinwoorden:</h4><p>${json['verkleinwoorden']}</p></div>`);
        big_content.insertAdjacentHTML("beforeend", `<div><h4>Herhalingen:</h4><p>${json['herhalingen']}</p></div>`);
        big_content.insertAdjacentHTML("beforeend", `<div><h4>Collectieve voornaamwoorden:</h4><p>${json['collectieve_voornaamwoorden']}</p></div>`);
        big_content.insertAdjacentHTML("beforeend", `<div><h4>Tussenwerpsels:</h4><p>${json['tussenwerpsels']}</p></div>`);

        small_content.insertAdjacentHTML("beforeend", `<div class="col-6"><h4>Stemfrequentie:</h4><p>${json['pitch']}</p></div>`);
        small_content.insertAdjacentHTML("beforeend", `<div class="col-6"><h4>Stemvolume:</h4><p>${json['loudness']}</p></div>`);

        loading_eigenschappen.classList.add('hidden');
        document.getElementById('eigenschappen_content').classList.remove('hidden');
    }).catch((error) => {
        document.getElementById('errors').classList.remove('hidden');
        loading_eigenschappen.classList.add('hidden');
        console.log(error);
    });
  } else {
      fetch('http://127.0.0.1:5000/receive_normal', {
        method: 'POST',
        body: data_to_send
    }).then(response => {
        return response.json();
    }).then(json => {
        btn_record.disabled = false;
        pitch_normal = json['pitch'];
        loudness_normal = json['loudness'];
    }).catch((error) => {
        console.log(error)
    });
  }

}

function start_audio(text_after){
    audioChunks = [];
    rec.start();
    btn_record.classList.remove("btn-primary");
    btn_record.classList.add("btn-warning");
    btn_record.innerText = text_after
}
function stop_audio(innertext, text_after){
    if (innertext === "stop standaard opname") {
        document.getElementById('saved').classList.remove('hidden');
        picture.src = "/static/img/rusthuis.jpg";
        tekst_bij_foto.innerText = "Spreek in hoe je tegen deze bejaarde dame zou praten:";
    } else {
        loading_eigenschappen.classList.remove('hidden');
        document.getElementById('eigenschappen_elderspeak').classList.remove('hidden');
        btn_record.disabled = true;
    }
    rec.stop();
    btn_record.classList.remove("btn-warning");
    btn_record.classList.add("btn-primary");
    btn_record.innerText = text_after;
}

btn_record.addEventListener('click', () => {
    if (btn_record.innerText.toLowerCase() === "standaard audio opnemen"){
        start_audio("Stop standaard opname")
    } else if (btn_record.innerText.toLowerCase() === "stop standaard opname"){
        stop_audio("stop standaard opname", "Elderspeak audio opnemen")
        btn_record.disabled = true;
    } else if (btn_record.innerText.toLowerCase() === "elderspeak audio opnemen"){
        start_audio("Stop elderspeak audio opname")
    } else if (btn_record.innerText.toLowerCase() === "stop elderspeak audio opname"){
        stop_audio("stop elderspeak audio opname", "Saved")
    }

});

document.getElementById('reset').addEventListener('click', () => {
    location.reload()
})