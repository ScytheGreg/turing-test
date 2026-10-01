document.addEventListener("DOMContentLoaded", () => {
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

    // Pobranie bieżącego stanu z backendu przy starcie
    fetchState();

    async function fetchState() {
        try {
            const res = await fetch("/api/state");
            const data = await res.json();
            updateUI(data.state, data.transcript, data.answer);
        } catch (err) {
            console.error("Błąd pobierania stanu:", err);
        }
    }

    async function startRecording() {
        try {
            recordButton.disabled = true;
            const res = await fetch("/api/record/start", { method: "POST" });
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

            const res = await fetch("/api/record/stop", { method: "POST" });
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
            await fetch("/api/cancel", { method: "POST" });
            updateUI("idle");
        } catch (err) {
            console.error("Błąd anulowania:", err);
        }
    }

    async function sendMessage() {
        try {
            sendButton.disabled = true;
            reRecordButton.disabled = true;

            // Najpierw aktualizujemy ewentualnie poprawioną transkrypcję
            const text = transcriptInput.value.trim();
            await fetch("/api/transcript", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            });

            updateUI("sending");

            // Wysłanie wiadomości do LLM
            const res = await fetch("/api/send", { method: "POST" });
            const data = await res.json();

            if (res.ok) {
                // data odpowiada strukturze zwracanej przez FastAPI
                const answer = typeof data === "string" ? data : data.answer;
                updateUI("idle", null, answer);
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

        // 1. Aktualizacja Badge stanu
        statusBadge.className = `badge ${normalizedState}`;

        const stateLabels = {
            idle: "Stan: Gotowy",
            recording: "Stan: Nagrywanie...",
            transcribing: "Stan: Transkrypcja...",
            review: "Stan: Sprawdź tekst",
            sending: "Stan: Wysyłanie..."
        };
        statusBadge.textContent = stateLabels[normalizedState] || `Stan: ${normalizedState}`;

        // 2. Sterowanie widocznością sekcji i przycisków
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

        // 3. Obsługa sekcji z odpowiedzią AI
        if (answer) {
            responseSection.hidden = false;
            answerText.textContent = answer;
        }
    }
});