import React, { useState, useEffect } from 'react'
import apiService from '../services/apiService'

function Dashboard() {
  const [stats, setStats] = useState({
    totalQRCodes: 0,
    activeQRCodes: 0,
    totalScans: 0,
    totalRecords: 0,
  })
  const [recentNotifications, setRecentNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const analytics = await apiService.getAnalytics()
      setStats(analytics.analytics)

      const notifications = await apiService.getNotifications({ limit: 5 })
      setRecentNotifications(notifications.notifications)
      
      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <h2 style={{ marginBottom: '24px' }}>Dashboard Overview</h2>
      
      <div className="grid grid-4">
        <div className="card">
          <h3 style={{ color: '#007bff', marginBottom: '10px' }}>Total QR Codes</h3>
          <p style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.totalQRCodes}</p>
        </div>
        
        <div className="card">
          <h3 style={{ color: '#28a745', marginBottom: '10px' }}>Active QR Codes</h3>
          <p style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.activeQRCodes}</p>
        </div>
        
        <div className="card">
          <h3 style={{ color: '#ffc107', marginBottom: '10px' }}>Total Scans</h3>
          <p style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.totalScans}</p>
        </div>
        
        <div className="card">
          <h3 style={{ color: '#17a2b8', marginBottom: '10px' }}>Data Records</h3>
          <p style={{ fontSize: '36px', fontWeight: 'bold' }}>{stats.totalRecords}</p>
        </div>
      </div>

      <div className="card" style={{ marginTop: '30px' }}>
        <h3 style={{ marginBottom: '20px' }}>Recent Notifications</h3>
        {recentNotifications.length === 0 ? (
          <p>No notifications available</p>
        ) : (
          <div>
            {recentNotifications.map((notification) => (
              <div
                key={notification._id}
                style={{
                  padding: '16px',
                  borderLeft: `4px solid ${getPriorityColor(notification.priority)}`,
                  backgroundColor: '#f8f9fa',
                  marginBottom: '12px',
                  borderRadius: '4px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h4 style={{ marginBottom: '8px' }}>{notification.title}</h4>
                    <p style={{ color: '#666', fontSize: '14px' }}>{notification.message}</p>
                  </div>
                  <span className={`badge badge-${getPriorityBadge(notification.priority)}`}>
                    {notification.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '20px' }}>System Features</h3>
        <div className="grid grid-2">
          <div style={{ padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <h4 style={{ marginBottom: '8px' }}>🔍 QR Code Generation</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Generate QR codes optimized for various materials and dimensions with engraving specifications.
            </p>
          </div>
          
          <div style={{ padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <h4 style={{ marginBottom: '8px' }}>🤖 LLM Integration</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              AI-powered insights and recommendations for maintenance, anomaly detection, and optimization.
            </p>
          </div>
          
          <div style={{ padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <h4 style={{ marginBottom: '8px' }}>📱 Mobile Scanning</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Mobile app for field staff to scan QR codes and record maintenance activities in real-time.
            </p>
          </div>
          
          <div style={{ padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <h4 style={{ marginBottom: '8px' }}>📊 Analytics Dashboard</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Comprehensive analytics and reporting on QR code usage, maintenance patterns, and system health.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function getPriorityColor(priority) {
  const colors = {
    critical: '#dc3545',
    high: '#ffc107',
    medium: '#17a2b8',
    low: '#28a745',
  }
  return colors[priority] || '#6c757d'
}

function getPriorityBadge(priority) {
  const badges = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'success',
  }
  return badges[priority] || 'info'
}

export default Dashboard
