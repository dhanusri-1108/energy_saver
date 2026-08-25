// Talks to OUR OWN Flask backend at /api/chat — the Anthropic key never
// touches this file or the browser at all; app.py holds it server-side.

const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

let history = [];

function addMessage(who, text) {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}

addMessage("bot", `Vanakkam! Naan ${window.BOT_NAME} ${window.BOT_EMOJI} ${window.BOT_TAGLINE}. Kelvi kelunga!`);

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  chatInput.value = "";
  history.push({ role: "user", content: text });

  const typingDiv = addMessage("typing", "typing…");
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history }),
    });
    const data = await res.json();
    typingDiv.remove();

    if (!res.ok) {
      addMessage("error", data.error || "Something went wrong.");
      history.pop();
      return;
    }

    addMessage("bot", data.reply);
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    typingDiv.remove();
    addMessage("error", "Network error: " + err.message);
    history.pop();
  } finally {
    sendBtn.disabled = false;
  }
});
