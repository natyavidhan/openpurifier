# OpenPurifier

DIY HEPA air purifier: a Xiaomi-type cylindrical filter (PANCA, Ø200 × 293 mm) and a HEWA Onyx
150 mm exhaust fan in a 3D-printed cylinder, Ø265 × 425 mm. Every printed part fits a 256 mm bed.
An ESP32-C3 SuperMini turns the fan on and off by having a servo flip a small mains toggle switch,
so no relay board is involved.

```
cad/        text-to-cad model (build123d): src/lib/params.py holds every dimension
circuit/    wiring.html: wiring diagram + connection list
firmware/   openpurifier.yaml: ESPHome config (untested build)
reference/  listing drawings and the Xiaomi filter datasheet
```

## How the air flows

Room air enters through the slots in the lower body and passes through the filter from the outside in.
It rises through the filter's open top and through the transition plate into the fan's front grille,
which faces down. The fan's collar points up and blows the air out through the grille in the top cap.
Foam seals the filter's top ring to the transition plate and the fan's front plate to the transition
plate, so the outer shell doesn't have to be airtight.

## Measure these before printing

Change the value in `cad/src/lib/params.py`, then run `cad run src/assembly.py` and
`PYTHONPATH=src cad run checks/check_fit.py` from `cad/`.

| Parameter | Now | What to measure |
|---|---|---|
| `FAN_PLATE_T` | 10 | Fan front plate + grille thickness. The deck posts are cut to it: too short and the deck won't clamp the fan |
| `FAN_PLATE`, `FAN_PLATE_CORNER_R` | 180, 3 | Plate size and corner radius. Corners are only 2.7 mm from the shell wall |
| `FAN_COLLAR_OD` | 145 | Collar outer diameter (deck hole Ø148, cap duct Ø148) |
| `FILTER_D`, `FILTER_H` | 200, 293 | Your PANCA filter (Xiaomi's datasheet says 200 × 293) |
| Filter top ring | — | The foam seal lands at Ø172–194, so the ring's flat face must cover that band |
| `INSERT_HOLE_D` | 4.0 | Hole for your M3 × 4 inserts (4.0 suits a 4.5–5 mm knurl) |
| SG90 tab holes | ±13.8 | `SERVO_TAB_HOLE_DX` in `electronics.py` |

## Print list (PETG for everything near the motor; PLA is fine for the shell)

| Part | Qty | Orientation | Size (mm) |
|---|---|---|---|
| shell_lower_a / _b | 1 + 1 | upright, turned ~21° on the bed | 229 footprint × 246 tall |
| shell_upper_a / _b | 1 + 1 | upright, turned ~21° | 229 × 183 |
| tray | 1 | as modelled | 224 × 224 × 10 |
| transition_plate | 1 | upside down | 241 × 10 |
| deck | 1 | upside down (posts up) | 220 × 17.5 |
| top_cap | 1 | upside down (grille face on the bed) | Ø249 × 17 |
| switch_bracket, fork_horn, esp32_holder, psu_box, psu_lid, mains_cradle | 1 each | base down / flat | small |

## Hardware

- M3 × 10 socket head: 24 (shell seams 12, ring joint 4, transition plate → shell 4, deck → transition plate 4)
- M3 × 6 socket head: 12 (top cap 4, electronics mounts 8)
- M3 × 4 brass inserts: 36 (seam flanges on the "a" halves 12, lower-ring bosses 4, upper-ring columns 4,
  transition plate 4, cap lip 4, deck 8)
- Soft closed-cell foam tape: 10 × 5 mm (~0.6 m) for the filter seal ring; 6 × 3 mm (~0.7 m) under the fan
  plate; one Ø190 × 5 mm pad on the tray
- Electronics: ESP32-C3 SuperMini, SG90, MTS-101 toggle (M6 bushing), 16 mm momentary push button with
  5 V LED ring, HLK-5M05, 2 × WAGO 221-413, inline 5×20 fuse holder + 1 A slow-blow fuse, PG7 cable
  gland, 2-core mains cord with plug (0.75 mm²), 1000 µF 10 V capacitor, 10 k / 330 Ω / 1 k
  resistors, BC547, heat-shrink, small zip ties

## Assembly order

1. Heat-set all the inserts.
2. Shell: screw each ring's halves together at the seams. Heads go on the "b" half; use a short L-key from inside.
   Stack the upper ring on the lower one and drive 4 × M3 × 10 down through the tabs with a long hex driver.
3. Fan module, on the bench: foam ring in the transition plate's filter seat (underside), foam strip on
   its top, fan face-down onto it, deck over the collar, 4 × M3 × 10 down through the deck posts.
4. Lower the fan module into the top of the shell and screw it down: 4 × M3 × 10 through the transition
   plate's ears into the shell columns.
5. Electronics onto the deck. Run the cord in through the PG7 gland and zip-tie it to the anchors up the
   inside wall. Wire as `circuit/wiring.html`.
6. Flash the ESP32 over USB **with the mains unplugged**. Tune "Servo centre trim" and "Switch throw"
   until each press flips the toggle cleanly. Then fit the top cap (4 × M3 × 6).
7. Filter: slide it in from below, put the tray on with its ears between the feet, push it up and turn
   it clockwise until it stops. To change the filter, reverse this.

## Safety

The mains side runs at 230 V. Keep every joint heat-shrunk or inside a WAGO, keep the fuse and the
gland, and never open the purifier or plug in USB while it's connected to mains. Test it the first
time on a socket protected by an RCD/ELCB.
