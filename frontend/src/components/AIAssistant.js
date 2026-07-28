import { ApiService } from '../services/api.js';

export function renderAIAssistant() {
  return `
    <div class="bx--tile" style="border: 1px solid var(--cds-purple-50); box-shadow: 0 0 15px rgba(138,63,252,0.15);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="bx--tile__heading" style="color: var(--cds-purple-50); font-weight: 600;">
          <i class="fa-solid fa-wand-magic-sparkles"></i> AI TRANSPLANT CLINICAL ASSISTANT
        </span>
        <span class="bx--tag" style="background: rgba(138,63,252,0.2); color: #be95ff; border: 1px solid #8a3ffc;">QUANTUM-AI ONLINE</span>
      </div>

      <!-- Assistant Messages Log -->
      <div id="ai-chat-log" style="background: var(--cds-layer-02); padding: 1rem; max-height: 180px; overflow-y: auto; font-size: 13px; margin-bottom: 12px; border-left: 3px solid var(--cds-purple-50);">
        <div style="color: var(--cds-text-01); margin-bottom: 6px;">
          <strong>AI Assistant:</strong> Welcome Dr./Coordinator. How can I assist with organ compatibility matching, urgent patient alerts, or telemetry analytics today?
        </div>
      </div>

      <!-- Quick Action Shortcuts -->
      <div style="display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;">
        <button class="bx--btn bx--btn--ghost btn-ai-shortcut" data-query="Explain donor match scoring algorithm" style="padding: 4px 10px; font-size: 11px; border: 1px solid var(--cds-border-subtle);">
          <i class="fa-solid fa-dna"></i> Explain Match Scoring
        </button>
        <button class="bx--btn bx--btn--ghost btn-ai-shortcut" data-query="Highlight urgent priority cases" style="padding: 4px 10px; font-size: 11px; border: 1px solid var(--cds-border-subtle);">
          <i class="fa-solid fa-triangle-exclamation"></i> Highlight Urgent Cases
        </button>
        <button class="bx--btn bx--btn--ghost btn-ai-shortcut" data-query="Check cold box temperature telemetry" style="padding: 4px 10px; font-size: 11px; border: 1px solid var(--cds-border-subtle);">
          <i class="fa-solid fa-temperature-arrow-down"></i> Telemetry Check
        </button>
      </div>

      <!-- Chat Input Form -->
      <form id="form-ai-query" style="display: flex; gap: 8px;">
        <input type="text" id="input-ai-prompt" placeholder="Ask AI Assistant e.g. 'Summarize Sarah Jenkins medical history'..." required style="flex: 1; padding: 10px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        <button type="submit" class="bx--btn bx--btn--primary" style="background-color: var(--cds-purple-50);">
          <span>ASK AI</span>
          <i class="fa-solid fa-paper-plane"></i>
        </button>
      </form>
    </div>
  `;
}

export function attachAIAssistantEvents() {
  const form = document.getElementById('form-ai-query');
  const input = document.getElementById('input-ai-prompt');
  const chatLog = document.getElementById('ai-chat-log');

  const sendQuery = async (queryText) => {
    if (!queryText.trim()) return;

    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.style.color = 'var(--cds-interactive-01)';
    userDiv.style.marginBottom = '6px';
    userDiv.innerHTML = `<strong>You:</strong> ${queryText}`;
    chatLog.appendChild(userDiv);
    chatLog.scrollTop = chatLog.scrollHeight;

    try {
      const formData = new FormData();
      formData.append('query', queryText);

      const res = await fetch('/api/v1/telemetry/ai-query', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      const aiDiv = document.createElement('div');
      aiDiv.style.color = 'var(--cds-text-01)';
      aiDiv.style.marginBottom = '6px';
      aiDiv.innerHTML = `<strong>AI Assistant:</strong> ${data.response}`;
      chatLog.appendChild(aiDiv);
      chatLog.scrollTop = chatLog.scrollHeight;
    } catch (err) {
      console.error('AI Query Error:', err);
    }
  };

  if (form) {
    form.onsubmit = (e) => {
      e.preventDefault();
      const text = input.value;
      input.value = '';
      sendQuery(text);
    };
  }

  document.querySelectorAll('.btn-ai-shortcut').forEach(btn => {
    btn.onclick = () => {
      const query = btn.getAttribute('data-query');
      sendQuery(query);
    };
  });
}
