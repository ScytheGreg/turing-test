document.addEventListener("DOMContentLoaded", () => {

    // 1. Odczytanie identyfikatora sesji z URL (domyślnie 'alice')
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = (urlParams.get("session") || "bob").toLowerCase();

    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
        `${wsProtocol}//${window.location.host}/ws/${sessionId}`
    );

    // Wyświetlenie nazwy wybranej sesji w nagłówku
    const headerTitle = document.getElementById("sessionTitle");
    if (headerTitle) {
        headerTitle.textContent = `Rozmowa: ${sessionId.toUpperCase()}`;
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
    const messagesElement = document.getElementById("messages");
    const emptyState = document.getElementById("emptyState");
    let stateRequestToken = 0;

    document.body.classList.add(
        sessionId === "alice" ? "session-alice" : "session-bob",
    );

    // Rejestracja zdarzeń
    recordButton.addEventListener("click", startRecording);
    stopButton.addEventListener("click", stopRecording);
    reRecordButton.addEventListener("click", cancelRecording);
    sendButton.addEventListener("click", sendMessage);
    transcriptInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (!sendButton.disabled) {
                sendButton.click();
            }
        }
    });

    // Pobranie stanu przy starcie
    fetchState();

    async function fetchState() {
        const requestToken = stateRequestToken;

        try {
            const res = await fetch(`${apiBase}/state`);
            const data = await res.json();

            if (requestToken !== stateRequestToken) {
                return;
            }

            updateUI(data.state, data.transcript, data.answer);
        } catch (err) {
            console.error("Błąd pobierania stanu:", err);
        }
    }

    async function startRecording() {
        stateRequestToken += 1;

        try {
            recordButton.disabled = true;
            const res = await fetch(`${apiBase}/record/start`, { method: "POST" });
            const data = await res.json();

            if (res.ok) {
                updateUI(data.state || "recording");
            } else {
                alert(data.detail || "Nie udało się rozpocząć nagrywania.");
                fetchState();
            }
        } catch (err) {
            console.error("Błąd startu nagrywania:", err);
            fetchState();
        }
    }

    async function stopRecording() {
        stateRequestToken += 1;

        try {
            stopButton.disabled = true;
            updateUI("transcribing");

            const res = await fetch(`${apiBase}/record/stop`, { method: "POST" });
            const data = await res.json();

            if (res.ok) {
                updateUI(data.state || "review", data.transcript);
            } else {
                alert(data.detail || "Błąd rozpoznawania mowy.");
                fetchState();
            }
        } catch (err) {
            console.error("Błąd zatrzymywania nagrywania:", err);
            fetchState();
        }
    }

    async function cancelRecording() {
        stateRequestToken += 1;

        try {
            const res = await fetch(`${apiBase}/cancel`, { method: "POST" });
            const data = await res.json();
            updateUI(res.ok ? data.state || "idle" : "idle");
        } catch (err) {
            console.error("Błąd anulowania:", err);
            updateUI("idle");
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
                updateUI("idle");

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
        recordButton.disabled = normalizedState !== "idle";
        stopButton.disabled = normalizedState !== "recording";

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
            appendMessage("incoming", answer);
        }
    }

    function appendMessage(direction, text) {
        if (!text) {
            return;
        }

        emptyState.hidden = true;

        const messageElement = document.createElement("article");
        const labelElement = document.createElement("div");
        const textElement = document.createElement("div");

        messageElement.className = `message message-${direction}`;
        labelElement.className = "message-label";
        labelElement.textContent = direction === "outgoing" ? "Ty" : "Rozmówca";
        textElement.className = "message-text";
        textElement.textContent = text;

        messageElement.append(labelElement, textElement);
        messagesElement.appendChild(messageElement);
        messagesElement.scrollTop = messagesElement.scrollHeight;
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
            appendMessage("outgoing", message.text);
        }

        if (message.type === "assistant_message" || message.type === "human_reply") {
            appendMessage("incoming", message.text);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
});
