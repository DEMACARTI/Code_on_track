import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import QRCodeList from './pages/QRCodeList'
import Notifications from './pages/Notifications'
import Analytics from './pages/Analytics'

function App() {
  return (
    <Router>
      <div className="app">
        <nav style={styles.nav}>
          <div className="container" style={styles.navContent}>
            <h1 style={styles.logo}>Railway QR Tracking System</h1>
            <div style={styles.navLinks}>
              <Link to="/" style={styles.link}>Dashboard</Link>
              <Link to="/qrcodes" style={styles.link}>QR Codes</Link>
              <Link to="/notifications" style={styles.link}>Notifications</Link>
              <Link to="/analytics" style={styles.link}>Analytics</Link>
            </div>
          </div>
        </nav>
        
        <main className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/qrcodes" element={<QRCodeList />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

const styles = {
  nav: {
    backgroundColor: '#1a1a2e',
    color: 'white',
    padding: '16px 0',
    marginBottom: '30px',
  },
  navContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: '24px',
    fontWeight: 'bold',
  },
  navLinks: {
    display: 'flex',
    gap: '30px',
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    fontSize: '16px',
    fontWeight: '500',
  },
}

export default App
