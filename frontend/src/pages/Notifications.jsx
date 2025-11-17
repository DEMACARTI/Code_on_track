import React, { useState, useEffect } from 'react'
import apiService from '../services/apiService'

function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending')

  useEffect(() => {
    fetchNotifications()
  }, [filter])

  const fetchNotifications = async () => {
    try {
      const data = await apiService.getNotifications({ status: filter, limit: 50 })
      setNotifications(data.notifications)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching notifications:', error)
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (id, newStatus) => {
    try {
      await apiService.updateNotificationStatus(id, newStatus)
      fetchNotifications()
    } catch (error) {
      console.error('Error updating notification:', error)
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <h2 style={{ marginBottom: '24px' }}>Notifications & Alerts</h2>

      <div className="card">
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            className={`button ${filter === 'pending' ? 'button-primary' : 'button-secondary'}`}
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
          <button
            className={`button ${filter === 'acknowledged' ? 'button-primary' : 'button-secondary'}`}
            onClick={() => setFilter('acknowledged')}
          >
            Acknowledged
          </button>
          <button
            className={`button ${filter === 'resolved' ? 'button-primary' : 'button-secondary'}`}
            onClick={() => setFilter('resolved')}
          >
            Resolved
          </button>
          <button
            className={`button ${filter === '' ? 'button-primary' : 'button-secondary'}`}
            onClick={() => setFilter('')}
          >
            All
          </button>
        </div>

        {notifications.length === 0 ? (
          <p>No notifications found</p>
        ) : (
          <div>
            {notifications.map((notification) => (
              <div
                key={notification._id}
                className="card"
                style={{
                  marginBottom: '16px',
                  borderLeft: `4px solid ${getPriorityColor(notification.priority)}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                      <h3>{notification.title}</h3>
                      <span className={`badge badge-${getTypeBadge(notification.type)}`}>
                        {notification.type}
                      </span>
                      <span className={`badge badge-${getPriorityBadge(notification.priority)}`}>
                        {notification.priority}
                      </span>
                      {notification.llmGenerated && (
                        <span className="badge" style={{ backgroundColor: '#9c27b0', color: 'white' }}>
                          🤖 AI Generated
                        </span>
                      )}
                    </div>
                    
                    <p style={{ color: '#666', marginBottom: '12px' }}>{notification.message}</p>
                    
                    <div style={{ fontSize: '14px', color: '#999' }}>
                      <p>QR ID: {notification.qrId}</p>
                      <p>Created: {new Date(notification.createdAt).toLocaleString()}</p>
                      {notification.assignedTo && <p>Assigned to: {notification.assignedTo}</p>}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {notification.status === 'pending' && (
                      <>
                        <button
                          className="button button-primary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                          onClick={() => handleStatusUpdate(notification._id, 'acknowledged')}
                        >
                          Acknowledge
                        </button>
                        <button
                          className="button button-secondary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                          onClick={() => handleStatusUpdate(notification._id, 'resolved')}
                        >
                          Resolve
                        </button>
                      </>
                    )}
                    {notification.status === 'acknowledged' && (
                      <button
                        className="button button-primary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => handleStatusUpdate(notification._id, 'resolved')}
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
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

function getTypeBadge(type) {
  const badges = {
    maintenance: 'warning',
    alert: 'danger',
    suggestion: 'info',
    insight: 'success',
    anomaly: 'danger',
  }
  return badges[type] || 'info'
}

export default Notifications
