function sendMessage() {
    let userInput = document.getElementById("user-input");
    let message = userInput.value.trim();
    if (message === "") return;

    let chatBox = document.getElementById("chat-box");

    let userMessageHTML = `<div class="chat-message user-message">
                                <div class="message-bubble">${message}</div>
                           </div>`;
    chatBox.innerHTML += userMessageHTML;
    userInput.value = "";

    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        let botMessageHTML = `<div class="chat-message bot-message">
                                  <div class="message-bubble">${data.message}</div>
                              </div>`;
        chatBox.innerHTML += botMessageHTML;
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}