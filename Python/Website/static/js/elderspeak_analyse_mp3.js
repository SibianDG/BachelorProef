let mp3_file = document.getElementById('mp3_file');
const btn_normalize = document.getElementById('send_data');
let el_pitch = document.getElementById('input_pitch');
let el_loudness = document.getElementById('input_loudness');
let el_loading = document.getElementById('loading');


let loading_eigenschappen = document.getElementById('loading_eigenschappen');
const big_content = document.getElementById('big-content');
const small_content = document.getElementById('small-content');

//normal parameters
let pitch_normal = 0;
let loudness_normal = 0;


function sendData(blob) {
    pitch_normal = el_pitch.value;
    loudness_normal = el_loudness.value;
  let data_to_send = new FormData();
  data_to_send.append('audio_data', blob);
    data_to_send.append('extra_data', [pitch_normal, loudness_normal])
    fetch('/receive_elderspeak', {
        method: 'POST',
        body: data_to_send
    }).then(response => {
        el_loading.classList.add('hidden');
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
        console.log("TOT HIER???")
        loading_eigenschappen.classList.add('hidden');
        document.getElementById('eigenschappen_content').classList.remove('hidden');
    }).catch((error) => {
        document.getElementById('errors').classList.remove('hidden');
        loading_eigenschappen.classList.add('hidden');
        console.log(error);
    });

}


btn_normalize.addEventListener('click', () => {
    el_loading.classList.remove('hidden');
    document.getElementById('eigenschappen_elderspeak').classList.remove('hidden');
    let blob = mp3_file.files[0];
    sendData(blob);
});

document.getElementById('reset').addEventListener('click', () => {
    location.reload()
})