let audioEnabled = false;
const displayConfig = DisplayConfig.getDisplayConfig(window.location.search);

document.getElementById("leftTitle").textContent = displayConfig.leftName;
document.getElementById("rightTitle").textContent = displayConfig.rightName;

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
            message.type !== "assistant_message"
        ) {
            return;
        }

        const messageElement = document.createElement("div");

        if (message.type === "user_message") {
            messageElement.className = "message host-message";
        } else {
            messageElement.className = `message response-message ${sessionId}-response`;
        }

        messageElement.textContent = message.text;

        messagesElement.appendChild(messageElement);
        messagesElement.scrollTop = messagesElement.scrollHeight;
    };

    ws.onclose = () => {
        console.log(`Display disconnected: ${sessionId}`);
    };

    ws.onerror = (error) => {
        console.error(`Display WebSocket error [${sessionId}]:`, error);
    };
}


connectSession(displayConfig.left, "leftMessages");
connectSession(displayConfig.right, "rightMessages");
