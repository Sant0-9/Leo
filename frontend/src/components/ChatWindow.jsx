/**
 * Chat Window Component for Leo AI Assistant
 * Modern chat interface with enhanced UX and memory integration
 */

import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';

const ChatWindow = ({ isConnected }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [memoryStats, setMemoryStats] = useState({});
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await chatAPI.getHistory(20);
        setMessages(history.messages || []);
        
        // Load memory stats
        const stats = await chatAPI.getMemoryStats();
        setMemoryStats(stats);
      } catch (err) {
        console.error('Error loading conversation history:', err);
        setError('Failed to load conversation history');
      }
    };

    loadHistory();
  }, []);

  // Focus input when component mounts
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Add user message to UI immediately
    const userMsgObj = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
      mode: 'assistant'
    };
    
    setMessages(prev => [...prev, userMsgObj]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatAPI.sendMessage(userMessage);
      
      // Add assistant response to UI
      const assistantMsgObj = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        mode: 'assistant'
      };
      
      setMessages(prev => [...prev, assistantMsgObj]);
      
      // Update memory stats
      const stats = await chatAPI.getMemoryStats();
      setMemoryStats(stats);
      
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message to UI
      const errorMsgObj = {
        id: Date.now().toString() + '_error',
        role: 'system',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        mode: 'assistant'
      };
      
      setMessages(prev => [...prev, errorMsgObj]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = async () => {
    try {
      await chatAPI.clearMemory();
      setMessages([]);
      setMemoryStats({});
      setError(null);
      
      // Add system message
      const systemMsg = {
        id: Date.now().toString(),
        role: 'system',
        content: 'Conversation memory cleared. Starting fresh!',
        timestamp: new Date().toISOString(),
        mode: 'assistant'
      };
      
      setMessages([systemMsg]);
      
    } catch (err) {
      console.error('Error clearing conversation:', err);
      setError('Failed to clear conversation');
    }
  };

  const formatMessageTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getMessageIcon = (role) => {
    switch (role) {
      case 'user':
        return '👤';
      case 'assistant':
        return '🤖';
      case 'system':
        return '🔧';
      default:
        return '💬';
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
            💬
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Leo Assistant</h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-500">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {Object.keys(memoryStats).length > 0 && (
            <div className="hidden sm:flex items-center text-sm text-gray-500 bg-gray-100 rounded-full px-3 py-1">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {memoryStats.total_messages || 0} messages
            </div>
          )}
          <button 
            onClick={clearConversation}
            className="flex items-center space-x-1 text-sm text-gray-500 hover:text-red-600 transition-colors px-3 py-1 rounded-lg hover:bg-red-50"
            title="Clear conversation memory"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span className="hidden sm:inline">Clear</span>
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 m-4 rounded-r-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-red-700">{error}</span>
            </div>
            <button 
              onClick={() => setError(null)} 
              className="text-red-500 hover:text-red-700 ml-4"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-3xl mb-6">
              🧠
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-3">Welcome to Leo Assistant!</h3>
            <p className="text-gray-600 mb-8 max-w-md">
              I'm your AI assistant ready to help with various tasks. Start a conversation by typing a message below or try one of these suggestions:
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              <button 
                onClick={() => handleSuggestionClick("What can you do?")}
                className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-4 py-2 rounded-full text-sm transition-colors"
              >
                What can you do?
              </button>
              <button 
                onClick={() => handleSuggestionClick("Tell me about Agent Mode")}
                className="bg-purple-100 hover:bg-purple-200 text-purple-800 px-4 py-2 rounded-full text-sm transition-colors"
              >
                Tell me about Agent Mode
              </button>
              <button 
                onClick={() => handleSuggestionClick("How does memory work?")}
                className="bg-green-100 hover:bg-green-200 text-green-800 px-4 py-2 rounded-full text-sm transition-colors"
              >
                How does memory work?
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                  message.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : message.role === 'system'
                    ? 'bg-gray-100 text-gray-700'
                    : 'bg-gray-100 text-gray-900'
                } rounded-2xl px-4 py-3 shadow-sm`}>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm">
                      {getMessageIcon(message.role)}
                    </span>
                    <span className="text-xs font-medium opacity-75">
                      {message.role === 'user' ? 'You' : 
                       message.role === 'assistant' ? 'Leo' : 'System'}
                    </span>
                    <span className="text-xs opacity-50">
                      {formatMessageTime(message.timestamp)}
                    </span>
                  </div>
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 rounded-2xl px-4 py-3 shadow-sm max-w-xs lg:max-w-md">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm">🤖</span>
                    <span className="text-xs font-medium opacity-75">Leo</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-xs text-gray-500">Leo is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Container */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message to Leo..."
              className="w-full resize-none border border-gray-300 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32"
              rows="1"
              disabled={isLoading}
              style={{
                minHeight: '48px',
                height: 'auto'
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px';
              }}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className={`flex items-center justify-center w-12 h-12 rounded-full transition-all duration-200 ${
              !inputMessage.trim() || isLoading
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
            }`}
            title="Send message (Enter)"
          >
            {isLoading ? (
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        
        {/* Input Footer */}
        <div className="flex items-center justify-between mt-2 px-1">
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            {memoryStats.session_duration_minutes && (
              <span>Session: {Math.round(memoryStats.session_duration_minutes)}m</span>
            )}
            {memoryStats.memory_usage_percent && (
              <span>Memory: {Math.round(memoryStats.memory_usage_percent)}%</span>
            )}
          </div>
          <div className="text-xs text-gray-400">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;