/**
 * GENGRAV Renderer - GRBL 1.1 Compatible
 * Full LaserGRBL-style API with GRBL 1.1 features
 */
import './index.css';

const $ = id => document.getElementById(id);
let isConnected = false;
let currentGCode = null;
let grblVersion = null;

function log(msg, type = 'log') {
  const c = $('console');
  const l = document.createElement('div');
  l.className = `console-line ${type}`;
  l.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  c.appendChild(l);
  c.scrollTop = c.scrollHeight;
  // Keep only last 500 lines
  while (c.children.length > 500) c.removeChild(c.firstChild);
}

function updateConnectionUI(connected) {
  isConnected = connected;
  const s = $('connectionStatus');
  s.className = connected ? 'connection connected' : 'connection disconnected';
  s.querySelector('.text').textContent = connected ? 'Connected' : 'Disconnected';
  $('connectBtn').disabled = connected;
  $('disconnectBtn').disabled = !connected;
  $('baudSelect').disabled = connected;
  $('dtrReset').disabled = connected;
  $('softReset').disabled = connected;

  const controls = ['readSettingsBtn', 'saveSettingsBtn', 'applyDefaultsBtn', 'enableLaserBtn',
    'homeBtn', 'goHomeBtn', 'jogYPlus', 'jogYMinus', 'jogXPlus', 'jogXMinus', 'jogCenter', 'sendCmdBtn',
    'config22', 'config100', 'config101',
    'laserTestBtn', 'laserFocusBtn', 'laserOffBtn', 'testPower',
    'unlockBtn', 'resetBtn',
    // GRBL 1.1 override controls
    'feedMinus10', 'feedMinus1', 'feedPlus1', 'feedPlus10', 'feedReset',
    'spindleMinus10', 'spindleMinus1', 'spindlePlus1', 'spindlePlus10', 'spindleReset',
    'rapidFull', 'rapid50', 'rapid25'];
  controls.forEach(id => {
    const el = $(id);
    if (el) el.disabled = !connected;
  });
}

function updateStatus(s) {
  $('posX').textContent = s.position.x.toFixed(3);
  $('posY').textContent = s.position.y.toFixed(3);
  $('posZ').textContent = s.position.z.toFixed(3);
  
  // GRBL 1.1 state with substate
  let stateText = s.state;
  if (s.subState !== null && s.subState !== undefined) {
    stateText += `:${s.subState}`;
  }
  $('machineState').textContent = stateText;
  
  // Color-code machine state
  const stateEl = $('machineState');
  stateEl.className = '';
  if (s.state === 'Alarm') stateEl.className = 'state-alarm';
  else if (s.state === 'Run') stateEl.className = 'state-run';
  else if (s.state === 'Hold') stateEl.className = 'state-hold';
  else if (s.state === 'Idle') stateEl.className = 'state-idle';
  else if (s.state === 'Jog') stateEl.className = 'state-jog';
  else if (s.state === 'Door') stateEl.className = 'state-alarm';
  else if (s.state === 'Home') stateEl.className = 'state-run';
  
  // GRBL 1.1 overrides display
  if (s.overrides) {
    $('feedOvr').textContent = s.overrides.feed || 100;
    $('spindleOvr').textContent = s.overrides.spindle || 100;
    $('feedOverrideVal').textContent = `${s.overrides.feed || 100}%`;
    $('spindleOverrideVal').textContent = `${s.overrides.spindle || 100}%`;
  }
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

  log('Settings loaded', 'log');
}

// Connection
$('refreshBtn').addEventListener('click', async () => {
  log('Scanning for ports...');
  const ports = await window.grbl.listPorts();
  const sel = $('portSelect');
  sel.innerHTML = '<option value="">Select Port</option>';
  ports.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.path;
    const info = [p.path];
    if (p.manufacturer) info.push(p.manufacturer);
    if (p.vendorId) info.push(`VID:${p.vendorId}`);
    opt.textContent = info.join(' - ');
    sel.appendChild(opt);
  });
  log(`Found ${ports.length} compatible ports`);
  if (ports.length === 0) {
    log('No compatible ports found. Check USB connection.', 'error');
  }
});

$('connectBtn').addEventListener('click', async () => {
  const port = $('portSelect').value;
  if (!port) return log('Select a port first', 'error');
  
  const baudRate = parseInt($('baudSelect').value);
  const dtrReset = $('dtrReset').checked;
  const softReset = $('softReset').checked;
  
  log(`Connecting to ${port} @ ${baudRate} baud...`);
  log(`Options: DTR/RTS=${dtrReset}, SoftReset=${softReset}`);
  
  $('connectBtn').disabled = true;
  $('connectBtn').textContent = 'Connecting...';
  
  const r = await window.grbl.connect(port, baudRate, {
    dtrOnConnect: dtrReset,
    rtsOnConnect: dtrReset,
    softResetOnConnect: softReset
  });
  
  if (r.success) { 
    updateConnectionUI(true); 
    log('Connected successfully!');
    if (r.state?.version) {
      grblVersion = r.state.version;
      $('versionBadge').textContent = `Ver: ${grblVersion}`;
    }
  } else {
    log(`Connection failed: ${r.error}`, 'error');
    $('connectBtn').disabled = false;
  }
  $('connectBtn').textContent = 'Connect';
});

$('disconnectBtn').addEventListener('click', async () => {
  await window.grbl.disconnect();
  updateConnectionUI(false);
  log('Disconnected');
  $('versionBadge').textContent = 'Ver: --';
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
    ['$101', $('config101').value]
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

// Laser Test Controls
$('testPower').addEventListener('input', () => {
  $('testPowerValue').textContent = `${$('testPower').value}%`;
});

$('laserTestBtn').addEventListener('click', async () => {
  const power = parseInt($('testPower').value) * 10; // Convert % to S-value (assuming $30=1000)
  log(`Test firing laser at ${$('testPower').value}% power...`, 'warning');
  await window.grbl.laserTest(power, 200);
  log('Test fire complete');
});

$('laserFocusBtn').addEventListener('click', async () => {
  const power = Math.min(parseInt($('testPower').value) * 2, 50); // Very low power for focus
  log(`Focus mode ON at ${power/10}% - Use laser OFF to stop`, 'warning');
  await window.grbl.laserFocus(power);
});

$('laserOffBtn').addEventListener('click', async () => {
  await window.grbl.laserOff();
  log('Laser OFF');
});

// Emergency & Reset Controls
$('unlockBtn').addEventListener('click', async () => {
  log('Unlocking GRBL...');
  const r = await window.grbl.unlock();
  if (r.success) log('Unlocked');
  else log(`Unlock failed: ${r.error}`, 'error');
});

$('resetBtn').addEventListener('click', async () => {
  log('Sending soft reset...');
  await window.grbl.softReset();
  log('Reset sent');
});

// GRBL 1.1 Override Controls
// Feed Override
$('feedMinus10').addEventListener('click', () => window.grbl.feedOverrideDecrease(false));
$('feedMinus1').addEventListener('click', () => window.grbl.feedOverrideDecrease(true));
$('feedPlus1').addEventListener('click', () => window.grbl.feedOverrideIncrease(true));
$('feedPlus10').addEventListener('click', () => window.grbl.feedOverrideIncrease(false));
$('feedReset').addEventListener('click', () => window.grbl.feedOverrideReset());

// Spindle/Laser Override
$('spindleMinus10').addEventListener('click', () => window.grbl.spindleOverrideDecrease(false));
$('spindleMinus1').addEventListener('click', () => window.grbl.spindleOverrideDecrease(true));
$('spindlePlus1').addEventListener('click', () => window.grbl.spindleOverrideIncrease(true));
$('spindlePlus10').addEventListener('click', () => window.grbl.spindleOverrideIncrease(false));
$('spindleReset').addEventListener('click', () => window.grbl.spindleOverrideReset());

// Rapid Override
$('rapidFull').addEventListener('click', () => window.grbl.rapidOverrideReset());
$('rapid50').addEventListener('click', () => window.grbl.rapidOverride50());
$('rapid25').addEventListener('click', () => window.grbl.rapidOverride25());

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
  currentGCode = `; GENGRAV\nG21 G90\nM4 S0\nG0 X0 Y0\n; Image placeholder\nM5 S0\nG0 X0 Y0\nM2`;
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
  log(`Sending: ${cmd}`);
  const r = await window.grbl.send(cmd);
  if (!r.success) log(`Error: ${r.error}`, 'error');
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
window.grbl.onVersion(v => { 
  grblVersion = v; 
  $('versionBadge').textContent = `Ver: ${v || '--'}`; 
  log(`GRBL Version: ${v}`);
});
window.grbl.onAlarm(a => {
  log(`⚠️ ALARM ${a.code}: ${a.message}`, 'error');
  $('machineState').textContent = 'Alarm';
  $('machineState').className = 'state-alarm';
});
window.grbl.onMessage(m => log(`[MSG] ${m}`, 'log'));

log('GENGRAV ready - GRBL 1.1 compatible');
$('refreshBtn').click();
