import { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Minimize2 } from 'lucide-react';
import { chatAPI } from '../services/api';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      sendInitialGreeting();
    }
  }, [isOpen]);

  const sendInitialGreeting = async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.sendMessage('Hi', null);
      setSessionId(response.session_id);
      setMessages([
        {
          role: 'assistant',
          content: response.response,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error('Error sending initial greeting:', error);
      setMessages([
        {
          role: 'assistant',
          content: "Hi! I'm having trouble connecting. Please try again in a moment.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(inputMessage, sessionId);
      
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: "I apologize, but I'm having trouble processing your message. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setIsMinimized(false);
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div
          className={`mb-4 bg-white rounded-2xl shadow-2xl transition-all duration-300 ${
            isMinimized ? 'h-16' : 'h-[600px]'
          } w-[380px] flex flex-col overflow-hidden slide-up`}
        >
          <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl">🏡</span>
              </div>
              <div>
                <h3 className="font-semibold text-lg">Maya</h3>
                <p className="text-xs text-red-200">DreamHome Realty Assistant</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={toggleMinimize}
                className="hover:bg-purple-700 p-2 rounded-lg transition"
              >
                <Minimize2 size={18} />
              </button>
              <button
                onClick={toggleChat}
                className="hover:bg-purple-700 p-2 rounded-lg transition"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 chat-messages">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    } message-fade-in`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-purple-600 text-white rounded-br-none'
                          : 'bg-white text-gray-800 shadow-md rounded-bl-none'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p
                        className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-purple-200' : 'text-gray-400'
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-md">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full typing-dot"></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full typing-dot"></div>
                        <div className="w-2 h-2 bg-purple-400 rounded-full typing-dot"></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 bg-white border-t">
                <form onSubmit={sendMessage} className="flex gap-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !inputMessage.trim()}
                    className="bg-purple-600 text-white px-5 py-3 rounded-xl hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    <Send size={20} />
                  </button>
                </form>
                <p className="text-xs text-gray-400 mt-2 text-center">
                  Powered by AI • Your data is secure
                </p>
              </div>
            </>
          )}
        </div>
      )}

      <button
        onClick={toggleChat}
        className="bg-gradient-to-r from-purple-600 to-purple-800 text-white w-16 h-16 rounded-full shadow-2xl hover:shadow-purple-500/50 hover:scale-110 transition-all duration-300 flex items-center justify-center"
      >
        {isOpen ? <X size={28} /> : <MessageCircle size={28} />}
      </button>

      {!isOpen && (
        <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold animate-pulse">
          1
        </div>
      )}
    </div>
  );
};

export default ChatWidget;