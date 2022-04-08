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
            sendData(blob)
        }
    }
}

//https://stackoverflow.com/questions/70733510/send-blob-to-python-flask-and-then-save-it
let wat_gezegd = document.getElementById('wat_gezegd')
let verkleinwoorden = document.getElementById('verkleinwoorden')
let loading_eigenschappen = document.getElementById('loading_eigenschappen')
let herhalingen = document.getElementById('herhalingen')
let pitch = document.getElementById('pitch')


function sendData(blob) {
  let data_to_send = new FormData();
  data_to_send.append('audio_data', blob);
  fetch('http://127.0.0.1:5000/receive', {
      method: 'POST',
      body: data_to_send
  }).then(response => {
      return response.json();
  }).then(json => {

      wat_gezegd.insertAdjacentHTML("beforeend", `<h4>Wat heb je gezegd?</h4><p>${json['speech_recognition']}</p>`);
      verkleinwoorden.insertAdjacentHTML("beforeend", `<h4>Verkleinwoorden:</h4><p>${json['verkleinwoorden']}</p>`);
      herhalingen.insertAdjacentHTML("beforeend", `<h4>Herhalingen:</h4><p>${json['herhalingen']}</p>`);
      pitch.insertAdjacentHTML("beforeend", `<h4>Toonhoogte:</h4><p>${json['pitch']}</p>`);
      loading_eigenschappen.classList.add('hidden');
      document.getElementById('eigenschappen_content').classList.remove('hidden');
  }).catch((error) => {
      console.log(error)
  });
}

const btn_record = document.getElementById('btn-record');
btn_record.addEventListener('click', () => {
    if (btn_record.innerText.toLowerCase().includes("opn")){
        btn_record.classList.remove("btn-primary");
        btn_record.classList.add("btn-warning");
        btn_record.innerText = "Stop"
        audioChunks = [];
        rec.start();
        wat_gezegd.innerHTML = "";
        verkleinwoorden.innerHTML = "";
        herhalingen.innerHTML = "";
        pitch.innerHTML = "";
    } else if (btn_record.innerText.toLowerCase().includes("stop")){
        rec.stop();
        loading_eigenschappen.classList.remove('hidden');
        document.getElementById('eigenschappen_elderspeak').classList.remove('hidden')
        btn_record.classList.remove("btn-warning");
        btn_record.classList.add("btn-primary");
        btn_record.innerText = "Nieuwe opname";
        document.getElementById('saved').classList.remove('hidden');
    }

});