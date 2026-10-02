document.addEventListener("DOMContentLoaded", () => {

    // 1. Odczytanie identyfikatora sesji z URL (domyślnie 'alice')
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = (urlParams.get("session") || "bob").toLowerCase();

    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
        `${wsProtocol}//${window.location.host}/ws/${sessionId}`
    );

    // Wyświetlenie nazwy wybranej sesji w nagłówku
    const headerTitle = document.querySelector("h1");
    if (headerTitle) {
        headerTitle.textContent = `Test Turinga — Rozmowa: ${sessionId.toUpperCase()}`;
    }

    // Adres bazowy dla wybranych endpointów sesji
    const apiBase = `/api/session/${sessionId}`;

    // Elementy UI
    const statusBadge = document.getElementById("statusBadge");
    const recordButton = document.getElementById("recordButton");
    const stopButton = document.getElementById("stopButton");
    const reviewSection = document.getElementById("reviewSection");
    const transcriptInput = document.getElementById("transcriptInput");
    const reRecordButton = document.getElementById("reRecordButton");
    const sendButton = document.getElementById("sendButton");
    const responseSection = document.getElementById("responseSection");
    const answerText = document.getElementById("answerText");

    // Rejestracja zdarzeń
    recordButton.addEventListener("click", startRecording);
    stopButton.addEventListener("click", stopRecording);
    reRecordButton.addEventListener("click", cancelRecording);
    sendButton.addEventListener("click", sendMessage);

    // Pobranie stanu przy starcie
    fetchState();

    async function fetchState() {
        try {
            const res = await fetch(`${apiBase}/state`);
            const data = await res.json();
            updateUI(data.state, data.transcript, data.answer);
        } catch (err) {
            console.error("Błąd pobierania stanu:", err);
        }
    }

    async function startRecording() {
        try {
            recordButton.disabled = true;
            const res = await fetch(`${apiBase}/record/start`, { method: "POST" });
            if (res.ok) {
                updateUI("recording");
            } else {
                alert("Nie udało się rozpocząć nagrywania.");
                fetchState();
            }
        } catch (err) {
            console.error("Błąd startu nagrywania:", err);
            fetchState();
        } finally {
            recordButton.disabled = false;
        }
    }

    async function stopRecording() {
        try {
            stopButton.disabled = true;
            updateUI("transcribing");

            const res = await fetch(`${apiBase}/record/stop`, { method: "POST" });
            const data = await res.json();

            if (res.ok) {
                updateUI("review", data.transcript);
            } else {
                alert("Błąd rozpoznawania mowy.");
                fetchState();
            }
        } catch (err) {
            console.error("Błąd zatrzymywania nagrywania:", err);
            fetchState();
        } finally {
            stopButton.disabled = false;
        }
    }

    async function cancelRecording() {
        try {
            await fetch(`${apiBase}/cancel`, { method: "POST" });
            updateUI("idle");
        } catch (err) {
            console.error("Błąd anulowania:", err);
        }
    }

    async function sendMessage() {
        try {
            sendButton.disabled = true;
            reRecordButton.disabled = true;

            const text = transcriptInput.value.trim();
            if (!text) {
                return;
            }

            if (ws.readyState !== WebSocket.OPEN) {
                alert("Połączenie z serwerem nie jest gotowe.");
                return;
            }

            ws.send(JSON.stringify({
                text: text
            }));
            if (sessionId === "bob") {
                updateUI("idle");
                 return;
            }
            await fetch(`${apiBase}/transcript`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
            });

            updateUI("sending");

            const res = await fetch(`${apiBase}/send`, { method: "POST" });
            const data = await res.json();

            if (res.ok) {
                updateUI("idle", null, data.answer);

                if (data.audio_path) {
                    const audio = new Audio(data.audio_path);
                    audio.play().catch(err => console.error("Błąd odtwarzania audio:", err));
                }
            } else {
                alert("Błąd podczas wysyłania wiadomości.");
                fetchState();
            }
        } catch (err) {
            console.error("Błąd wysyłania:", err);
            fetchState();
        } finally {
            sendButton.disabled = false;
            reRecordButton.disabled = false;
        }
    }

    function updateUI(state, transcript = null, answer = null) {
        const normalizedState = (state || "idle").toLowerCase();

        statusBadge.className = `badge ${normalizedState}`;

        const stateLabels = {
            idle: "Stan: Gotowy",
            recording: "Stan: Nagrywanie...",
            transcribing: "Stan: Transkrypcja...",
            review: "Stan: Sprawdź tekst",
            sending: "Stan: Wysyłanie..."
        };
        statusBadge.textContent = stateLabels[normalizedState] || `Stan: ${normalizedState}`;

        if (normalizedState === "idle") {
            recordButton.hidden = false;
            stopButton.hidden = true;
            reviewSection.hidden = true;
        } else if (normalizedState === "recording") {
            recordButton.hidden = true;
            stopButton.hidden = false;
            reviewSection.hidden = true;
        } else if (normalizedState === "transcribing") {
            recordButton.hidden = true;
            stopButton.hidden = true;
            reviewSection.hidden = true;
        } else if (normalizedState === "review") {
            recordButton.hidden = true;
            stopButton.hidden = true;
            reviewSection.hidden = false;
            if (transcript !== null) {
                transcriptInput.value = transcript;
            }
        } else if (normalizedState === "sending") {
            recordButton.hidden = true;
            stopButton.hidden = true;
            reviewSection.hidden = true;
        }

        if (answer) {
            responseSection.hidden = false;
            answerText.textContent = answer;
        }
    }
    ws.onopen = () => {
        console.log("WebSocket connected:", sessionId);
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        console.log("WebSocket event:", message);

        if (message.type === "connected") {
            console.log("Connected to session:", message.session_id);
        }

        if (message.type === "user_message") {
            console.log("User message:", message.text);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
});