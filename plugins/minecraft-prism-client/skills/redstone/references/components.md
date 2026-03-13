# Redstone Component Reference

Quick reference for every redstone component's behavior in Java Edition. Consult when explaining components to users or verifying build correctness.

## Power Sources

### Lever
- **Output:** Constant signal strength 15 while ON
- **Placement:** Any solid surface (top, side, bottom of block)
- **Toggle:** Click to flip ON/OFF — stays until clicked again
- **Powers:** The block it's attached to + adjacent components

### Button (Stone / Wood)
- **Output:** Pulse of signal strength 15
- **Duration:** Stone = 10 game ticks (1 second). Wood = 15 game ticks (1.5 seconds)
- **Placement:** Any solid surface
- **Wood only:** Can be activated by arrows (useful for ranged activation)
- **Powers:** The block it's attached to + adjacent components

### Pressure Plate
- **Output:** Signal strength 15 when entity is standing on it
- **Types:** Stone (players/mobs only), Wood (players/mobs/items/arrows), Heavy weighted (signal varies with entity count), Light weighted (signal varies with entity count)
- **Placement:** Top of solid block
- **Powers:** The block below it + adjacent components

### Redstone Torch
- **Output:** Constant signal strength 15 when lit
- **Placement:** Top or side of any solid block
- **Inverts:** Turns OFF when the block it's attached to is powered
- **Powers strongly:** The block directly above it
- **Powers weakly:** All adjacent blocks except the one it's attached to
- **Burnout:** 8+ state changes in 60 game ticks = temporary burnout

### Redstone Block
- **Output:** Constant signal strength 15 in all directions
- **Cannot be turned off** — always outputs power
- **Movable by pistons** — useful for compact circuits and flying machines
- **Powers:** All adjacent dust and components

### Daylight Detector
- **Output:** Signal strength 0-15 based on sun position
- **Click to toggle:** Normal mode (strongest at noon) vs inverted mode (strongest at midnight)
- **Useful for:** Automatic lighting, day/night activated farms

### Tripwire Hook
- **Output:** Signal strength 15 when string between two hooks is disturbed
- **Placement:** Two hooks facing each other, up to 40 blocks apart, connected by string
- **Detects:** Entities walking through, string being broken

### Observer
- **Output:** 2 game tick pulse at signal strength 15
- **Triggers on:** Block state change detected by its face
- **Placement:** Detecting face (the "eye") faces the block to watch. Output face (red dot) faces the signal destination
- **Delay:** 2 game ticks between detection and output

### Target Block
- **Output:** Signal strength varies with arrow accuracy (1-15, bullseye = 15)
- **Duration:** 10 game ticks (1 second)
- **Unique:** Only block that can be strongly powered by redstone dust on top of it

## Signal Transmission

### Redstone Dust
- **Signal decay:** Loses 1 strength per block traveled
- **Range:** Maximum 15 blocks from source
- **Connection:** Auto-connects to adjacent dust, repeaters, comparators, and most mechanism components
- **Up/down:** Dust can travel up the side of a block if there's dust on top. Cannot go down unless there's space
- **Powers weakly:** The block it sits on top of
- **Transparent blocks:** Cannot be placed on glass, slabs (bottom), leaves, or other transparent blocks
- **Important:** Dust does NOT strongly power blocks — dust on a block cannot activate dust on an adjacent block through that block

### Redstone Repeater
- **Function:** One-way signal booster + delay + diode
- **Signal boost:** Resets any input signal to strength 15
- **Delay:** 1-4 redstone ticks (2-8 game ticks). Right-click to increase
- **Direction:** Only transmits from back (input) to front (output). The front has a single torch indicator
- **Locking:** A powered repeater pointing into the SIDE of another repeater locks it. Locked repeater holds its current output state regardless of input changes
- **Strongly powers:** The block in front of it
- **Placement:** Only on top of solid blocks, facing the output direction

### Redstone Comparator
- **Compare mode** (front torch unlit): Outputs rear signal if >= both side signals, else 0
- **Subtract mode** (front torch lit): Output = rear - max(sides), minimum 0
- **Container reading:** Reads fill level of container behind it as signal 0-15
- **Direction:** Input from back, side inputs from left/right, output from front
- **Does NOT boost signal** — output can be lower than input
- **Placement:** Only on top of solid blocks

## Mechanism Components (Outputs)

### Piston / Sticky Piston
- **Activation:** Powered directly, or quasi-powered (power in space above)
- **Push limit:** 12 blocks
- **Sticky piston:** Pulls 1 block back on retract (if the block is movable)
- **Timing:** 3 game ticks to extend, instant retract (Java)
- **Cannot push:** Obsidian, bedrock, extended pistons, most containers

### Redstone Lamp
- **Activation:** Any adjacent power source
- **On delay:** Instant
- **Off delay:** 2 game ticks after power removed (creates brief "afterglow")
- **Light level:** 15 when on, 0 when off

### Dispenser
- **Activation:** Powered directly or quasi-powered
- **Function:** Uses/places items from inventory (shoots arrows, places water, ignites TNT, etc.)
- **Pulse-activated:** Does one action per pulse. Sustained power = one action only

### Dropper
- **Activation:** Powered directly or quasi-powered
- **Function:** Drops or transfers 1 item per pulse into adjacent inventory or world
- **Key difference from dispenser:** Never "uses" items — just ejects/transfers them

### Hopper
- **Function:** Pulls items from above, pushes items to connected container
- **Direction:** Points toward its output destination (set when placed by clicking the destination)
- **Locking:** Stops transferring when powered by redstone
- **Transfer rate:** 1 item per 8 game ticks (2.5 items/second)
- **Interaction with comparator:** Comparator reads fill level as signal 0-15

### Note Block
- **Activation:** Powered or clicked
- **Pitch:** Right-click to change (25 notes, 2 octaves)
- **Instrument:** Determined by block below it (wood = bass, sand = snare, glass = clicks, etc.)

### TNT
- **Activation:** Powered by any adjacent signal
- **Fuse:** 40 game ticks (4 seconds) after activation
- **Destroyed by:** Explosions, fire, lava (these also ignite it)

### Door / Trapdoor / Fence Gate
- **Activation:** Powered directly (doors check both halves)
- **Iron variants:** Only openable by redstone (not by hand)
- **Wood variants:** Openable by both redstone and right-click

### Rail Types
- **Powered Rail:** Accelerates minecarts when powered, brakes when unpowered
- **Detector Rail:** Outputs signal when minecart passes over it
- **Activator Rail:** Activates minecart functionality (ignites TNT minecart, drops hopper minecart items, ejects players)
