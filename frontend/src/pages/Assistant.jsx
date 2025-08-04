/**
 * Assistant Page Component for Leo AI Assistant
 * Modern full-screen chat interface
 */

import React from 'react';
import ChatWindow from '../components/ChatWindow';
import ModeToggle from '../components/ModeToggle';

const Assistant = ({ onModeChange, isConnected }) => {
  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="flex-shrink-0 bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center text-lg">
                💬
              </div>
              <h1 className="text-lg font-semibold text-gray-900">Assistant Mode</h1>
            </div>
            
            <ModeToggle 
              currentMode="assistant"
              onModeChange={onModeChange}
              isConnected={isConnected}
            />
          </div>
        </div>
      </div>
      
      {/* Chat Window */}
      <div className="flex-1 bg-white">
        <div className="h-full max-w-7xl mx-auto">
          <ChatWindow isConnected={isConnected} />
        </div>
      </div>
    </div>
  );
};

export default Assistant;