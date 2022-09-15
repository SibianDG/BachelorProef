let mp3_file = document.getElementById('mp3_file');
const btn_normalize = document.getElementById('normalize');
let el_pitch = document.getElementById('pitch');
let el_loudness = document.getElementById('loudness');
let el_loading = document.getElementById('loading');

//normal parameters
let pitch_normal = 0;
let loudness_normal = 0;

Number.prototype.round = function(places) {
  return +(Math.round(this + "e+" + places)  + "e-" + places);
}

function sendData(blob) {
  let data_to_send = new FormData();
  data_to_send.append('audio_data', blob);
    console.log('Prepared')
  fetch('/receive_normal', {
    method: 'POST',
    body: data_to_send
    }).then(response => {
        el_loading.classList.add('hidden');
        return response.json();
    }).then(json => {
        pitch_normal = json['pitch'];
        loudness_normal = json['loudness'];
    }).then(_ => {
        el_pitch.innerText = pitch_normal;
        el_loudness.innerText = parseFloat(loudness_normal).round(2);
    }).catch((error) => {
        console.log(error)
    });
}

btn_normalize.addEventListener('click', () => {
    el_loading.classList.remove('hidden');
    let blob = mp3_file.files[0];
    sendData(blob);
});

console.log("PRESENT!!")