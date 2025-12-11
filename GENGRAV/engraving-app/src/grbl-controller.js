/**
 * GRBL Controller - Based on LaserGRBL's GrblCore.cs
 */
const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const EventEmitter = require('events');

const GRBL_RX_BUFFER_SIZE = 128;
const STATUS_POLL_INTERVAL = 250;

const MachineState = {
    DISCONNECTED: 'Disconnected', IDLE: 'Idle', RUN: 'Run', HOLD: 'Hold',
    JOG: 'Jog', ALARM: 'Alarm', DOOR: 'Door', CHECK: 'Check', HOME: 'Home', SLEEP: 'Sleep'
};

const GRBL_SETTINGS = {
    '$22': { name: 'Homing cycle', units: 'bool' },
    '$30': { name: 'Max spindle', units: 'RPM' },
    '$32': { name: 'Laser mode', units: 'bool' },
    '$100': { name: 'X steps/mm', units: 'step/mm' },
    '$101': { name: 'Y steps/mm', units: 'step/mm' },
    '$110': { name: 'X max rate', units: 'mm/min' },
    '$111': { name: 'Y max rate', units: 'mm/min' },
    '$120': { name: 'X accel', units: 'mm/s²' },
    '$121': { name: 'Y accel', units: 'mm/s²' },
    '$130': { name: 'X max travel', units: 'mm' },
    '$131': { name: 'Y max travel', units: 'mm' }
};

const LASER_DEFAULTS = {
    '$0': 10, '$1': 25, '$10': 1, '$20': 0, '$21': 0, '$22': 0,
    '$30': 1000, '$31': 0, '$32': 1,
    '$100': 80, '$101': 80, '$102': 80,
    '$110': 2000, '$111': 2000, '$112': 500,
    '$120': 500, '$121': 500, '$122': 500,
    '$130': 150, '$131': 150, '$132': 50
};

class GRBLController extends EventEmitter {
    constructor() {
        super();
        this.port = null;
        this.parser = null;
        this.isConnected = false;
        this.portPath = null;
        this.machineState = MachineState.DISCONNECTED;
        this.grblVersion = null;
        this.position = { x: 0, y: 0, z: 0 };
        this.workPosition = { x: 0, y: 0, z: 0 };
        this.feedRate = 0;
        this.spindleSpeed = 0;
        this.settings = {};
        this.commandQueue = [];
        this.sentCommands = [];
        this.bufferUsed = 0;
        this.pollInterval = null;
        this.isRunning = false;
        this.totalCommands = 0;
        this.completedCommands = 0;
        this.stopRequested = false;
        this.emergencyStop = false;
        this.maxPower = 500;
    }

    async listPorts() {
        try {
            const ports = await SerialPort.list();
            return ports.filter(p =>
                p.manufacturer?.toLowerCase().includes('arduino') ||
                p.manufacturer?.toLowerCase().includes('ch340') ||
                p.path.includes('usbserial') ||
                p.path.includes('ttyUSB') ||
                p.path.includes('COM')
            );
        } catch (e) {
            console.error('Error listing ports:', e);
            return [];
        }
    }

    async connect(portPath) {
        if (this.isConnected) await this.disconnect();
        return new Promise((resolve, reject) => {
            this.port = new SerialPort({
                path: portPath, baudRate: 115200, dataBits: 8, parity: 'none', stopBits: 1
            });
            this.parser = this.port.pipe(new ReadlineParser({ delimiter: '\r\n' }));
            this.portPath = portPath;

            this.port.on('open', () => {
                this.isConnected = true;
                this.machineState = MachineState.IDLE;
                this.emit('connected');
                this.log('Connected to ' + portPath);
                setTimeout(() => {
                    this.readSettings().catch(console.error);
                    this.startStatusPolling();
                }, 1500);
                resolve(true);
            });

            this.parser.on('data', (line) => this.handleResponse(line));
            this.port.on('error', (err) => { this.isConnected = false; this.emit('error', err); reject(err); });
            this.port.on('close', () => { this.isConnected = false; this.stopStatusPolling(); this.emit('disconnected'); });
        });
    }

    async disconnect() {
        this.stopStatusPolling();
        if (this.port?.isOpen) return new Promise(r => this.port.close(r));
    }

    sendRaw(cmd) {
        if (!this.isConnected) return false;
        this.port.write(cmd + '\n');
        this.emit('tx', cmd);
        return true;
    }

    async send(cmd) {
        if (!this.isConnected) throw new Error('Not connected');
        if (this.emergencyStop) throw new Error('Emergency stop active');

        return new Promise((resolve, reject) => {
            const cmdLen = cmd.length + 1;
            if (this.bufferUsed + cmdLen > GRBL_RX_BUFFER_SIZE) {
                this.commandQueue.push({ cmd, resolve, reject });
                return;
            }
            this.port.write(cmd + '\n');
            this.bufferUsed += cmdLen;
            this.sentCommands.push({ cmd, len: cmdLen, resolve, reject });
            this.emit('tx', cmd);
        });
    }

    processQueue() {
        while (this.commandQueue.length > 0) {
            const { cmd, resolve, reject } = this.commandQueue[0];
            const cmdLen = cmd.length + 1;
            if (this.bufferUsed + cmdLen <= GRBL_RX_BUFFER_SIZE) {
                this.commandQueue.shift();
                this.port.write(cmd + '\n');
                this.bufferUsed += cmdLen;
                this.sentCommands.push({ cmd, len: cmdLen, resolve, reject });
                this.emit('tx', cmd);
            } else break;
        }
    }

    handleResponse(line) {
        if (!line) return;
        this.emit('rx', line);

        if (line.startsWith('<') && line.endsWith('>')) { this.parseStatus(line); return; }

        if (line === 'ok') {
            if (this.sentCommands.length > 0) {
                const cmd = this.sentCommands.shift();
                this.bufferUsed -= cmd.len;
                this.completedCommands++;
                cmd.resolve(true);
                this.emit('progress', {
                    completed: this.completedCommands, total: this.totalCommands,
                    percent: Math.round((this.completedCommands / this.totalCommands) * 100)
                });
            }
            this.processQueue();
            return;
        }

        if (line.startsWith('error:')) {
            if (this.sentCommands.length > 0) {
                const cmd = this.sentCommands.shift();
                this.bufferUsed -= cmd.len;
                cmd.reject(new Error(line));
            }
            this.emit('error', line);
            this.processQueue();
            return;
        }

        if (line.includes('Grbl')) {
            const match = line.match(/Grbl\s+(\d+\.\d+[a-z]?)/i);
            if (match) this.grblVersion = match[1];
            this.emit('version', this.grblVersion);
        }

        if (line.match(/^\$\d+=/)) {
            const m = line.match(/^\$(\d+)=(.+)$/);
            if (m) this.settings[`$${m[1]}`] = parseFloat(m[2]) || m[2];
        }

        if (line.startsWith('ALARM:')) { this.machineState = MachineState.ALARM; this.emit('alarm', line); }
    }

    parseStatus(report) {
        const content = report.slice(1, -1);
        const parts = content.split('|');
        this.machineState = parts[0];

        for (const part of parts.slice(1)) {
            if (part.startsWith('MPos:')) {
                const coords = part.slice(5).split(',');
                this.position = { x: parseFloat(coords[0]) || 0, y: parseFloat(coords[1]) || 0, z: parseFloat(coords[2]) || 0 };
            }
            if (part.startsWith('WPos:')) {
                const coords = part.slice(5).split(',');
                this.workPosition = { x: parseFloat(coords[0]) || 0, y: parseFloat(coords[1]) || 0, z: parseFloat(coords[2]) || 0 };
            }
            if (part.startsWith('FS:')) {
                const vals = part.slice(3).split(',');
                this.feedRate = parseFloat(vals[0]) || 0;
                this.spindleSpeed = parseFloat(vals[1]) || 0;
            }
        }
        this.emit('status', { state: this.machineState, position: this.position, workPosition: this.workPosition, feedRate: this.feedRate, spindleSpeed: this.spindleSpeed });
    }

    startStatusPolling() {
        if (this.pollInterval) return;
        this.pollInterval = setInterval(() => { if (this.isConnected) this.port.write('?'); }, STATUS_POLL_INTERVAL);
    }

    stopStatusPolling() {
        if (this.pollInterval) { clearInterval(this.pollInterval); this.pollInterval = null; }
    }

    async readSettings() {
        return new Promise((resolve) => {
            this.settings = {};
            const timeout = setTimeout(() => { this.parser.off('data', onData); resolve(this.settings); }, 2000);
            const onData = (line) => {
                if (line === 'ok') { clearTimeout(timeout); this.parser.off('data', onData); this.emit('settings', this.settings); resolve(this.settings); }
            };
            this.parser.on('data', onData);
            this.sendRaw('$$');
        });
    }

    async writeSetting(key, value) {
        await this.send(`${key}=${value}`);
        this.settings[key] = value;
    }

    async applyDefaults() {
        for (const [k, v] of Object.entries(LASER_DEFAULTS)) {
            await this.writeSetting(k, v);
            await this.delay(50);
        }
        this.emit('settings', this.settings);
    }

    async enableLaserMode() { await this.writeSetting('$32', 1); this.log('Laser mode enabled'); }
    isLaserModeEnabled() { return this.settings['$32'] === 1; }

    supportsTrueJogging() {
        if (!this.grblVersion) return true;
        const match = this.grblVersion.match(/(\d+)\.(\d+)/);
        if (match) return parseInt(match[1]) > 1 || (parseInt(match[1]) === 1 && parseInt(match[2]) >= 1);
        return true;
    }

    async home() { await this.send('G10 L20 P1 X0 Y0 Z0'); this.position = { x: 0, y: 0, z: 0 }; this.log('Home set'); }
    async goHome() { await this.send('G90'); await this.send('G0 X0 Y0'); }

    async moveTo(x, y, feed = 1000) {
        await this.send('G90');
        await this.send(`G0 X${x.toFixed(2)} Y${y.toFixed(2)} F${feed}`);
    }

    async jog(axis, distance, feed = 500) {
        const distStr = parseFloat(distance).toFixed(1);
        if (this.supportsTrueJogging()) {
            await this.send(`$J=G91${axis}${distStr}F${feed}`);
        } else {
            await this.send('G91');
            await this.send(`G1${axis}${distStr}F${feed}`);
            await this.send('G90');
        }
    }

    async laserOn(power = 100) { await this.send(`M4 S${Math.min(power, this.maxPower)}`); }
    async laserOff() { await this.send('M5'); }

    async doEmergencyStop() {
        this.emergencyStop = true;
        this.stopRequested = true;
        this.commandQueue = [];
        this.sentCommands.forEach(c => c.reject(new Error('E-Stop')));
        this.sentCommands = [];
        this.bufferUsed = 0;
        this.stopStatusPolling();
        if (this.port?.isOpen) { this.port.write('M5\n'); this.port.write(Buffer.from([0x18])); }
        this.machineState = MachineState.ALARM;
        this.emit('estop');
        this.log('EMERGENCY STOP');
    }

    async resetEstop() {
        this.emergencyStop = false;
        this.stopRequested = false;
        if (this.port?.isOpen) { this.port.write(Buffer.from([0x18])); await this.delay(500); await this.send('$X'); }
        this.startStatusPolling();
        this.log('Reset complete');
    }

    async runGCode(gcode) {
        if (this.emergencyStop) throw new Error('E-Stop active');
        const lines = gcode.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith(';'));
        this.totalCommands = lines.length;
        this.completedCommands = 0;
        this.isRunning = true;
        this.stopRequested = false;
        this.emit('start', { total: this.totalCommands });

        try {
            for (const line of lines) { if (this.stopRequested) break; await this.send(line); }
            while (this.sentCommands.length > 0 && !this.stopRequested) await this.delay(100);
            this.emit('complete');
        } finally { this.isRunning = false; }
    }

    stop() { this.stopRequested = true; }
    delay(ms) { return new Promise(r => setTimeout(r, ms)); }
    log(msg) { this.emit('log', msg); console.log('[GRBL]', msg); }
    getState() { return { connected: this.isConnected, state: this.machineState, position: this.position, settings: this.settings, version: this.grblVersion, laserMode: this.isLaserModeEnabled() }; }
}

module.exports = { GRBLController, MachineState, GRBL_SETTINGS, LASER_DEFAULTS };
