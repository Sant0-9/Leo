/**
 * Leo AI Assistant - Main App Component
 */

import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import Home from './pages/Home';
import Assistant from './pages/Assistant';
import { healthAPI } from './services/api';
import NotificationSystem from './components/NotificationSystem';

function App() {
  const [currentMode, setCurrentMode] = useState('agent');
  const [backendStatus, setBackendStatus] = useState('checking');
  
  const {
    isConnected,
    lastMessage,
    connectionError,
    reconnectAttempts,
    maxReconnectAttempts
  } = useWebSocket();

  // Check backend health on startup
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        await healthAPI.check();
        setBackendStatus('healthy');
      } catch (error) {
        console.error('Backend health check failed:', error);
        setBackendStatus('error');
      }
    };

    checkBackendHealth();
    const healthInterval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(healthInterval);
  }, []);

  const handleModeChange = (newMode) => {
    setCurrentMode(newMode);
  };

  const showConnectionIssues = backendStatus === 'error' || 
    (!isConnected && reconnectAttempts >= maxReconnectAttempts);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
      {/* Connection Status Overlay */}
      {showConnectionIssues && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transition-colors duration-300">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.962-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 transition-colors duration-300">Connection Issues</h3>
              <div className="text-gray-600 dark:text-gray-300 space-y-2 mb-6 transition-colors duration-300">
                {backendStatus === 'error' && (
                  <p>Backend server is not responding</p>
                )}
                {connectionError && (
                  <p>WebSocket: {connectionError}</p>
                )}
                {reconnectAttempts >= maxReconnectAttempts && (
                  <p>Max reconnection attempts reached</p>
                )}
              </div>
              <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
                <p className="text-sm text-gray-700 mb-2">Make sure the backend server is running:</p>
                <code className="text-sm bg-gray-800 text-green-400 px-3 py-2 rounded block">
                  python3 mock_backend.py
                </code>
              </div>
              <button 
                onClick={() => window.location.reload()} 
                className="btn-primary w-full"
              >
                <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main App Content */}
      <div className={`transition-all duration-300 ${showConnectionIssues ? 'blur-sm' : ''}`}>
        {currentMode === 'agent' ? (
          <Home 
            onModeChange={handleModeChange}
            lastMessage={lastMessage}
            isConnected={isConnected}
          />
        ) : (
          <Assistant 
            onModeChange={handleModeChange}
            isConnected={isConnected}
          />
        )}
      </div>

      {/* Development Info */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 left-4 bg-gray-900 text-white text-xs p-3 rounded-lg shadow-lg opacity-75 hover:opacity-100 transition-opacity">
          <div className="space-y-1">
            <div>Backend: <span className={backendStatus === 'healthy' ? 'text-green-400' : 'text-red-400'}>{backendStatus}</span></div>
            <div>WebSocket: <span className={isConnected ? 'text-green-400' : 'text-red-400'}>{isConnected ? 'Connected' : 'Disconnected'}</span></div>
            <div>Mode: <span className="text-blue-400">{currentMode}</span></div>
            {reconnectAttempts > 0 && (
              <div>Reconnects: <span className="text-yellow-400">{reconnectAttempts}/{maxReconnectAttempts}</span></div>
            )}
          </div>
        </div>
      )}
      
      {/* Notification System */}
      <NotificationSystem />
    </div>
  );
}

export default App;