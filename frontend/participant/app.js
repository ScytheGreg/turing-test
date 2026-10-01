const recordButton = document.getElementById("recordButton");
const stopButton = document.getElementById("stopButton");

const rerecordButton = document.getElementById("rerecordButton");
const sendButton = document.getElementById("sendButton");

const statusElement = document.getElementById("status");
const reviewSection = document.getElementById("review");
const transcriptElement = document.getElementById("transcript");

const answerSection = document.getElementById("answer");
const answerTextElement = document.getElementById("answerText");


function setStatus(message) {
    statusElement.textContent = message;
}


function showRecordingControls() {
    recordButton.hidden = false;
    stopButton.hidden = true;
}


function showStopControl() {
    recordButton.hidden = true;
    stopButton.hidden = false;
}


async function startRecording() {
    recordButton.disabled = true;

    const response = await fetch("/api/record/start", {
        method: "POST",
    });

    const data = await response.json();

    if (!response.ok) {
        recordButton.disabled = false;
        throw new Error(data.detail);
    }

    showStopControl();

    recordButton.disabled = false;

    setStatus("🔴 Nagrywanie...");
}


async function stopRecording() {
    stopButton.disabled = true;

    setStatus("⏳ Rozpoznawanie mowy...");

    const response = await fetch("/api/record/stop", {
        method: "POST",
    });

    const data = await response.json();

    if (!response.ok) {
        stopButton.disabled = false;
        throw new Error(data.detail);
    }

    showRecordingControls();

    transcriptElement.value = data.transcript;

    reviewSection.hidden = false;

    stopButton.disabled = false;

    setStatus("📝 Sprawdź transkrypcję.");
}


async function updateTranscript() {
    const text = transcriptElement.value.trim();

    if (!text) {
        throw new Error("Transkrypcja nie może być pusta.");
    }

    const response = await fetch("/api/transcript", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            text: text,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail);
    }
}


async function sendMessage() {
    await updateTranscript();

    setStatus("⏳ Generowanie odpowiedzi...");

    sendButton.disabled = true;
    rerecordButton.disabled = true;

    const response = await fetch("/api/send", {
        method: "POST",
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail);
    }

    answerTextElement.textContent = data.answer;
    answerSection.hidden = false;

    setStatus("✅ Gotowe.");
}


function rerecord() {
    reviewSection.hidden = true;
    answerSection.hidden = true;

    transcriptElement.value = "";

    sendButton.disabled = false;
    rerecordButton.disabled = false;

    showRecordingControls();

    setStatus("Gotowy do ponownego nagrania.");
}


recordButton.addEventListener("click", async () => {
    try {
        await startRecording();
    } catch (error) {
        setStatus(`❌ ${error.message}`);
    }
});


stopButton.addEventListener("click", async () => {
    try {
        await stopRecording();
    } catch (error) {
        setStatus(`❌ ${error.message}`);
    }
});


rerecordButton.addEventListener("click", () => {
    rerecord();
});


sendButton.addEventListener("click", async () => {
    try {
        await sendMessage();
    } catch (error) {
        sendButton.disabled = false;
        rerecordButton.disabled = false;

        setStatus(`❌ ${error.message}`);
    }
});


showRecordingControls();