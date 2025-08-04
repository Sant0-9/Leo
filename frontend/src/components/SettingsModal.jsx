/**
 * Settings Modal Component
 * Provides user settings and preferences
 */

import React, { useState } from 'react';
import { useTheme } from './ThemeProvider';
import { showNotification } from './NotificationSystem';

const SettingsModal = ({ isOpen, onClose }) => {
  const { isDark, toggleTheme } = useTheme();
  const [settings, setSettings] = useState({
    notifications: true,
    autoUpdates: true,
    agentUpdateInterval: 30,
    memoryRetention: 7,
    voiceEnabled: false,
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    showNotification('success', 'Settings Updated', `${key} has been updated`);
  };

  const clearAllData = () => {
    if (window.confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
      localStorage.clear();
      showNotification('info', 'Data Cleared', 'All local data has been cleared');
    }
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify({ settings, theme: isDark ? 'dark' : 'light' }, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'leo-settings.json';
    link.click();
    URL.revokeObjectURL(url);
    showNotification('success', 'Settings Exported', 'Settings have been exported to your downloads');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden transition-colors duration-300">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">⚙️</span>
              <h2 className="text-xl font-semibold">Settings</h2>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-96 space-y-6">
          {/* Appearance */}
          <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Appearance</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Dark Mode</label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Toggle dark/light theme</p>
                </div>
                <button
                  onClick={toggleTheme}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    isDark ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      isDark ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Notifications</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Enable Notifications</label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Receive system notifications</p>
                </div>
                <button
                  onClick={() => handleSettingChange('notifications', !settings.notifications)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    settings.notifications ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      settings.notifications ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Agent Settings */}
          <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Agent Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Auto Updates</label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Automatically update data in agent mode</p>
                </div>
                <button
                  onClick={() => handleSettingChange('autoUpdates', !settings.autoUpdates)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    settings.autoUpdates ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      settings.autoUpdates ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Update Interval (seconds)
                </label>
                <input
                  type="range"
                  min="10"
                  max="120"
                  value={settings.agentUpdateInterval}
                  onChange={(e) => handleSettingChange('agentUpdateInterval', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>10s</span>
                  <span className="font-medium">{settings.agentUpdateInterval}s</span>
                  <span>2m</span>
                </div>
              </div>
            </div>
          </div>

          {/* Memory Settings */}
          <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Memory Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Memory Retention (days)
                </label>
                <input
                  type="range"
                  min="1"
                  max="30"
                  value={settings.memoryRetention}
                  onChange={(e) => handleSettingChange('memoryRetention', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>1 day</span>
                  <span className="font-medium">{settings.memoryRetention} days</span>
                  <span>30 days</span>
                </div>
              </div>
            </div>
          </div>

          {/* Experimental Features */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Experimental</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-900 dark:text-white">Voice Commands</label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Enable voice interaction (coming soon)</p>
                </div>
                <button
                  onClick={() => handleSettingChange('voiceEnabled', !settings.voiceEnabled)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                    settings.voiceEnabled ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                  disabled
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      settings.voiceEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 border-t border-gray-200 dark:border-gray-600 transition-colors duration-300">
          <div className="flex items-center justify-between">
            <div className="flex space-x-3">
              <button
                onClick={exportSettings}
                className="btn-secondary text-sm"
              >
                Export Settings
              </button>
              <button
                onClick={clearAllData}
                className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
              >
                Clear All Data
              </button>
            </div>
            <button
              onClick={onClose}
              className="btn-primary"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;