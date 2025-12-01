import React, { useState, useEffect } from 'react'
import apiService from '../services/apiService'

function QRCodeList() {
  const [qrCodes, setQRCodes] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    status: '',
    materialType: '',
    station: '',
  })

  useEffect(() => {
    fetchQRCodes()
  }, [filters])

  const fetchQRCodes = async () => {
    try {
      const data = await apiService.getQRCodes(filters)
      setQRCodes(data.qrCodes)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching QR codes:', error)
      setLoading(false)
    }
  }

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value })
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>QR Code Management</h2>
        <button className="button button-primary">Generate New QR Code</button>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '16px' }}>Filters</h3>
        <div className="grid grid-3">
          <div>
            <label>Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="damaged">Damaged</option>
              <option value="replaced">Replaced</option>
            </select>
          </div>

          <div>
            <label>Material Type</label>
            <select
              value={filters.materialType}
              onChange={(e) => handleFilterChange('materialType', e.target.value)}
            >
              <option value="">All</option>
              <option value="metal">Metal</option>
              <option value="plastic">Plastic</option>
              <option value="wood">Wood</option>
              <option value="stone">Stone</option>
              <option value="glass">Glass</option>
            </select>
          </div>

          <div>
            <label>Station</label>
            <input
              type="text"
              placeholder="Enter station name"
              value={filters.station}
              onChange={(e) => handleFilterChange('station', e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3 style={{ marginBottom: '16px' }}>QR Codes ({qrCodes.length})</h3>
        {qrCodes.length === 0 ? (
          <p>No QR codes found</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>QR ID</th>
                  <th>Material</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Scans</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {qrCodes.map((qr) => (
                  <tr key={qr._id}>
                    <td style={{ fontFamily: 'monospace' }}>{qr.qrId.substring(0, 8)}...</td>
                    <td>{qr.materialType}</td>
                    <td>
                      {qr.location?.station || 'N/A'}
                      {qr.location?.platform && ` - Platform ${qr.location.platform}`}
                    </td>
                    <td>
                      <span className={`badge badge-${getStatusBadge(qr.status)}`}>
                        {qr.status}
                      </span>
                    </td>
                    <td>{qr.scans?.length || 0}</td>
                    <td>{new Date(qr.createdAt).toLocaleDateString()}</td>
                    <td>
                      <button className="button button-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

function getStatusBadge(status) {
  const badges = {
    active: 'success',
    inactive: 'warning',
    damaged: 'danger',
    replaced: 'info',
  }
  return badges[status] || 'info'
}

export default QRCodeList
