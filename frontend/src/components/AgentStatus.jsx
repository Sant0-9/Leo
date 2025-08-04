/**
 * Agent Status Component for Leo AI Assistant
 * Modern, responsive display of real-time Agent Mode status with API integrations
 */

import React, { useState, useEffect } from 'react';
import { agentAPI } from '../services/api';
import CalendarModal from './CalendarModal';

const AgentStatus = ({ lastMessage, isConnected }) => {
  const [agentStatus, setAgentStatus] = useState({
    is_active: false,
    status: 'inactive',
    update_interval: 45,
    connected_clients: 0,
    last_update: null
  });
  
  const [currentMessage, setCurrentMessage] = useState('Initializing Agent Mode...');
  const [metrics, setMetrics] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const [apiData, setApiData] = useState({
    calendar: null,
    weather: null,
    gmail: null,
    last_updated: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCalendarModal, setShowCalendarModal] = useState(false);

  // Fetch initial agent status
  useEffect(() => {
    const fetchAgentStatus = async () => {
      try {
        setLoading(true);
        const status = await agentAPI.getStatus();
        setAgentStatus(status);
        
        if (status.is_active) {
          setCurrentMessage('Agent Mode is active and monitoring...');
        } else {
          setCurrentMessage('Agent Mode is inactive');
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching agent status:', err);
        setError('Failed to connect to Agent Mode');
        setCurrentMessage('Connection error - retrying...');
      } finally {
        setLoading(false);
      }
    };

    fetchAgentStatus();
    const statusInterval = setInterval(fetchAgentStatus, 30000);
    return () => clearInterval(statusInterval);
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const { type, message, metrics: newMetrics, timestamp } = lastMessage;
      
      switch (type) {
        case 'agent_status':
          setCurrentMessage(message || 'Agent Mode active');
          if (newMetrics) {
            setMetrics(newMetrics);
          }
          
          setRecentActivities(prev => [
            {
              id: Date.now(),
              type: 'status',
              message,
              timestamp: new Date(timestamp).toLocaleTimeString(),
              metrics: newMetrics
            },
            ...prev.slice(0, 4)
          ]);
          break;
          
        case 'task_completed':
          const taskMessage = `Task completed: ${lastMessage.task_name}`;
          setRecentActivities(prev => [
            {
              id: Date.now(),
              type: 'task',
              message: taskMessage,
              timestamp: new Date(timestamp).toLocaleTimeString(),
              duration: lastMessage.duration_seconds
            },
            ...prev.slice(0, 4)
          ]);
          break;
          
        case 'insight_generated':
          setRecentActivities(prev => [
            {
              id: Date.now(),
              type: 'insight',
              message: lastMessage.insight,
              timestamp: new Date(timestamp).toLocaleTimeString(),
              confidence: lastMessage.confidence,
              category: lastMessage.category
            },
            ...prev.slice(0, 4)
          ]);
          break;
          
        case 'api_data_updated':
          if (lastMessage.data) {
            setApiData(prev => ({
              ...prev,
              ...lastMessage.data,
              last_updated: timestamp
            }));
            
            setRecentActivities(prev => [
              {
                id: Date.now(),
                type: 'api_update',
                message: lastMessage.message || 'API data refreshed',
                timestamp: new Date(timestamp).toLocaleTimeString(),
                apiData: lastMessage.data
              },
              ...prev.slice(0, 4)
            ]);
          }
          break;
          
        case 'connection':
          setCurrentMessage('Connected to Leo Assistant');
          break;
          
        default:
          break;
      }
    }
  }, [lastMessage]);

  const handleTriggerUpdate = async () => {
    try {
      await agentAPI.triggerUpdate();
    } catch (err) {
      console.error('Error triggering update:', err);
    }
  };

  const handleGenerateInsight = async () => {
    try {
      await agentAPI.generateInsight();
    } catch (err) {
      console.error('Error generating insight:', err);
    }
  };

  const formatNumber = (num) => {
    return typeof num === 'number' ? num.toLocaleString() : num;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <div className="w-6 h-6 mr-2 animate-spin">🤖</div>
            Agent Mode
          </h2>
          <div className="status-badge status-loading">Loading...</div>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            🤖 Agent Mode
          </h2>
          <div className="flex items-center space-x-3">
            <div className={`status-badge ${agentStatus.is_active ? 'status-online' : 'status-offline'}`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${agentStatus.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
              {agentStatus.is_active ? 'Active' : 'Inactive'}
            </div>
            <div className={`status-badge ${isConnected ? 'status-online' : 'status-offline'}`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              WebSocket
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <div className="flex items-center text-red-700">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                💭
              </div>
            </div>
            <div className="flex-1">
              <p className="text-gray-700 font-medium">{currentMessage}</p>
              {agentStatus.is_active && (
                <p className="text-sm text-gray-500 mt-1">
                  Next update in ~{agentStatus.update_interval}s
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      {Object.keys(metrics).length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="text-2xl font-bold text-blue-600">{formatNumber(metrics.tasks_processed)}</div>
            <div className="text-sm text-gray-600">Tasks Processed</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="text-2xl font-bold text-green-600">{metrics.efficiency_score}%</div>
            <div className="text-sm text-gray-600">Efficiency</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="text-2xl font-bold text-purple-600">{metrics.active_processes}</div>
            <div className="text-sm text-gray-600">Active Processes</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="text-2xl font-bold text-orange-600">{metrics.insights_generated}</div>
            <div className="text-sm text-gray-600">Insights Generated</div>
          </div>
        </div>
      )}

      {/* API Integrations */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            🔗 API Integrations
          </h3>
          {apiData.last_updated && (
            <div className="text-sm text-gray-500">
              Updated: {new Date(apiData.last_updated).toLocaleTimeString()}
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Calendar */}
          <div 
            className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200 cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-105"
            onClick={() => setShowCalendarModal(true)}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">📅</span>
                <span className="font-medium text-gray-900">Calendar</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  apiData.calendar?.status === 'healthy' ? 'bg-green-500' : 
                  apiData.calendar?.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                }`}></div>
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
            </div>
            {apiData.calendar?.status === 'healthy' ? (
              <div className="space-y-2">
                <div className="text-2xl font-bold text-blue-700">{apiData.calendar.total_count}</div>
                <div className="text-sm text-blue-600">Upcoming Events</div>
                {apiData.calendar.upcoming_events?.length > 0 && (
                  <div className="text-xs text-gray-600 truncate">
                    📌 {apiData.calendar.upcoming_events[0].title}
                  </div>
                )}
                <div className="text-xs text-blue-500 font-medium">Click to view all</div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-sm text-gray-500">
                  {apiData.calendar?.error || 'Not connected'}
                </div>
                <div className="text-xs text-blue-500 font-medium">Click to view demo</div>
              </div>
            )}
          </div>

          {/* Weather */}
          <div className="bg-gradient-to-br from-yellow-50 to-orange-100 rounded-xl p-4 border border-yellow-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🌤️</span>
                <span className="font-medium text-gray-900">Weather</span>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                apiData.weather?.status === 'healthy' ? 'bg-green-500' : 
                apiData.weather?.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
              }`}></div>
            </div>
            {apiData.weather?.status === 'healthy' ? (
              <div className="space-y-2">
                <div className="text-2xl font-bold text-orange-700">
                  {Math.round(apiData.weather.current?.temperature)}°
                </div>
                <div className="text-sm text-orange-600">{apiData.weather.location}</div>
                <div className="text-xs text-gray-600">
                  {apiData.weather.current?.description}
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">
                {apiData.weather?.error || 'Not connected'}
              </div>
            )}
          </div>

          {/* Gmail */}
          <div className="bg-gradient-to-br from-red-50 to-pink-100 rounded-xl p-4 border border-red-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">📧</span>
                <span className="font-medium text-gray-900">Gmail</span>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                apiData.gmail?.status === 'healthy' ? 'bg-green-500' : 
                apiData.gmail?.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
              }`}></div>
            </div>
            {apiData.gmail?.status === 'healthy' ? (
              <div className="space-y-2">
                <div className="text-2xl font-bold text-red-700">{apiData.gmail.unread_count}</div>
                <div className="text-sm text-red-600">Unread Emails</div>
                <div className="text-xs text-gray-600">
                  📮 {apiData.gmail.today_count} emails today
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">
                {apiData.gmail?.error || 'Not connected'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        {recentActivities.length > 0 ? (
          <div className="space-y-3">
            {recentActivities.map((activity) => (
              <div key={activity.id} className={`p-3 rounded-lg border-l-4 ${
                activity.type === 'task' ? 'bg-green-50 border-green-500' :
                activity.type === 'insight' ? 'bg-purple-50 border-purple-500' :
                activity.type === 'api_update' ? 'bg-blue-50 border-blue-500' :
                'bg-gray-50 border-gray-500'
              }`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                  </div>
                  {activity.confidence && (
                    <div className="text-xs bg-white rounded-full px-2 py-1 text-gray-600">
                      {activity.confidence}% confidence
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔍</div>
            <p>No recent activities</p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <button 
            onClick={handleTriggerUpdate}
            disabled={!agentStatus.is_active}
            className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Trigger Update
          </button>
          <button 
            onClick={handleGenerateInsight}
            disabled={!agentStatus.is_active}
            className="btn-secondary flex-1 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Generate Insight
          </button>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{agentStatus.connected_clients}</div>
            <div className="text-sm text-gray-600">Connected Clients</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{agentStatus.update_interval}s</div>
            <div className="text-sm text-gray-600">Update Interval</div>
          </div>
          {agentStatus.last_update && (
            <div className="text-center">
              <div className="text-sm font-medium text-gray-900">
                {new Date(agentStatus.last_update).toLocaleTimeString()}
              </div>
              <div className="text-sm text-gray-600">Last Update</div>
            </div>
          )}
        </div>
      </div>

      {/* Calendar Modal */}
      <CalendarModal 
        isOpen={showCalendarModal} 
        onClose={() => setShowCalendarModal(false)} 
      />
    </div>
  );
};

export default AgentStatus;