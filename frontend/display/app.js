let audioEnabled = false;

document.getElementById("enableAudio").addEventListener("click", () => {
    audioEnabled = true;

    document.getElementById("enableAudio").textContent = "🔊 Dźwięk włączony";
    document.getElementById("enableAudio").disabled = true;
});


function connectSession(sessionId, messagesElementId) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";

    const ws = new WebSocket(
        `${protocol}//${window.location.host}/ws/${sessionId}`
    );

    const messagesElement = document.getElementById(messagesElementId);

    ws.onopen = () => {
        console.log(`Display connected: ${sessionId}`);
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        console.log(`Display event [${sessionId}]:`, message);

        if (message.type === "audio_ready") {
            if (!audioEnabled) {
                console.warn("Dźwięk nie został jeszcze włączony.");
                return;
            }

            const audio = new Audio(
                new URL(message.audio_url, window.location.origin).href
            );

            console.log("Odtwarzam audio:", audio.src);

            audio.play().catch((error) => {
                console.error(
                    `Błąd odtwarzania audio [${sessionId}]:`,
                    error
                );
            });

            return;
        }

        if (
            message.type !== "user_message" &&
            message.type !== "human_reply" &&
            message.type !== "assistant_message" &&
            message.type !== "host_message"
        ) {
            return;
        }

        const messageElement = document.createElement("div");
        messageElement.className = "message";
        messageElement.textContent = message.text;

        messagesElement.appendChild(messageElement);
    };

    ws.onclose = () => {
        console.log(`Display disconnected: ${sessionId}`);
    };

    ws.onerror = (error) => {
        console.error(`Display WebSocket error [${sessionId}]:`, error);
    };
}


connectSession("alice", "aliceMessages");
connectSession("bob", "bobMessages");
