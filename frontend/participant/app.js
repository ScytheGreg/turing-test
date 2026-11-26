document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = (urlParams.get("session") || "bob").toLowerCase();
    const apiBase = `/api/session/${sessionId}`;
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
        `${wsProtocol}//${window.location.host}/ws/${sessionId}`
    );

    const headerTitle = document.getElementById("sessionTitle");
    const statusBadge = document.getElementById("statusBadge");
    const messageForm = document.getElementById("messageForm");
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");
    const messagesElement = document.getElementById("messages");
    const emptyState = document.getElementById("emptyState");

    headerTitle.textContent = `Rozmowa: ${sessionId.toUpperCase()}`;
    document.body.classList.add(
        sessionId === "alice" ? "session-alice" : "session-bob",
    );

    messageForm.addEventListener("submit", sendMessage);
    messageInput.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" || event.shiftKey || event.isComposing) {
            return;
        }

        event.preventDefault();
        messageForm.requestSubmit();
    });

    async function sendMessage(event) {
        event.preventDefault();

        const text = messageInput.value.trim();
        if (!text || sendButton.disabled) {
            return;
        }

        if (ws.readyState !== WebSocket.OPEN) {
            statusBadge.textContent = "Brak połączenia z serwerem";
            return;
        }

        sendButton.disabled = true;
        messageInput.disabled = true;
        statusBadge.className = "badge sending";
        statusBadge.textContent = "Wysyłanie...";

        try {
            ws.send(JSON.stringify({ text }));

            if (sessionId === "bob") {
                messageInput.value = "";
                setReady();
                return;
            }

            const response = await fetch(`${apiBase}/message`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Nie udało się wysłać wiadomości.");
            }

            messageInput.value = "";
            setReady();
        } catch (error) {
            console.error("Błąd wysyłania wiadomości:", error);
            statusBadge.className = "badge error";
            statusBadge.textContent = "Nie udało się wysłać";
        } finally {
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
    }

    function setReady() {
        statusBadge.className = "badge idle";
        statusBadge.textContent = "Gotowy";
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
        setReady();
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "user_message") {
            appendMessage("outgoing", message.text);
        }

        if (message.type === "assistant_message" || message.type === "human_reply") {
            appendMessage("incoming", message.text);
        }
    };

    ws.onclose = () => {
        statusBadge.className = "badge error";
        statusBadge.textContent = "Rozłączono";
        messageInput.disabled = true;
        sendButton.disabled = true;
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
});
