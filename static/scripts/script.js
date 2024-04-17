const selectImage = document.querySelector('.select-image');
const generateImage = document.querySelector('.generate-image');
const translate = document.querySelector('.translate');
const text1 = document.querySelector('.txt1');
const text2 = document.querySelector('.txt2');
const inputFile = document.querySelector('#file');
const imgArea = document.querySelector('.img-area');
var s1='';
var s2='';
var lang='';
let image_base64 = ''; 


selectImage.addEventListener('click', function () {
    inputFile.click();
})

inputFile.addEventListener('change', function () {
    const image = this.files[0]
    if (image.size < 200000000) {
        const reader = new FileReader();
        reader.onload = () => {
            const allImg = imgArea.querySelectorAll('img');
            allImg.forEach(item => item.remove());
            const imgUrl = reader.result;
            const img = document.createElement('img');
            img.src = imgUrl;
            imgArea.appendChild(img);
            imgArea.classList.add('active');
            image_base64 = imgUrl;
            imgArea.dataset.img = image.name;
        }
        reader.readAsDataURL(image);
    } else {
        alert("Image size more than 20MB");
    }
})



generateImage.addEventListener('click', async function () {
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image_base64 }),
        });

        if (response.ok) {
            const result = await response.json();
            finalcaption = result.caption;
            s1 = finalcaption.slice(9,finalcaption.length - 7);
            text1.innerHTML=s1;
            text2.innerHTML="";
            console.log(result);
        } else {
            console.error(`Error: ${response.status} - ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

function speak1() {
    const utterance = new SpeechSynthesisUtterance(s1);
    const voices = speechSynthesis.getVoices();
    utterance.voice = voices[0];
    speechSynthesis.speak(utterance);
  }

translate.addEventListener('click', async function () {
    lang = document.getElementById("lang").value;
    console.log(lang);
    try {
        const response = await fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'s1': s1, 'lang': lang}),
        });

        if (response.ok) {
            const result = await response.json();
            s2 = result.caption;
            text2.innerHTML=s2;
            console.log(result);
        } else {
            console.error(`Error: ${response.status} - ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});


// function speak2() {
//     const utterance = new SpeechSynthesisUtterance();
//     const voices = speechSynthesis.getVoices();
//     const selectedVoice = voices.find(voice => voice.lang.includes(lang));

//     if (selectedVoice) {
//         utterance.voice = selectedVoice;
//     } else {
//         console.error('No suitable voice found for the specified language.');
//         return;
//     }
//     utterance.text = s2;
//     console.log(utterance.text);
//     speechSynthesis.speak(utterance);
//   }

function clean() {
    text2.innerHTML="";
}
