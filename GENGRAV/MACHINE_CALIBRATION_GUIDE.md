# GRBL Laser Engraving Machine Calibration Guide

## Overview
This guide will help you calibrate your GRBL-based laser engraving machine to ensure accurate movement and engraving. The machine should have a 250mm x 250mm working area with Arduino Uno running GRBL firmware.

## Prerequisites
- Arduino Uno with GRBL 1.1 firmware installed
- USB cable connected to computer
- Laser engraving control app running
- Ruler or measuring tape (metric)
- Test material (cardboard or wood)

## Step 1: Connect to GRBL and Check Settings

### 1.1 Connect to Arduino
1. Open the Laser Engraving Control app
2. Click "Refresh Ports" to scan for Arduino
3. Select the Arduino port (usually `/dev/tty.usbmodem*` on Mac or `COM*` on Windows)
4. Click "Connect"
5. Wait for "Connected successfully!" message

### 1.2 View Current Settings
In the "Manual G-Code" section, send these commands one by one:

```
$$
```

This will display all GRBL settings. Key settings to note:

| Setting | Parameter | Default | Description |
|---------|-----------|---------|-------------|
| `$100` | X-axis steps/mm | 250.000 | Steps per millimeter for X-axis |
| `$101` | Y-axis steps/mm | 250.000 | Steps per millimeter for Y-axis |
| `$102` | Z-axis steps/mm | 250.000 | Steps per millimeter for Z-axis |
| `$110` | X-axis max rate | 500.000 | Maximum rate in mm/min |
| `$111` | Y-axis max rate | 500.000 | Maximum rate in mm/min |
| `$112` | Z-axis max rate | 500.000 | Maximum rate in mm/min |
| `$120` | X-axis acceleration | 10.000 | Acceleration in mm/sec^2 |
| `$121` | Y-axis acceleration | 10.000 | Acceleration in mm/sec^2 |
| `$122` | Z-axis acceleration | 10.000 | Acceleration in mm/sec^2 |
| `$130` | X-axis max travel | 250.000 | Maximum X-axis travel in mm |
| `$131` | Y-axis max travel | 250.000 | Maximum Y-axis travel in mm |
| `$132` | Z-axis max travel | 200.000 | Maximum Z-axis travel in mm |
| `$30` | Max spindle/laser speed | 1000.000 | Maximum laser power (S value) |
| `$31` | Min spindle/laser speed | 0.000 | Minimum laser power (S value) |
| `$32` | Laser mode | 0 | Enable laser mode (set to 1) |

## Step 2: Enable Laser Mode

**Important:** GRBL must be in laser mode for proper operation.

Send this command:
```
$32=1
```

Verify by sending `$$` again and checking that `$32=1`.

## Step 3: Calibrate Steps Per Millimeter

### 3.1 X-Axis Calibration

1. **Home the machine:**
   - Click "Home" button or send `$H`
   
2. **Mark starting position:**
   - Place a marker or tape at the laser head position
   
3. **Move 100mm:**
   - Send command: `G21 G91 G0 X100 F1000`
   - This moves 100mm in X direction
   
4. **Measure actual distance:**
   - Measure the actual distance moved
   - If it moved exactly 100mm, no adjustment needed
   - If not, calculate new steps/mm:
   
   ```
   New $100 = (Current $100) × (Commanded Distance / Actual Distance)
   
   Example:
   - Current $100 = 250
   - Commanded = 100mm
   - Actual = 98mm
   
   New $100 = 250 × (100 / 98) = 255.10
   ```
   
5. **Update setting:**
   ```
   $100=255.10
   ```
   
6. **Test again and repeat until accurate**

### 3.2 Y-Axis Calibration

Repeat the same process for Y-axis:

1. Home the machine: `$H`
2. Send command: `G21 G91 G0 Y100 F1000`
3. Measure actual distance moved
4. Calculate new $101 value if needed
5. Update: `$101=<new_value>`
6. Test and verify

## Step 4: Verify Maximum Travel Limits

### 4.1 X-Axis Maximum Travel

1. **Home the machine:** `$H`
2. **Move to maximum X position:**
   ```
   G21 G90 G0 X250 F1000
   ```
3. **Check position:**
   - If the laser head reaches the end without collision: OK
   - If it hits the limit before 250mm: Adjust `$130` to actual maximum
   - If there's more travel available: You can increase `$130`
   
4. **Update if needed:**
   ```
   $130=<actual_max_mm>
   ```

### 4.2 Y-Axis Maximum Travel

1. **Home the machine:** `$H`
2. **Move to maximum Y position:**
   ```
   G21 G90 G0 Y250 F1000
   ```
3. **Verify travel and adjust `$131` if needed**

## Step 5: Calibrate Laser Power

### 5.1 Test Laser Power Range

1. **Prepare test material:**
   - Use cardboard or scrap wood
   - Place in center of bed
   
2. **Test at different power levels:**
   
   **10% Power:**
   ```
   G21 G90 G0 X10 Y10
   M3 S100
   G4 P1
   M5
   ```
   
   **50% Power:**
   ```
   G0 X20 Y10
   M3 S500
   G4 P1
   M5
   ```
   
   **100% Power:**
   ```
   G0 X30 Y10
   M3 S1000
   G4 P1
   M5
   ```

3. **Verify power consistency:**
   - All three marks should show increasing burn intensity
   - If S1000 is too powerful or too weak, adjust `$30` (max laser value)

### 5.2 Set Safe Defaults

For most PCB engraving applications:
```
$30=1000   (Maximum laser power)
$31=0      (Minimum laser power)
```

## Step 6: Test Movement Accuracy

### 6.1 Test Square Pattern

1. **Create a 100mm square:**
   ```
   $H
   G21 G90
   G0 X0 Y0 F1000
   M3 S100
   G1 X100 Y0 F500
   G1 X100 Y100 F500
   G1 X0 Y100 F500
   G1 X0 Y0 F500
   M5
   ```

2. **Measure the square:**
   - Each side should be exactly 100mm
   - Opposite sides should be parallel
   - Diagonals should be equal (~141.4mm)

### 6.2 Test Diagonal Movement

1. **Engrave diagonal line:**
   ```
   $H
   G21 G90
   G0 X0 Y0
   M3 S100
   G1 X100 Y100 F500
   M5
   ```

2. **Measure diagonal:**
   - Should be approximately 141.4mm (√(100² + 100²))
   - Verify straightness with a ruler

## Step 7: Fine-Tune Acceleration

### 7.1 Test for Vibration

If you notice:
- Rounded corners on squares
- Vibration during movement
- Lost steps or position errors

Try reducing acceleration:
```
$120=5.000    (X-axis acceleration)
$121=5.000    (Y-axis acceleration)
```

### 7.2 Test for Speed

If movement is too slow, you can increase:
```
$110=1000     (X-axis max rate)
$111=1000     (Y-axis max rate)
```

Test thoroughly after any speed increases.

## Step 8: Save and Document Settings

### 8.1 Save Current Configuration

After calibration, save all settings:

1. Send `$$` to display all settings
2. Copy the output to a text file
3. Save as `grbl_settings_backup_YYYYMMDD.txt`
4. Store in a safe location

### 8.2 Create Quick Reference Card

Document these key values on a card near the machine:

```
Machine: 250x250mm GRBL Laser Engraver
Date Calibrated: __________

$100 (X steps/mm): _______
$101 (Y steps/mm): _______
$130 (X max travel): _______
$131 (Y max travel): _______
$32 (Laser mode): 1

Safe Laser Power: S100-S500
Engraving Speed: F500
Travel Speed: F1000
```

## Step 9: Verify QR Code Engraving

### 9.1 Test with Small QR Code

1. Generate a test QR code using the generation app
2. In the engraving app, select "Test Engrave (10mm Square)"
3. Verify:
   - Size is accurate (10mm x 10mm)
   - Lines are straight and clean
   - No position drift

### 9.2 Test Full-Size QR Code

1. Generate a QR code for batch engraving
2. Start engraving with time delay
3. Monitor for:
   - Consistent positioning between codes
   - No accumulated position errors
   - Readable QR codes after engraving

## Troubleshooting

### Problem: Machine moves wrong distance

**Solution:** Re-calibrate steps/mm (Step 3)

### Problem: Laser turns on during travel moves

**Solution:** Ensure laser mode is enabled: `$32=1`

### Problem: Machine loses position over time

**Solution:** 
- Check belt tension
- Reduce acceleration (`$120`, `$121`)
- Reduce max speed (`$110`, `$111`)

### Problem: Corners are rounded

**Solution:**
- Reduce acceleration for sharper corners
- Check junction deviation: `$11=0.010`

### Problem: Laser power is inconsistent

**Solution:**
- Verify `$30` and `$31` settings
- Check laser power supply
- Clean laser lens

## Recommended Final Settings

For 250x250mm PCB engraving with typical NEMA17 motors:

```
$100=250.000   (X steps/mm)
$101=250.000   (Y steps/mm)
$102=250.000   (Z steps/mm)
$110=1000.000  (X max rate)
$111=1000.000  (Y max rate)
$112=500.000   (Z max rate)
$120=10.000    (X accel)
$121=10.000    (Y accel)
$122=10.000    (Z accel)
$130=250.000   (X max travel)
$131=250.000   (Y max travel)
$132=200.000   (Z max travel)
$30=1000.000   (Max laser)
$31=0.000      (Min laser)
$32=1          (Laser mode ON)
```

## Maintenance Schedule

### Daily:
- Clean laser lens
- Check for debris on bed
- Verify home position accuracy

### Weekly:
- Check belt tension
- Clean rails and linear bearings
- Test calibration square

### Monthly:
- Full recalibration check
- Backup GRBL settings
- Inspect all mechanical components

## Safety Reminders

⚠️ **ALWAYS:**
- Wear laser safety goggles when operating
- Keep fire extinguisher nearby
- Never leave machine unattended during operation
- Test on scrap material first
- Keep workspace ventilated

---

**Last Updated:** 2024
**Document Version:** 1.0
