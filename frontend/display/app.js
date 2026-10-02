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

        if (
            message.type !== "user_message" &&
            message.type !== "human_reply"
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