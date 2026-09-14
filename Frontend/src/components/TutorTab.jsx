import { useState, useEffect } from 'react';
import api from '../services/api';

export default function TutorTab({ projectId }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    api.get(`/tutor/conversations/${projectId}`).then((res) => {
      const conversations = res.data;
      if (conversations.length > 0) {
        const latest = conversations[conversations.length - 1];
        setConversationId(latest._id);
        const loadedMessages = latest.messages.flatMap((m) => [
          { role: 'user', text: m.question },
          { role: 'tutor', text: m.answer, sources: m.sources },
        ]);
        setMessages(loadedMessages);
      }
    });
  }, [projectId]);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: 'user', text: question };
    setMessages((prev) => [...prev, userMessage]);
    setAsking(true);
    setQuestion('');

    const res = await api.post('/tutor/ask', {
      project_id: projectId,
      conversation_id: conversationId,
      question: userMessage.text,
    });

    setConversationId(res.data.conversation_id);
    setMessages((prev) => [
      ...prev,
      { role: 'tutor', text: res.data.answer, sources: res.data.sources },
    ]);
    setAsking(false);
  };

  return (
    <div>
      <div
        className="border rounded p-3 mb-3"
        style={{ height: '400px', overflowY: 'auto', backgroundColor: '#f8f9fa' }}
      >
        {messages.length === 0 && (
          <p className="text-muted">Ask a question about your uploaded materials to get started.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`mb-2 d-flex ${m.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}>
            <div
              className={`p-2 rounded ${m.role === 'user' ? 'bg-primary text-white' : 'bg-white border'}`}
              style={{ maxWidth: '75%' }}
            >
              <div>{m.text}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-1">
                  {m.sources.map((s, j) => (
                    <span key={j} className="badge bg-light text-dark border me-1">
                      {s.material_name} — Page {s.page}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {asking && <p className="text-muted">Tutor is thinking...</p>}
      </div>

      <form onSubmit={handleAsk} className="d-flex gap-2">
        <input
          className="form-control"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={asking}
        />
        <button className="btn btn-primary" type="submit" disabled={asking}>
          Send
        </button>
      </form>
    </div>
  );
}