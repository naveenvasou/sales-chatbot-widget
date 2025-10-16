import { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Minimize2, Home } from 'lucide-react';
import { chatAPI } from '../services/api';
import CategoryButtons from './ui/CategoryButtons';
import ActionButtons from './ui/ActionButtons';
import LeadForm from './ui/LeadForm';
import PreferenceForm from './ui/PreferenceForm';
import NumberConfirmation from './ui/NumberConfirmation';
import PropertyCards from './ui/PropertyCards';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentState, setCurrentState] = useState(null);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [showMenuButton, setShowMenuButton] = useState(false);
  const [aiQuery, setAiQuery] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      initializeChat();
    }
  }, [isOpen]);

  const initializeChat = async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.init();
      setSessionId(response.session_id);
      setCurrentState(response.current_state);
      setShowMenuButton(response.show_menu_button);
      
      addMessage({
        role: 'assistant',
        content: response.message,
        uiComponent: response.ui_component,
      });
    } catch (error) {
      console.error('Init error:', error);
      addMessage({
        role: 'assistant',
        content: "Hi! I'm having trouble connecting. Please refresh and try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = (message) => {
    setMessages((prev) => [...prev, { ...message, timestamp: new Date() }]);
    
    // If no UI component but should show continue button
    /* if (!message.uiComponent && message.role === 'assistant') {
      // Check if we should auto-show a continue button
      setTimeout(() => {
        setMessages((prev) => {
          const lastMsg = prev[prev.length - 1];
          if (!lastMsg.uiComponent && lastMsg.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMsg,
                uiComponent: {
                  type: 'buttons',
                  data: {
                    options: [{ value: 'continue', label: '✅ Continue' }]
                  }
                }
              }
            ];
          }
          return prev;
        });
      }, 500);
    } */
  };

  const handleCategorySelect = async (category) => {
    setCurrentCategory(category.id);
    addMessage({ role: 'user', content: `${category.label}` });
    setIsLoading(true);

    try {
      const response = await chatAPI.selectCategory(sessionId, category);
      setCurrentState(response.current_state);
      setShowMenuButton(response.show_menu_button);
      
      addMessage({
        role: 'assistant',
        content: response.message,
        uiComponent: response.ui_component,
      });

      console.log(response.ui_component)

      if (!response.ui_component) {
        const next_response = await chatAPI.sendInput(sessionId, response.current_state, 'assisstant', 'continue');
        setCurrentState(next_response.current_state);
        setShowMenuButton(next_response.show_menu_button);
        addMessage({
        role: 'assistant',
        content: next_response.message,
        uiComponent: next_response.ui_component,
        });
      }
      
    } catch (error) {
      console.error('Category error:', error);
      addMessage({ role: 'assistant', content: 'Error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLeadSubmit = async (formData) => {
    addMessage({ role: 'user', content: `Submitted contact info` });
    setIsLoading(true);

    try {
      const response = await chatAPI.submitLead(
        sessionId,
        currentCategory,
        formData.name,
        formData.email,
        formData.phone
      );
      
      setCurrentState(response.current_state);
      setShowMenuButton(response.show_menu_button);
      
      addMessage({
        role: 'assistant',
        content: response.message,
        uiComponent: response.ui_component,
      });

      if (!response.ui_component) {
        const next_response = await chatAPI.sendInput(sessionId, response.current_state, 'assisstant', 'continue');
        setCurrentState(next_response.current_state);
        setShowMenuButton(next_response.show_menu_button);
        addMessage({
        role: 'assistant',
        content: next_response.message,
        uiComponent: next_response.ui_component,
        });
      }


    } catch (error) {
      console.error('Lead submit error:', error);
      addMessage({ role: 'assistant', content: 'Please check your information and try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUserInput = async (inputType, inputData) => {
    // Add user message
    const userMessage = typeof inputData === 'string' ? inputData : inputData.label;
    addMessage({ role: 'user', content: userMessage });
    setIsLoading(true);

    try {
      const response = await chatAPI.sendInput(sessionId, currentState, inputType, inputData);
      setCurrentState(response.current_state);
      setShowMenuButton(response.show_menu_button);
      
      addMessage({
        role: 'assistant',
        content: response.message,
        uiComponent: response.ui_component,
      });
    } catch (error) {
      console.error('Input error:', error);
      addMessage({ role: 'assistant', content: 'Something went wrong. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToMenu = async () => {
    addMessage({ role: 'user', content: 'Back to main menu' });
    setIsLoading(true);

    try {
      const response = await chatAPI.backToMenu(sessionId);
      setCurrentState(response.current_state);
      setShowMenuButton(false);
      setCurrentCategory(null);
      
      addMessage({
        role: 'assistant',
        content: response.message,
        uiComponent: response.ui_component,
      });
    } catch (error) {
      console.error('Menu error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAIQuestion = async (e) => {
    e.preventDefault();
    if (!aiQuery.trim()) return;
    
    const question = aiQuery;
    setAiQuery(''); // Clear input
    
    addMessage({ role: 'user', content: question });
    setIsLoading(true);
    
    try {
      const response = await chatAPI.askAI(sessionId, question);
      
      addMessage({
        role: 'assistant',
        content: response.message,
        uiComponent: response.ui_component,
      });
    } catch (error) {
      console.error('AI question error:', error);
      addMessage({ 
        role: 'assistant', 
        content: 'Sorry, I had trouble processing that. Could you rephrase?' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderUIComponent = (component) => {
    if (!component) return null;

    switch (component.type) {
      case 'category_buttons':
        return (
          <CategoryButtons
            categories={component.data.categories}
            onSelect={handleCategorySelect}
            disabled={isLoading}
          />
        );

      case 'lead_form':
        return (
          <LeadForm
            fields={component.data.fields}
            onSubmit={handleLeadSubmit}
            disabled={isLoading}
          />
        );

      case 'preference_form':
        return (
          <PreferenceForm
            fields={component.data.fields}
            onSubmit={(data) => handleUserInput('form', data)}
            disabled={isLoading}
          />
        );

      case 'buttons':
        return (
          <ActionButtons
            options={component.data.options}
            onSelect={(value) => handleUserInput('button', value)}
            disabled={isLoading}
          />
        );
        
        case 'property_cards':
          return (
            <PropertyCards
              propertyType={component.data.property_type}
              filtered={component.data.filtered}
              preferences={component.data.preferences}
              onAction={async (action, propertyId) => {
                addMessage({ role: 'user', content: `Requested ${action} for property` });
                setIsLoading(true);
                try {
                  const response = await chatAPI.propertyAction(sessionId, action, propertyId);
                  setCurrentState(response.current_state);
                  setShowMenuButton(response.show_menu_button);
                  addMessage({
                    role: 'assistant',
                    content: response.message,
                    uiComponent: response.ui_component,
                  });
                } catch (error) {
                  console.error('Property action error:', error);
                  addMessage({ role: 'assistant', content: 'Error occurred. Please try again.' });
                } finally {
                  setIsLoading(false);
                }
              }}
              onShowMore={() => handleUserInput('button', 'show_more')}
            />
          );

          case 'number_confirmation':
            return (
              <NumberConfirmation
                fields={component.data.fields}
                onSubmit={(data) => handleUserInput('number_confirmation', data)}
                disabled={isLoading}
              />
            );

      default:
        return null;
    }
  };
  // ... (previous code above)

  return (
    <div className="fixed bottom-4 right-4 left-4 md:bottom-6 md:right-6 md:left-auto z-50 flex flex-col items-end">
      {isOpen && (
        <div
          className={`bg-white rounded-2xl shadow-2xl transition-all duration-300 ${
            isMinimized ? 'h-16' : 'h-[600px]'
          } w-full md:w-[380px] md:mb-4 flex flex-col overflow-hidden slide-up`}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl">🏡</span>
              </div>
              <div>
                <h3 className="font-semibold text-lg">Maya</h3>
                <p className="text-xs text-purple-200">DreamHome Assistant</p>
              </div>
            </div>
            <div className="flex gap-2">
              {showMenuButton && (
                <button
                  onClick={handleBackToMenu}
                  className="hover:bg-purple-700 p-2 rounded-lg transition"
                  title="Back to Menu"
                >
                  <Home size={18} />
                </button>
              )}
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="hover:bg-purple-700 p-2 rounded-lg transition"
              >
                <Minimize2 size={18} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-purple-700 p-2 rounded-lg transition"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          {!isMinimized && (
            <>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 chat-messages overscroll-y-contain">
              {messages.map((message, index) => (
                <div key={index} className="message-fade-in">
                  {message.role === 'user' ? (
                    <div className="flex justify-end">
                      <div className="max-w-[80%] bg-purple-600 text-white rounded-2xl rounded-br-none px-4 py-3">
                        <p className="text-sm">{message.content}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-start">
                      <div className="max-w-[85%] bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-md">
                        <p className="text-sm text-gray-800 whitespace-pre-wrap">
                          {message.content}
                        </p>
                        {message.uiComponent && (
                          <div className="mt-3">
                            {renderUIComponent(message.uiComponent)}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Typing Indicator */}
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

            {/* Persistent AI Input */}
            <div className="border-t border-gray-200 p-3 bg-white">
              <form onSubmit={handleAIQuestion} className="flex gap-2">
                <input
                  type="text"
                  value={aiQuery}
                  onChange={(e) => setAiQuery(e.target.value)}
                  placeholder="Ask me anything about properties..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none text-sm"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !aiQuery.trim()}
                  className="bg-purple-600 text-white p-2 rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                >
                  <Send size={20} />
                </button>
              </form>
            </div>
            </>
          )}
        </div>
      )}

      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="bg-gradient-to-r from-purple-600 to-purple-800 text-white w-16 h-16 rounded-full shadow-2xl hover:shadow-purple-500/50 hover:scale-110 transition-all duration-300 flex items-center justify-center self-end"
        >
          {!isOpen && <MessageCircle size={28} />}
        </button>
      )}
      {!isOpen && (
        <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold animate-pulse">
          1
        </div>
      )}
    </div>
  );
};

export default ChatWidget;