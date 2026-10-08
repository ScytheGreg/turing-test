document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = (urlParams.get("session") || "bob").toLowerCase();

    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
        `${wsProtocol}//${window.location.host}/ws/${sessionId}`
    );

    const connectionStatus = document.getElementById("connectionStatus");
    const conversation = document.getElementById("conversation");
    const emptyState = document.getElementById("emptyState");
    const messageForm = document.getElementById("messageForm");
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");
    const sessionTitle = document.getElementById("sessionTitle");

    sessionTitle.textContent = `Rozmowa: ${sessionId.toUpperCase()}`;

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

    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            messageForm.requestSubmit();
        }
    });

    function addMessage(sender, text) {
        emptyState.hidden = true;

        const element = document.createElement("article");
        element.className = sender === "Ty"
            ? "message message-outgoing"
            : "message message-incoming";

        const senderElement = document.createElement("strong");
        senderElement.textContent = sender;

        const textElement = document.createElement("div");
        textElement.className = "message-text";
        textElement.textContent = text;

        element.appendChild(senderElement);
        element.appendChild(textElement);

        conversation.appendChild(element);
        conversation.scrollTop = conversation.scrollHeight;

        requestAnimationFrame(() => {
            window.scrollTo({
                top: document.documentElement.scrollHeight,
                behavior: "smooth",
            });
        });
    }
});
