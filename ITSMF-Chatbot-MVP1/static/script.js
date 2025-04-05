  // Typewriter effect function
function typeText(element, text, speed = 10) {
    element.innerHTML = "";
    let index = 0;
  
    function type() {
      if (index < text.length) {
        element.scrollIntoView({ behavior: 'smooth', block: 'end' });
        element.innerHTML += text.charAt(index);
        index++;
        setTimeout(type, speed);
      }
    }
  
    type();
  }

  async function sendMessage() {
    const input = document.getElementById("userInput");
    const chatLog = document.getElementById("chat-log");
    const userText = input.value.trim();
  
    if (!userText) return;
  
    // Display user message
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.textContent = userText;
    chatLog.appendChild(userMsg);
  
    input.value = "";
  
    // Placeholder for bot response
    const botMsg = document.createElement("div");
    botMsg.className = "message bot";
    botMsg.textContent = "Thinking...";
    chatLog.appendChild(botMsg);
    chatLog.scrollTop = chatLog.scrollHeight;
  
    try {
      const res = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText })
      });
  
      const data = await res.json();
      botMsg.textContent = "";  // Clear placeholder
  
      if (data.response) {
        typeText(botMsg, data.response);  // 👈 Typewriter here!
      } else {
        botMsg.textContent = "Oops! No response.";
      }
    } catch (err) {
      botMsg.textContent = "Error: " + err.message;
    }
  
    chatLog.scrollTop = chatLog.scrollHeight;
  }
