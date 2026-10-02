document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = (urlParams.get("session") || "bob").toLowerCase();

    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
        `${wsProtocol}//${window.location.host}/ws/${sessionId}`
    );

    const connectionStatus = document.getElementById("connectionStatus");
    const conversation = document.getElementById("conversation");
    const messageForm = document.getElementById("messageForm");
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");

    ws.onopen = () => {
        console.log("Human WebSocket connected:", sessionId);

        connectionStatus.textContent = "Połączono";
        connectionStatus.className = "status connected";

        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        console.log("Human event:", message);

        if (message.type === "user_message") {
            addMessage("Rozmówca", message.text);
        }
    };

    ws.onclose = () => {
        connectionStatus.textContent = "Rozłączono";
        connectionStatus.className = "status disconnected";

        messageInput.disabled = true;
        sendButton.disabled = true;
    };

    ws.onerror = (error) => {
        console.error("Human WebSocket error:", error);
    };

    messageForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const text = messageInput.value.trim();

        if (!text) {
            return;
        }

        if (ws.readyState !== WebSocket.OPEN) {
            return;
        }

        ws.send(JSON.stringify({
        type: "human_reply",
        text: text
    }));

        addMessage("Ty", text);

        messageInput.value = "";
        messageInput.focus();
    });

    function addMessage(sender, text) {
        const element = document.createElement("div");
        element.className = "message";

        const senderElement = document.createElement("strong");
        senderElement.textContent = sender;

        const textElement = document.createElement("div");
        textElement.textContent = text;

        element.appendChild(senderElement);
        element.appendChild(textElement);

        conversation.appendChild(element);
        conversation.scrollTop = conversation.scrollHeight;
    }
});
