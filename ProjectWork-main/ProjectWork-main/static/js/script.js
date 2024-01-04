(function () {
    if (!("mediaDevices" in navigator) || !("getUserMedia" in navigator.mediaDevices)) {
        alert("Camera API is not available in your browser");
        return;
    }

    // get page elements
    const video = document.querySelector("#video");
    const btnPlay = document.querySelector("#btnPlay");
    const btnPause = document.querySelector("#btnPause");
    const btnScreenshot = document.querySelector("#btnScreenshot");
    const btnChangeCamera = document.querySelector("#btnChangeCamera");
    const screenshotsContainer = document.querySelector("#screenshots");
    const canvas = document.querySelector("#canvas");
    const devicesSelect = document.querySelector("#devicesSelect");

    // video constraints
    const constraints = {
        video: {
            width: {
                min: 1280,
                ideal: 1920,
                max: 2560,
            },
            height: {
                min: 720,
                ideal: 1080,
                max: 1440,
            },
        },
    };

    // use front face camera
    let useFrontCamera = true;

    // current video stream
    let videoStream;

    // handle events
    function playVideo() {
        console.log("Verificando a inicialização do vídeo.")
        video.play();
        btnPlay.classList.add("is-hidden");
        btnPause.classList.remove("is-hidden");
    }

    function pauseVideo() {
        console.log("Verificando a pausa do vídeo.")
        video.pause();
        btnPause.classList.add("is-hidden");
        btnPlay.classList.remove("is-hidden");
    }

    btnPlay.addEventListener("click", playVideo);
    btnPause.addEventListener("click", pauseVideo);

    console.log("Registrando o evento de screenshot");
    // take screenshot
    btnScreenshot.addEventListener("click", function () {
        const img = document.createElement("img");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        img.src = canvas.toDataURL("image/png");
        screenshotsContainer.prepend(img);
    });

    // switch camera
    btnChangeCamera.addEventListener("click", function () {
        console.log("Change camera button clicked");
        useFrontCamera = !useFrontCamera;
        initializeCamera();
    });

    // stop video stream
    function stopVideoStream() {
        if (videoStream) {
            videoStream.getTracks().forEach((track) => {
                track.stop();
            });
        }
    }

    

    // initialize
    async function initializeCamera() {
        stopVideoStream();
        constraints.video.facingMode = useFrontCamera ? "user" : "environment";

        try {
            videoStream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = videoStream;
            playVideo(); // Inicia automaticamente a reprodução ao trocar de câmera
        } catch (err) {
            alert("Could not access the camera");
        }
    }

    initializeCamera();
})();
