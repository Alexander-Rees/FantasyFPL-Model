import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./RAGChat.css";

const RAGChat = ({ teamContext }) => {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMessage = query.trim();
    setQuery("");
    setError("");
    setLoading(true);

    // Add user message to chat
    const newMessages = [...messages, { role: "user", content: userMessage }];
    setMessages(newMessages);

    try {
      // Call LLM service - use environment variable or default to localhost
      const llmApiUrl = process.env.REACT_APP_LLM_API_URL || "http://localhost:5002";
      
      // Build request with optional team context
      const requestBody = {
        query: userMessage,
        include_sources: true,
      };
      
      // Add team context if available
      if (teamContext) {
        requestBody.user_context = {
          team_players: teamContext.players || [],
          budget: teamContext.budget,
          free_transfers: teamContext.freeTransfers,
        };
      }
      
      const response = await axios.post(`${llmApiUrl}/api/v1/query`, requestBody);

      // Add assistant response
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: response.data.answer,
          sources: response.data.sources || [],
        },
      ]);
    } catch (err) {
      console.error("RAG query error:", err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to get response. Make sure the LLM service is running on port 5002."
      );
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: "Sorry, I couldn't process your question. Please try again.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError("");
  };

  return (
    <div className="rag-chat-container">
      <div className="rag-chat-header">
        <h3>🤖 FPL AI Assistant</h3>
        <p className="rag-chat-subtitle">
          Ask questions about captaincy, transfers, players, and more!
        </p>
        {messages.length > 0 && (
          <button onClick={clearChat} className="clear-chat-button">
            Clear Chat
          </button>
        )}
      </div>

      <div className="rag-chat-messages">
        {messages.length === 0 ? (
          <div className="rag-chat-empty">
            <p>💡 Try asking:</p>
            <ul>
              <li>"Who should I captain this gameweek?"</li>
              <li>"What are the best transfer options?"</li>
              <li>"Which players are in good form?"</li>
              <li>"Should I use my wildcard?"</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`rag-message rag-message-${msg.role} ${
                msg.error ? "rag-message-error" : ""
              }`}
            >
              <div className="rag-message-content">
                {msg.role === "user" ? (
                  <strong>You:</strong>
                ) : (
                  <strong>AI Assistant:</strong>
                )}
                <p>{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="rag-sources">
                    <strong>Sources:</strong>
                    <ul>
                      {msg.sources.slice(0, 3).map((source, i) => (
                        <li key={i}>
                          {source.title} (GW{source.gameweek})
                          {source.relevance && (
                            <span className="relevance">
                              {" "}
                              - {Math.round(source.relevance * 100)}% relevant
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="rag-message rag-message-assistant">
            <div className="rag-message-content">
              <strong>AI Assistant:</strong>
              <p className="rag-loading">
                <span className="rag-loading-dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </span>
              </p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="rag-error">{error}</div>}

      <form onSubmit={handleSubmit} className="rag-chat-input-form">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about FPL..."
          className="rag-chat-input"
          rows="2"
          disabled={loading}
        />
        <button
          type="submit"
          className="rag-chat-submit"
          disabled={loading || !query.trim()}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default RAGChat;

