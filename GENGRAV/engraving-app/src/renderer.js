/**
 * GENGRAV Renderer
 */
import './index.css';

const $ = id => document.getElementById(id);
let isConnected = false;
let currentGCode = null;

function log(msg, type = 'log') {
  const c = $('console');
  const l = document.createElement('div');
  l.className = `console-line ${type}`;
  l.textContent = msg;
  c.appendChild(l);
  c.scrollTop = c.scrollHeight;
}

function updateConnectionUI(connected) {
  isConnected = connected;
  const s = $('connectionStatus');
  s.className = connected ? 'connection connected' : 'connection disconnected';
  s.querySelector('.text').textContent = connected ? 'Connected' : 'Disconnected';
  $('connectBtn').disabled = connected;
  $('disconnectBtn').disabled = !connected;

  const controls = ['readSettingsBtn', 'saveSettingsBtn', 'applyDefaultsBtn', 'enableLaserBtn',
    'homeBtn', 'goHomeBtn', 'jogYPlus', 'jogYMinus', 'jogXPlus', 'jogXMinus', 'jogCenter', 'sendCmdBtn',
    'config22', 'config100', 'config101', 'config110', 'config111', 'config30'];
  controls.forEach(id => $(id).disabled = !connected);
}

function updateStatus(s) {
  $('posX').textContent = s.position.x.toFixed(3);
  $('posY').textContent = s.position.y.toFixed(3);
  $('posZ').textContent = s.position.z.toFixed(3);
  $('machineState').textContent = s.state;
}

function updateSettings(settings) {
  // Update badges
  const laser = settings['$32'];
  const badge = $('laserBadge');
  badge.textContent = `$32: ${laser === 1 ? 'ON' : 'OFF'}`;
  badge.className = laser === 1 ? 'badge active' : 'badge';

  // Update config fields
  if (settings['$22'] !== undefined) $('config22').value = settings['$22'];
  if (settings['$100'] !== undefined) $('config100').value = settings['$100'];
  if (settings['$101'] !== undefined) $('config101').value = settings['$101'];
  if (settings['$110'] !== undefined) $('config110').value = settings['$110'];
  if (settings['$111'] !== undefined) $('config111').value = settings['$111'];
  if (settings['$30'] !== undefined) $('config30').value = settings['$30'];

  log('Settings loaded', 'log');
}

// Connection
$('refreshBtn').addEventListener('click', async () => {
  const ports = await window.grbl.listPorts();
  const sel = $('portSelect');
  sel.innerHTML = '<option value="">Select Port</option>';
  ports.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.path;
    opt.textContent = `${p.path} ${p.manufacturer || ''}`;
    sel.appendChild(opt);
  });
  log(`Found ${ports.length} ports`);
});

$('connectBtn').addEventListener('click', async () => {
  const port = $('portSelect').value;
  if (!port) return log('Select a port first', 'error');
  log(`Connecting to ${port}...`);
  const r = await window.grbl.connect(port);
  if (r.success) { updateConnectionUI(true); log('Connected!'); }
  else log(`Failed: ${r.error}`, 'error');
});

$('disconnectBtn').addEventListener('click', async () => {
  await window.grbl.disconnect();
  updateConnectionUI(false);
  log('Disconnected');
});

// Settings
$('readSettingsBtn').addEventListener('click', async () => {
  log('Reading settings...');
  const r = await window.grbl.readSettings();
  if (r.success) updateSettings(r.settings);
});

$('saveSettingsBtn').addEventListener('click', async () => {
  log('Saving settings...');
  const settings = [
    ['$22', $('config22').value],
    ['$100', $('config100').value],
    ['$101', $('config101').value],
    ['$110', $('config110').value],
    ['$111', $('config111').value],
    ['$30', $('config30').value]
  ];
  for (const [k, v] of settings) {
    if (v) {
      const r = await window.grbl.writeSetting(k, v);
      if (r.success) log(`${k}=${v} saved`);
      else log(`${k} error: ${r.error}`, 'error');
    }
  }
  log('Settings saved!', 'log');
});

$('applyDefaultsBtn').addEventListener('click', async () => {
  if (!confirm('Apply default settings?')) return;
  log('Applying defaults...');
  await window.grbl.applyDefaults();
  await window.grbl.readSettings();
});

$('enableLaserBtn').addEventListener('click', async () => {
  log('Enabling laser mode...');
  const r = await window.grbl.enableLaserMode();
  if (r.success) { $('laserBadge').textContent = '$32: ON'; $('laserBadge').className = 'badge active'; log('Laser mode enabled'); }
});

// Machine Control
$('homeBtn').addEventListener('click', async () => { await window.grbl.home(); log('Home set'); });
$('goHomeBtn').addEventListener('click', async () => { await window.grbl.goHome(); log('Going home...'); });

const jogStep = () => parseFloat($('jogStep').value);
$('jogYPlus').addEventListener('click', () => window.grbl.jog('Y', jogStep()));
$('jogYMinus').addEventListener('click', () => window.grbl.jog('Y', -jogStep()));
$('jogXPlus').addEventListener('click', () => window.grbl.jog('X', jogStep()));
$('jogXMinus').addEventListener('click', () => window.grbl.jog('X', -jogStep()));

// Image
$('preview').addEventListener('click', () => $('fileInput').click());
$('loadImageBtn').addEventListener('click', () => $('fileInput').click());
$('fileInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    const img = document.createElement('img');
    img.src = reader.result;
    $('preview').innerHTML = '';
    $('preview').appendChild(img);
    $('generateBtn').disabled = false;
    log(`Loaded: ${file.name}`);
  };
  reader.readAsDataURL(file);
});

$('generateBtn').addEventListener('click', () => {
  currentGCode = `; GENGRAV\nG21 G90\nM4 S0\nG0 X0 Y0\n; Image placeholder\nM5\nG0 X0 Y0\nM2`;
  $('startBtn').disabled = false;
  log('G-Code generated');
});

$('startBtn').addEventListener('click', async () => {
  if (!currentGCode) return;
  log('Starting...');
  $('stopBtn').disabled = false;
  $('progressBox').hidden = false;
  await window.grbl.runGCode(currentGCode);
  $('stopBtn').disabled = true;
});

$('stopBtn').addEventListener('click', async () => { await window.grbl.stop(); log('Stopping...'); });
$('emergencyBtn').addEventListener('click', async () => { log('!!! EMERGENCY STOP !!!', 'error'); await window.grbl.emergencyStop(); });

$('sendCmdBtn').addEventListener('click', async () => {
  const cmd = $('cmdInput').value.trim();
  if (!cmd) return;
  await window.grbl.send(cmd);
  $('cmdInput').value = '';
});
$('cmdInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') $('sendCmdBtn').click(); });
$('clearConsoleBtn').addEventListener('click', () => { $('console').innerHTML = ''; });

// IPC Events
window.grbl.onStatus(updateStatus);
window.grbl.onLog(m => log(m, 'log'));
window.grbl.onTx(c => log(`>> ${c}`, 'tx'));
window.grbl.onRx(l => log(`<< ${l}`, 'rx'));
window.grbl.onProgress(p => { $('progressBox').hidden = false; $('progressFill').style.width = `${p.percent}%`; $('progressText').textContent = `${p.percent}%`; });
window.grbl.onSettings(updateSettings);
window.grbl.onError(e => log(`ERROR: ${e}`, 'error'));
window.grbl.onEstop(() => log('EMERGENCY STOP ACTIVATED', 'error'));
window.grbl.onComplete(() => { log('Complete!'); $('stopBtn').disabled = true; setTimeout(() => $('progressBox').hidden = true, 2000); });

log('GENGRAV ready');
$('refreshBtn').click();
