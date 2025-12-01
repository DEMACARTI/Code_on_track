(G-code for engraving a QR code on a 250x250mm board)

G21 ; Set units to millimeters
G90 ; Use absolute positioning
G0 Z5.000 ; Raise the tool to a safe height
G0 X0 Y0 ; Move to the origin

; Start engraving the QR code
G1 Z-1.000 F500 ; Lower the tool to engraving depth

; Example QR code pattern (simplified for demonstration)
G1 X10 Y10 F1000 ; Move to first point
G1 X20 Y10 ; Draw a horizontal line
G1 X20 Y20 ; Draw a vertical line
G1 X10 Y20 ; Draw a horizontal line back
G1 X10 Y10 ; Draw a vertical line back

; Repeat for other QR code sections (simplified)
G1 X30 Y30 ; Move to next section
G1 X40 Y30 ; Draw a horizontal line
G1 X40 Y40 ; Draw a vertical line
G1 X30 Y40 ; Draw a horizontal line back
G1 X30 Y30 ; Draw a vertical line back

; Finish engraving
G0 Z5.000 ; Raise the tool to a safe height
G0 X0 Y0 ; Return to origin
M30 ; End of program