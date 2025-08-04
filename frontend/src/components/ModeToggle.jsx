/**
 * Mode Toggle Component for Leo AI Assistant
 * Modern toggle switch between Agent and Assistant modes
 */

import React, { useState } from 'react';
import ThemeToggle from './ThemeToggle';
import SettingsModal from './SettingsModal';

const ModeToggle = ({ currentMode, onModeChange, isConnected }) => {
  const [showSettings, setShowSettings] = useState(false);

  const handleModeChange = (newMode) => {
    if (onModeChange) {
      onModeChange(newMode);
    }
  };

  return (
    <div className="flex items-center space-x-3">
      <button
        onClick={() => setShowSettings(true)}
        className="w-10 h-10 rounded-lg transition-all duration-200 flex items-center justify-center bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600 hover:scale-105 active:scale-95"
        title="Settings"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>
      <ThemeToggle size="md" />
      <div className="flex items-center justify-center p-1 bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-600 transition-colors duration-300">
      <button
        onClick={() => handleModeChange('agent')}
        className={`
          relative px-6 py-3 rounded-xl font-medium text-sm transition-all duration-300
          flex items-center space-x-2 min-w-[120px] justify-center
          ${currentMode === 'agent' 
            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg' 
            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
          }
        `}
        disabled={!isConnected}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span>Agent</span>
        {currentMode === 'agent' && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse" />
        )}
      </button>
      
      <button
        onClick={() => handleModeChange('assistant')}
        className={`
          relative px-6 py-3 rounded-xl font-medium text-sm transition-all duration-300
          flex items-center space-x-2 min-w-[120px] justify-center
          ${currentMode === 'assistant' 
            ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg' 
            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
          }
        `}
        disabled={!isConnected}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <span>Assistant</span>
        {currentMode === 'assistant' && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse" />
        )}
      </button>
      </div>
      
      {/* Settings Modal */}
      <SettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </div>
  );
};

export default ModeToggle;