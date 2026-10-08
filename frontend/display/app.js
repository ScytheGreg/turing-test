let audioEnabled = false;
const displayConfig = window.DisplayConfig
    ? window.DisplayConfig.getDisplayConfig(window.location.search)
    : {
        left: "alice",
        right: "bob",
        leftName: "ALICE",
        rightName: "BOB",
    };
const getMessageLabel = window.DisplayConfig
    ? window.DisplayConfig.getMessageLabel
    : (messageType) => messageType === "user_message"
        ? "Pytanie · prowadzący"
        : "Odpowiedź";

document.getElementById("leftTitle").textContent = displayConfig.leftName;
document.getElementById("rightTitle").textContent = displayConfig.rightName;
document.getElementById("leftSession").textContent = displayConfig.left.toUpperCase();
document.getElementById("rightSession").textContent = displayConfig.right.toUpperCase();

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
        const labelElement = document.createElement("div");
        const textElement = document.createElement("div");
        const isHostMessage = message.type === "user_message";

        if (isHostMessage) {
            messageElement.className = "message host-message";
        } else {
            messageElement.className = `message response-message ${sessionId}-response`;
        }

        labelElement.className = "message-label";
        labelElement.textContent = getMessageLabel(
            message.type,
            sessionId,
        );
        textElement.className = "message-text";
        textElement.textContent = message.text;
        messageElement.append(labelElement, textElement);

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
