# PostgreSQL Remote Access Configuration Guide

## Step 1: Configure PostgreSQL for Remote Connections

### A. Edit postgresql.conf
# Location: /opt/homebrew/var/postgresql@14/postgresql.conf (macOS)
# or /etc/postgresql/14/main/postgresql.conf (Linux)

# Find and change:
listen_addresses = '*'  # Listen on all network interfaces
port = 5433

### B. Edit pg_hba.conf
# Location: Same directory as postgresql.conf

# Add these lines at the end:
# Allow connections from specific IP ranges (use your network range)
host    irf_dev    irf_user    192.168.1.0/24    scram-sha-256
# Or allow from anywhere (less secure):
host    irf_dev    irf_user    0.0.0.0/0         scram-sha-256

# For SSL connections (more secure):
hostssl irf_dev    irf_user    0.0.0.0/0         scram-sha-256

## Step 2: Set Up SSL (Recommended)

# Generate SSL certificates in PostgreSQL data directory
cd /opt/homebrew/var/postgresql@14/  # macOS
# or cd /var/lib/postgresql/14/main/  # Linux

# Generate self-signed certificate
openssl req -new -x509 -days 365 -nodes -text -out server.crt \
  -keyout server.key -subj "/CN=postgres-server"

# Set proper permissions
chmod 600 server.key
chown postgres:postgres server.key server.crt  # Linux only

# Enable SSL in postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

## Step 3: Restart PostgreSQL
# macOS:
brew services restart postgresql@14

# Linux:
sudo systemctl restart postgresql

## Step 4: Configure Firewall

# macOS:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/postgres
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/local/bin/postgres

# Linux (ufw):
sudo ufw allow 5433/tcp
sudo ufw reload

# Linux (firewalld):
sudo firewall-cmd --permanent --add-port=5433/tcp
sudo firewall-cmd --reload

## Step 5: Update Connection Strings

# Remote connection (SSL):
DATABASE_URL=postgresql://irf_user:irf_pass@YOUR_PUBLIC_IP:5433/irf_dev?sslmode=require

# Remote connection (no SSL - not recommended):
DATABASE_URL=postgresql://irf_user:irf_pass@YOUR_PUBLIC_IP:5433/irf_dev

## Security Best Practices

1. Always use SSL/TLS for remote connections
2. Use strong passwords
3. Limit access by IP address in pg_hba.conf
4. Use a VPN (like Tailscale or WireGuard) for team access
5. Keep PostgreSQL updated
6. Enable connection logging
7. Use certificate-based authentication for production
8. Never expose database directly to the internet without VPN

## Recommended Architecture

Internet
   ↓
[VPN/Tailscale] ← Secure tunnel
   ↓
[Your PostgreSQL Server]
   ↓
[QR Generation App] ← Local network
[Engraving App]     ← Local network

## Testing Remote Connection

# From remote machine:
psql "postgresql://irf_user:irf_pass@YOUR_IP:5433/irf_dev?sslmode=require"

# Or using Node.js test:
node -e "
const { Pool } = require('pg');
const pool = new Pool({
  host: 'YOUR_IP',
  port: 5433,
  database: 'irf_dev',
  user: 'irf_user',
  password: 'irf_pass',
  ssl: { rejectUnauthorized: false }
});
pool.query('SELECT NOW()', (err, res) => {
  console.log(err ? err.stack : res.rows[0]);
  pool.end();
});
"
