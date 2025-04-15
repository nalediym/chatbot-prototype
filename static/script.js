// function typewriterEffect(element, text, speed = 15) {
//   let index = 0;
//   function type() {
//     if (index < text.length) {
//       element.textContent += text.charAt(index);
//       element.scrollIntoView({ behavior: "smooth", block: "end" });
//       index++;
//       setTimeout(type, speed);
//     }
//   }
//   type();
// }


function typewriterEffect(element, text, speed = 15) {
  let index = 0;
  let plainText = text.replace(/<br>/g, '\n'); // Avoid breaking HTML

  function type() {
    if (index < plainText.length) {
      element.textContent += plainText.charAt(index);
      element.scrollIntoView({ behavior: "smooth", block: "end" });
      index++;
      setTimeout(type, speed);
    }
  }

  type();
}


async function sendMessage() {
  const input = document.getElementById("chatInput");
  const chatWindow = document.getElementById("chatWindow");
  const message = input.value.trim();
  if (!message) return;

  // Show user message
  const userMsg = document.createElement("div");
  userMsg.className = "message user";
  userMsg.textContent = message;
  chatWindow.appendChild(userMsg);

  // Bot placeholder
  const botMsg = document.createElement("div");
  botMsg.className = "message bot";
  botMsg.textContent = "Thinking...";
  chatWindow.appendChild(botMsg);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  input.value = "";

  // === Base URL auto detect ===
  const baseURL = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
    ? "http://127.0.0.1:8000"
    : window.location.origin;

  try {
    const res = await fetch(`${baseURL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) throw new Error("Server returned: " + res.status);

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let finalText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      finalText += chunk;
      // botMsg.textContent = finalText;
      botMsg.innerHTML = finalText.replace(/\n/g, "<br>");
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    //botMsg.textContent = ""; // reset
    //typewriterEffect(botMsg, finalText);

  } catch (err) {
    botMsg.textContent = "⚠️ Error: " + err.message;
    console.error("Chat fetch error:", err);
  }

  chatWindow.scrollTop = chatWindow.scrollHeight;
}


document.querySelectorAll('.question').forEach(btn => {
  btn.addEventListener('click', () => {
    document.getElementById('chatInput').value = btn.textContent;
    sendMessage();
  });
});

document.getElementById("clearChat").addEventListener("click", function (e) {
  e.preventDefault();
  const chatWindow = document.getElementById("chatWindow");
  if (chatWindow) {
    chatWindow.innerHTML = ""; // Clear all messages
  }
});