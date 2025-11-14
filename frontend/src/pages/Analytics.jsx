import React from 'react'

function Analytics() {
  return (
    <div>
      <h2 style={{ marginBottom: '24px' }}>Analytics & Insights</h2>

      <div className="grid grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>QR Code Distribution by Material</h3>
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <p>Chart visualization will be displayed here</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>
              Distribution of QR codes across different material types
            </p>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>Scan Activity Over Time</h3>
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <p>Chart visualization will be displayed here</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>
              Daily scan activity trends and patterns
            </p>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>Status Distribution</h3>
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <p>Chart visualization will be displayed here</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>
              Active, inactive, damaged, and replaced QR codes
            </p>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>Station Coverage</h3>
          <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
            <p>Chart visualization will be displayed here</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>
              QR code deployment across railway stations
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '16px' }}>AI-Generated Insights</h3>
        <div className="grid grid-2">
          <div style={{ padding: '16px', backgroundColor: '#f0f8ff', borderRadius: '4px', borderLeft: '4px solid #007bff' }}>
            <h4 style={{ marginBottom: '8px' }}>🔍 Pattern Detection</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              LLM has detected increased scan frequency at Platform 3, suggesting high usage patterns. Consider additional QR code deployment.
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#fff3cd', borderRadius: '4px', borderLeft: '4px solid #ffc107' }}>
            <h4 style={{ marginBottom: '8px' }}>⚠️ Maintenance Alert</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              5 QR codes require inspection due to age and usage patterns. Schedule maintenance within 7 days.
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#d4edda', borderRadius: '4px', borderLeft: '4px solid #28a745' }}>
            <h4 style={{ marginBottom: '8px' }}>✅ Optimization Opportunity</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Metal-based QR codes showing 15% better durability than plastic. Consider material upgrade for high-traffic areas.
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f8d7da', borderRadius: '4px', borderLeft: '4px solid #dc3545' }}>
            <h4 style={{ marginBottom: '8px' }}>🚨 Anomaly Detected</h4>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Unusual scan pattern detected on QR Code #abc123. Possible security concern requiring immediate attention.
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '16px' }}>Performance Metrics</h3>
        <div className="grid grid-4">
          <div style={{ textAlign: 'center' }}>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>Average Scan Rate</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#007bff' }}>24.5</p>
            <p style={{ fontSize: '14px', color: '#666' }}>scans/day</p>
          </div>

          <div style={{ textAlign: 'center' }}>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>System Uptime</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745' }}>99.8%</p>
            <p style={{ fontSize: '14px', color: '#666' }}>last 30 days</p>
          </div>

          <div style={{ textAlign: 'center' }}>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>LLM Analysis Time</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#17a2b8' }}>1.2s</p>
            <p style={{ fontSize: '14px', color: '#666' }}>average</p>
          </div>

          <div style={{ textAlign: 'center' }}>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>Data Accuracy</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ffc107' }}>98.5%</p>
            <p style={{ fontSize: '14px', color: '#666' }}>validated records</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics
