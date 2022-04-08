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

let wat_gezegd = document.getElementById('wat_gezegd')
let verkleinwoorden = document.getElementById('verkleinwoorden')
let loading_eigenschappen = document.getElementById('loading_eigenschappen')
let herhalingen = document.getElementById('herhalingen')
let pitch = document.getElementById('pitch')
const btn_record = document.getElementById('btn-record');
const picture = document.getElementById('picture');
const text_under_pic = document.getElementById('saved')
const loudness = document.getElementById('loudness')
const loudness_1 = document.getElementById('loudness_1')

function sendData(blob, kind) {
  let data_to_send = new FormData();
  data_to_send.append('audio_data', blob);
  if (kind.toLowerCase().includes("saved")){
    fetch('http://127.0.0.1:5000/receive_elderspeak', {
        method: 'POST',
        body: data_to_send
    }).then(response => {
        return response.json();
    }).then(json => {
        wat_gezegd.insertAdjacentHTML("beforeend", `<h4>Wat heb je gezegd?</h4><p>${json['speech_recognition']}</p>`);
        verkleinwoorden.insertAdjacentHTML("beforeend", `<h4>Verkleinwoorden:</h4><p>${json['verkleinwoorden']}</p>`);
        herhalingen.insertAdjacentHTML("beforeend", `<h4>Herhalingen:</h4><p>${json['herhalingen']}</p>`);
        pitch.insertAdjacentHTML("beforeend", `<h4>Toonhoogte:</h4><p>${json['pitch']}</p>`);
        let volume;
        if(parseFloat(loudness_1.innerText) < parseFloat(json['loudness'])){
            volume = `<span class="text-danger">Luider</span>`
        } else if(parseFloat(loudness_1.innerText) > parseFloat(json['loudness'])){
            volume = `<span class="text-success">Stiller</span>`
        } else {
            volume = "???"
        }
        loudness.insertAdjacentHTML("beforeend", `<h4>Verhoogd stemvolume:</h4><p>${volume}</p>`);
        loading_eigenschappen.classList.add('hidden');
        document.getElementById('eigenschappen_content').classList.remove('hidden');
    }).catch((error) => {
        console.log(error);
    });
  } else {
      fetch('http://127.0.0.1:5000/receive_normal', {
        method: 'POST',
        body: data_to_send
    }).then(response => {
        return response.json();
    }).then(json => {
        text_under_pic.innerText = json['pitch']
        loudness_1.innerText = json['loudness']
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
        picture.src = "/static/img/rusthuis.jpg"
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
    } else if (btn_record.innerText.toLowerCase() === "elderspeak audio opnemen"){
        start_audio("Stop elderspeak audio opname")
    } else if (btn_record.innerText.toLowerCase() === "stop elderspeak audio opname"){
        stop_audio("stop elderspeak audio opname", "Saved")
    }

});