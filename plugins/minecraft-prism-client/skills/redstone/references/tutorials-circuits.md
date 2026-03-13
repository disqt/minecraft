# Redstone Circuit Reference — Build-Ready Designs

Extracted from Minecraft Wiki (March 2025). Covers clock circuits, pulse circuits, memory circuits, and advanced builds. All dimensions are Width x Depth x Height (WxDxH) in blocks.

---

## Table of Contents

1. [Clock Circuits](#clock-circuits)
2. [Pulse Circuits](#pulse-circuits)
3. [Memory Circuits](#memory-circuits)
4. [Advanced Circuits](#advanced-circuits)
5. [Circuit Design Properties Glossary](#circuit-design-properties-glossary)

---

## Circuit Design Properties Glossary

Before diving into specific circuits, here are the standard design properties referenced throughout:

- **1-high**: Fits in a single vertical block layer
- **1-wide**: At least one horizontal dimension is exactly 1 block
- **Flat**: Buildable on ground with no stacked components
- **Flush**: Does not extend beyond the wall/floor/ceiling surface
- **Seamless**: No redstone components visible before or after operation
- **Silent**: Produces no mechanical sound (no pistons)
- **Instant**: Output responds immediately to input (0-tick delay)
- **Stackable**: Can stack vertically with unified control
- **Tileable**: Can be placed next to copies; each operates independently

---

## Clock Circuits

Clocks produce repeating pulse loops at a specific frequency. Period is measured in game ticks (gt); 1 gt = 0.05 seconds, 20 gt = 1 second.

### Rapid Pulsar (Torch Burnout Clock)
- **Dimensions**: Minimal (inline)
- **Materials**: 2 redstone torches, redstone dust
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Place two redstone torches connected by the same piece of redstone dust, exploiting torch burnout behavior
- **How it works**: Both torches burn out simultaneously, creating a constant rapid on-off pulse
- **Important notes**: Relies on torch burnout mechanic; simplest possible clock

### 5-Torch Loop Clock
- **Dimensions**: Loop configuration (compact)
- **Materials**: 5 redstone torches
- **Period**: 20gt (1.0s)
- **Build**: Join 5 redstone torches in a loop where each torch's output feeds the next torch's input
- **How it works**: The oldest clock in Minecraft. Each torch inverts its input; odd number of torches creates oscillation. Can extend period by adding torch pairs
- **Important notes**: Historical design; superseded by more compact options

### 4-Torch Cross Clock
- **Dimensions**: Compact cross pattern
- **Materials**: 4 redstone torches
- **Period**: 16gt (0.8s)
- **Build**: Each redstone torch's output feeds into two other torches, forming interconnected RS-NOR latches
- **How it works**: Resembles two interconnected RS-NOR latches that continuously toggle each other
- **Important notes**: More complex wiring than the 5-torch loop

---

### 4gt Repeater Loop Clock
- **Dimensions**: 2x3x2
- **Materials**: 2 redstone repeaters, redstone dust, 1 redstone torch, 1 solid block
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Place torch on a solid block to start the loop. Two repeaters form a closed loop with dust. The torch and block can be removed after the clock starts running
- **How it works**: Signal chases itself around the repeater loop indefinitely. The torch provides the initial pulse to start oscillation
- **Important notes**: The starting torch/block can be removed once running. Very compact and reliable

### Switchable 4gt Repeater Loop
- **Dimensions**: 3x4x2
- **Materials**: 2 repeaters, 1 sticky piston, 1 lever, redstone dust
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Same repeater loop as above, but a sticky piston controlled by a lever completes or breaks the circuit loop
- **How it works**: Lever toggles the piston, which inserts or removes a block to complete or break the loop
- **Important notes**: Controllable on/off; good for practical builds

### 2gt Repeater Loop (10 Hz Clock)
- **Dimensions**: 3x4x2
- **Materials**: Multiple repeaters in loop
- **Period**: 2gt (0.1s, 10 Hz)
- **Build**: Repeater loop configured for minimum delay
- **How it works**: Runs at maximum redstone speed
- **Important notes**: Java Edition only. Runs too fast for some redstone components to respond

---

### Basic Torch-Repeater Clock
- **Dimensions**: Compact expandable loop
- **Materials**: 1 redstone torch, repeaters (minimum 4gt total delay)
- **Period**: 12gt with 4gt repeater (0.6s, ~1.7 Hz); adjustable
- **Build**: Single torch provides oscillation; repeaters in series provide most of the delay. Total repeater delay must be at least 4gt or the torch burns out
- **How it works**: Torch inverts signal; repeaters slow it down. The delayed inverted signal feeds back to the torch input
- **Important notes**: Repeaters must total at least 4gt delay. Expandable by adding repeaters

### Vertical Torch-Repeater Clock (Design E)
- **Dimensions**: 1x5x4 minimum, extends vertically
- **Materials**: 1 torch, repeaters (adds 2 repeaters per block of height)
- **Period**: 72gt (3.6s) with 32gt repeater delay; expandable
- **Build**: Extends vertically, can be extended indefinitely. A lever stops the clock with output OFF
- **How it works**: Signal travels up through stacked repeaters and a torch at the end inverts and feeds back
- **Important notes**: Good for long-period clocks in a small footprint. Lever-controllable

### Compact Vertical Torch-Repeater Clock (Design D)
- **Dimensions**: 1x3x3
- **Materials**: 1 torch, 1 repeater, solid blocks
- **Period**: 12gt (0.6s, ~1.67 Hz) with 4gt repeater
- **Build**: Compressed vertical format that can be buried in walls. Output from dust side is inverted
- **How it works**: Same torch-repeater oscillation principle in a tighter package
- **Important notes**: Can be hidden inside walls; output is inverted on the dust side

---

### 4gt Subtraction Clock (Comparator)
- **Dimensions**: 2x2x2
- **Materials**: 1 comparator, redstone dust
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Place a comparator in subtraction mode with its output looping back to its side input via redstone dust
- **How it works**: The comparator subtracts the side input from the rear input. Signal declines by 1 per tick, creating oscillation
- **Important notes**: Works with input strength as low as 2. One of the most compact clocks possible

### 8-20gt Subtraction Clock (Comparator + Repeater)
- **Dimensions**: 2x3x2
- **Materials**: 1 comparator, 1 repeater, redstone dust, solid blocks
- **Period**: 8-20gt depending on repeater delay setting
- **Build**: Add a repeater in the feedback loop of a subtraction clock to slow it down
- **How it works**: The repeater adds configurable delay to the feedback path
- **Important notes**: Good for adjustable-speed clocks without rebuilding

### Super-Compact Subtraction Clock
- **Dimensions**: 2x1x3
- **Materials**: 1 comparator, 3 redstone dust, power source
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Minimal layout with comparator and dust in a tight column
- **How it works**: Same subtraction principle in the smallest possible form
- **Important notes**: Only 6 blocks total. Excellent for space-constrained builds

### 18gt Fader Pulser
- **Dimensions**: 1x4x4
- **Materials**: 1 comparator, 1 redstone torch, redstone dust
- **Period**: 18gt (0.9s, ~1.1 Hz)
- **Build**: Torch charges a fader loop; signal strength declines by 2 per cycle
- **How it works**: The comparator fader effect causes signal to decay over time, then the torch recharges it
- **Important notes**: Distinctive slow pulse rhythm

### 58gt Fader Pulser
- **Dimensions**: 2x4x2
- **Materials**: 2 comparators, 1 redstone torch, redstone dust
- **Period**: 58gt (2.9s, ~0.34 Hz)
- **Build**: Extended fader loop with two comparators
- **How it works**: Additional comparator doubles the fade time before torch recharge
- **Important notes**: Add more comparators to further extend period

---

### Single-Item Etho Hopper Clock
- **Dimensions**: Compact (2 hoppers + 2 pistons)
- **Materials**: 2 hoppers, 2 sticky pistons, redstone dust
- **Period**: First cycle 9gt Java / 16gt Bedrock; subsequent cycles 14gt Java / 16gt Bedrock
- **Build**: Two hoppers face each other. Two sticky pistons (both must be sticky) read the item position. A single item bounces between the hoppers
- **How it works**: Item transfers between hoppers at hopper speed. Pistons with comparators detect which hopper holds the item
- **Important notes**: Both pistons must be sticky. Period formula for multiple items: [(n-1) x 8 + 2] x 2 gt (Java)

### Multiplicative Hopper-Dropper Clock (MHDC)
- **Dimensions**: Varies (72 blocks for multi-stage)
- **Materials**: Hoppers, droppers, redstone dust
- **Period**: Extremely long — multi-stage versions can reach periods of 10.7 years across 72 blocks
- **Build**: Chain hopper clocks with droppers as multipliers
- **How it works**: Each stage multiplies the period of the previous stage
- **Important notes**: For ultra-long timing applications (days, weeks, or longer)

---

### Dropper-Dropper Clock
- **Dimensions**: 7x4x2
- **Materials**: 2 droppers, 2 repeaters (set to 3 redstone ticks), redstone dust
- **Period**: 32gt (1.6s) with single item; formula: (n x 8 + 6) x 2 gt for multiple items
- **Build**: Two droppers face each other. Repeaters set to 3rt. Items cycle between droppers
- **How it works**: A dropper fires an item to the other dropper, which fires it back after the repeater delay
- **Important notes**: No hoppers or pistons needed (uses quartz for repeaters instead). May need reset after chunk reload

---

### Simple 4-Tick Piston Clock
- **Dimensions**: Small inline
- **Materials**: 1 sticky piston, 1 redstone block, redstone dust
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Sticky piston faces a redstone block. Dust connects the block's position to the piston's input
- **How it works**: Redstone block powers the dust, which powers the piston, which pushes the block away, which unpowers the dust, which retracts the piston, which pulls the block back
- **Important notes**: Java Edition only. Very simple. Stoppable by powering the piston externally

### Self-Powered Piston Clock (Design E)
- **Dimensions**: Expandable vertically
- **Materials**: 1 sticky piston, redstone wire, solid block, obsidian, slime block, redstone block
- **Period**: 6gt (0.3s, ~3.33 Hz)
- **Build**: Uses quasi-connectivity and block update detection. Only vertical piston clock design
- **How it works**: Quasi-connectivity causes the piston to extend on block updates; slime/obsidian interaction creates the oscillation
- **Important notes**: Java Edition only. Outputs 5gt on, 1gt off. Toggleable with lever

---

### Single Observer 4gt Clock
- **Dimensions**: Minimal loop
- **Materials**: 1 observer, redstone dust
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Run redstone dust from the observer's observing face around to its output face, creating a feedback loop
- **How it works**: Observer detects its own output state change through the dust feedback loop
- **Important notes**: Toggleable with lever or piston. One of the simplest and most reliable clocks

### Double Observer Clock (6gt)
- **Dimensions**: 2 blocks inline
- **Materials**: 2 observers
- **Period**: 6gt (0.3s, ~3.33 Hz); pulse: 2gt on, 4gt off
- **Build**: Place two observers facing each other directly
- **How it works**: Each observer detects the other's state change, creating perpetual oscillation
- **Important notes**: Must place observers manually facing each other (not auto-placed)

### Double Observer Clock (4gt)
- **Dimensions**: 2 blocks inline
- **Materials**: 2 observers (placed via piston)
- **Period**: 4gt (0.2s, 5 Hz)
- **Build**: Use a piston to push one observer into place facing the other
- **How it works**: Functions like a single observer clock due to placement method
- **Important notes**: Different behavior than manually-placed double observer due to initial state

### N-Observer Clock
- **Dimensions**: N blocks in a chain
- **Materials**: 3+ observers, solid blocks (for odd numbers)
- **Period**: N redstone ticks (where N = observer count); pulse: 1rt on, (N-1)rt off
- **Build**: Chain observers together. Each observer adds 2gt delay. Handle odd numbers with solid blocks between some observers
- **How it works**: Signal propagates through the observer chain and loops back
- **Important notes**: Scalable to any period in increments of 1 redstone tick

---

### Despawn Clock
- **Dimensions**: 3x3x2
- **Materials**: 1 dropper, 1 pressure plate, 1 redstone torch, solid blocks
- **Period**: ~5 minutes (item despawn timing)
- **Build**: Torch triggers dropper to eject an item onto a pressure plate. After 5 minutes, the item despawns, releasing the pressure plate, which re-triggers the dropper
- **How it works**: Exploits the 5-minute item despawn timer as a clock source
- **Important notes**: Any nearby player might accidentally pick up the despawning item. Chain multiple for longer periods. Can use eggs from chickens to auto-refill

### Daylight Detector Clock
- **Dimensions**: Varies
- **Materials**: Daylight detector, comparators
- **Period**: 1 in-game day (24000gt = 20 real minutes)
- **Build**: Daylight detector with comparator output. Adjustable duty cycle via comparator threshold
- **How it works**: Daylight detector output changes with in-game time of day
- **Important notes**: Does not lose time if the chunk is unloaded. Weather may interfere. Phase is fixed to in-game time

---

### Clock Period Multipliers

#### T Flip-Flop Doubler
- **Materials**: Any T flip-flop circuit
- **Purpose**: Doubles any clock's period and produces equal on/off duty cycle
- **How it works**: Each input pulse toggles the output state

#### Latching Clock Multiplier (Ring Counter)
- **Materials**: Latched repeaters, edge detector, torchless repeater loop
- **Purpose**: Multiplies input clock period by N (number of latches, max ~12)
- **Build**: Ring counter takes clock input; requires separate startup circuit. Chain multipliers indefinitely
- **How it works**: Signal advances one position in the ring per input clock cycle
- **Important notes**: Combine with coprime factors (e.g., 7, 5, 3) for efficiency

#### Factorial Stacking
- **Materials**: Two clocks with coprime periods, AND gate
- **Purpose**: Creates very long periods from short clocks
- **Build**: Two clocks with coprime periods (no common factors) feeding an AND gate
- **Example**: 60-second clock (1200gt) from 48gt + 50gt clocks
- **Important notes**: Requires simultaneous start. Avoid clocks with common factors

#### Linear Feedback Shift Register (LFSR)
- **Materials**: Repeaters tapped at intervals
- **Purpose**: Arbitrary-duration delays and pseudorandom sequences
- **Formula**: Cycle time = 0.4 x (2^n - 1) seconds
- **How it works**: Feedback from specific tap points creates a pseudo-random sequence that eventually repeats

---

## Pulse Circuits

Pulse circuits produce signals of specific durations, or react to particular pulse characteristics.

### Pulse Generators

#### Circuit Breaker Pulse Generator
- **Dimensions**: 1x3x3 (9 blocks)
- **Materials**: 1 sticky piston, 1 regular piston, 1 repeater, redstone dust
- **Timing**: 1-tick circuit delay, 1-tick output pulse
- **Build**: Power the output through a block, then remove the block to keep the output pulse short. Adjust repeater delay for variable output length
- **How it works**: Piston removes the block that is conducting the output signal, cutting the pulse short
- **Important notes**: Adjustable output pulse length via repeater setting

#### Observer Pulse Generator
- **Dimensions**: 1x1x3 (3 blocks), tileable
- **Materials**: 1 observer, 1 piston, redstone dust
- **Timing**: 2-tick delay (Java), 1-tick output pulse
- **Build**: Observer detects piston movement. Flexible orientation; output can be rising or falling edge
- **How it works**: When input activates the piston, the observer detects the block state change and outputs a pulse
- **Important notes**: Very compact. Tileable for multi-channel pulse generation

#### Dust-Cut Pulse Generator
- **Dimensions**: 1x4x3 (12 blocks)
- **Materials**: 1 piston, redstone dust, solid blocks
- **Timing**: 0-tick (instant) delay, 1.5-tick output pulse
- **Build**: Piston moves a block that cuts the output dust line
- **How it works**: Output powers instantly through dust, then the piston moves a block to physically disconnect the dust line
- **Important notes**: Instant circuit delay makes this ideal for timing-critical applications

#### NOR-Gate Pulse Generator
- **Dimensions**: 1x4x3 (12 blocks), silent
- **Materials**: 1 repeater, 1 redstone torch, redstone dust, solid blocks
- **Timing**: 2-tick delay, 1-tick output pulse
- **Build**: Standard NOR gate arrangement comparing current power to power from 2 ticks prior
- **How it works**: The torch and repeater create a brief window where input is on but the delayed copy hasn't arrived yet
- **Important notes**: Silent operation (no pistons). Good for stealth builds

#### Locked-Repeater Pulse Generator
- **Dimensions**: 2x3x2 (12 blocks), flat, silent
- **Materials**: 2 repeaters, 1 redstone torch, solid blocks, lever
- **Timing**: 2-tick delay, 1-tick output pulse
- **Build**: Locked repeater allows pulse through when lever is disabled. Adjust repeater delays for variable timing
- **How it works**: One repeater locks the other after a set delay, cutting the output pulse
- **Important notes**: Flat design fits under floors. Silent operation

#### Comparator-Repeater Pulse Generator
- **Dimensions**: 2x4x2 (15 blocks), flat, silent
- **Materials**: 1 comparator, 1 repeater, redstone dust
- **Timing**: 1-tick delay, 2-tick output pulse
- **Build**: Comparator powers output immediately; delayed signal from repeater shuts it off
- **How it works**: Race condition between fast comparator path and slow repeater path creates a fixed-width pulse
- **Important notes**: Repeater is adjustable for longer pulses

---

### Pulse Limiters

Reduce the duration of long input pulses to a fixed short output pulse.

#### Circuit Breaker Pulse Limiter
- **Dimensions**: 1x3x3 (9 blocks)
- **Materials**: 1 sticky piston, 1 regular piston, 1 repeater
- **Timing**: 1-tick delay, 1-tick output
- **Build**: Identical to the circuit breaker pulse generator. Repeater adjustable for variable output length
- **How it works**: Long input pulse is cut short by piston removing the conducting block
- **Important notes**: Same circuit serves as both generator and limiter

#### Dust-Cut Pulse Limiter
- **Dimensions**: 1x5x3 (15 blocks), instant
- **Materials**: 1 piston, redstone dust, solid blocks
- **Timing**: 0-tick delay, 1.5-tick output
- **Build**: Moving block cuts the output dust line after the pulse starts. Passes through pulses shorter than 1.5 ticks unchanged
- **How it works**: Acts as an "ideal" limiter — short pulses pass through; long pulses are truncated
- **Important notes**: Does not repeat the input signal (no signal refresh)

#### NOR-Gate Pulse Limiter
- **Dimensions**: 1x4x3 (12 blocks), silent, 1-wide
- **Materials**: Repeaters, 1 redstone torch, solid blocks
- **Timing**: 2-tick delay, 1-tick output
- **Build**: Same NOR principle as the generator. Remove block above torch to extend pulse to 2 ticks
- **How it works**: Compares current vs. prior power states to produce a fixed-width pulse
- **Important notes**: 1-wide design fits in tight spaces

#### Locked-Repeater Pulse Limiter
- **Dimensions**: 2x4x2 (16 blocks), flat, silent
- **Materials**: Repeaters, 1 redstone torch, solid blocks
- **Timing**: 3-tick delay, 1-tick output
- **Build**: Repeater locking mechanism shuts off output after 1 tick regardless of input length
- **How it works**: Second repeater locks the first after the set delay, truncating the pulse
- **Important notes**: Output repeater is adjustable

#### Dropper-Hopper Pulse Limiter
- **Dimensions**: 1x4x2 (8 blocks), flat, silent
- **Materials**: 1 dropper, 1 hopper, 1 comparator, solid blocks
- **Timing**: 3-tick delay, 3.5-tick output
- **Build**: Dropper pushes item into hopper; comparator reads hopper contents until hopper returns item
- **How it works**: Item transfer time between dropper and hopper sets the fixed output duration
- **Important notes**: Output signal strength is 1 or 3 depending on item type

---

### Pulse Extenders

Increase the duration of short input pulses.

#### Single Repeater Extender
- **Dimensions**: 1x1x2 (2 blocks), flat, silent
- **Materials**: 1 repeater
- **Timing**: 1-4 tick delay, 1-4 tick output
- **Build**: Single repeater on a block. Set delay to desired extension
- **How it works**: Repeater increases pulse duration to match its delay setting. Only works for input pulses shorter than the repeater delay
- **Important notes**: Simplest possible extender. Only extends pulses shorter than the set delay

#### Repeater-Line Pulse Extender
- **Dimensions**: 2xNx2, flat, silent
- **Materials**: Multiple repeaters, redstone dust
- **Timing**: 0-tick (instant) or 4-tick (delayed), up to 4 ticks extension per repeater
- **Build**: Multiple repeaters in series. Input must be at least 4 ticks for the instant version
- **How it works**: Each repeater in the chain adds its delay to the pulse duration
- **Important notes**: Scalable to any desired extension

#### Dropper-Latch Pulse Extender
- **Dimensions**: 2x6x2 (24 blocks), flat, silent
- **Materials**: 1 dropper, 1 hopper, repeaters, solid blocks
- **Timing**: 5-tick delay, 5 ticks to 256 seconds output
- **Build**: Each item in the hopper adds 8 ticks to pulse duration. Up to 320 items can be loaded
- **How it works**: Items transfer through the hopper at a fixed rate; comparator output stays on until all items have passed
- **Important notes**: Enormous range (5 ticks to over 4 minutes). 1-wide variant exists using two droppers

#### Hopper-Clock Pulse Extender
- **Dimensions**: Varies (1-wide or flat), silent
- **Materials**: Hoppers, 1 sticky piston, 1 regular piston, 1 comparator, solid blocks
- **Timing**: 1-tick delay, 4 ticks to 256 seconds output
- **Build**: Hopper clock with regular piston replacing one sticky piston. Single item = 4-tick pulse; each additional item adds 8 ticks
- **How it works**: Modified hopper clock where the non-sticky piston allows the clock to stop after one cycle
- **Important notes**: Wide range with fine control via item count

#### Fader Pulse Extender
- **Dimensions**: 2xNx2, flat, silent
- **Materials**: Multiple comparators, redstone dust
- **Timing**: 0-tick delay, input pulse + up to 15 ticks per comparator
- **Build**: Chain of comparators in subtraction mode. Extension depends on input signal strength
- **How it works**: Signal strength decays through each comparator, extending the total powered duration
- **Important notes**: Requires minimum pulse length equal to comparator count. Signal strength decays, so output may be weaker

#### MHC (Multiplicative Hopper Clock) Pulse Extender
- **Dimensions**: 6x6x2 (72 blocks), flat
- **Materials**: 2 sticky pistons, hoppers, solid blocks
- **Timing**: 3-tick delay, up to 22 hours output
- **Build**: Multiplicative hopper clock configuration
- **Formula**: Output = 0.4 seconds x top_items x (2 x bottom_items - 1)
- **How it works**: Two hopper stages multiply their periods together
- **Important notes**: For extremely long delays (hours)

#### MHDC (Multiplicative Hopper-Dropper Clock) Pulse Extender
- **Dimensions**: 5x7x2 (70 blocks), flat
- **Materials**: Sticky pistons, hoppers, 1 dropper, solid blocks
- **Timing**: 5-tick delay, up to 81 hours output
- **Formula**: Duration = hoppers x (2 x droppers - 1) x 0.8 seconds
- **How it works**: Dropper counter multiplies the hopper-dropper clock period
- **Important notes**: Maximum duration over 3 days of real time

---

### Pulse Multipliers

Output multiple pulses for every single input pulse.

#### Observer Pulse Doubler (Dual Edge Detector)
- **Dimensions**: 1x1x1 (single block), flat, silent, tileable
- **Materials**: 1 observer
- **Timing**: 1-tick delay, two 1-tick pulses per input
- **Build**: Observer faces the input signal line directly
- **How it works**: Observer detects both the rising edge (signal on) and falling edge (signal off), producing two pulses
- **Important notes**: Input must be at least 3 ticks long. Shorter pulses need a redstone lamp buffer in front

#### Subtraction 1-Clock Pulse Multiplier
- **Dimensions**: 2x3x2 (12 blocks), flat, silent
- **Materials**: 1 repeater, 1 redstone torch, solid blocks
- **Timing**: 1-tick delay, 1-tick pulses
- **Build**: Enabled-clock design that runs while input is active
- **How it works**: A fast clock runs for the duration of the input pulse, producing multiple output pulses
- **Output count**: 5 pulses (stone button), 7 pulses (wooden button)
- **Important notes**: Does not repeat input signal

#### Dropper-Latch 2-Clock Pulse Multiplier
- **Dimensions**: 3x4x2 (24 blocks), flat, silent
- **Materials**: 2 droppers, 1 hopper, 1 repeater, solid blocks
- **Timing**: 3-tick delay, 1-320 two-tick pulses
- **Build**: Produces one 2-tick pulse per item in the bottom dropper
- **How it works**: Each item triggers one output pulse as it transfers through the system
- **Important notes**: Reset time = 0.4 seconds x pulse count

#### Dropper-Latch 1-Clock Pulse Multiplier
- **Dimensions**: 2x9x2 (36 blocks), flat, silent
- **Materials**: 1 dropper, hoppers, 1 repeater, solid blocks
- **Timing**: 5-tick delay, 2-777 one-tick pulses
- **Build**: Four 1-tick pulses per item in the middle hopper
- **How it works**: Items cycle through the hopper chain, each pass generating pulses
- **Important notes**: First and last items must be non-stackable

---

### Pulse Dividers

Output a signal only after receiving a certain number of input pulses.

#### Hopper-Loop Pulse Divider
- **Dimensions**: 2x(3 + pulse_count/2)x3
- **Materials**: Hoppers, 1 dropper, 1 comparator, redstone dust
- **Output**: 3-tick output pulse
- **Build**: Item moves through a hopper loop; each input pulse advances it one position. Output triggers when item reaches the comparator position
- **How it works**: Physical item position in the hopper chain acts as a counter
- **Important notes**: Even-count pulses require a second dropper. Output signal strength 1-3

#### Dropper-Hopper Pulse Divider
- **Dimensions**: 3x4x2 (24 blocks), flat
- **Materials**: 1 dropper, 1 hopper, 1 comparator, solid blocks
- **Output**: (4 x pulse_count) ticks
- **Build**: Counts pulses by moving items from dropper to hopper. Comparator detects when all items have transferred
- **How it works**: Each input pulse moves one item; output fires when the target count is reached
- **Important notes**: Counts up to 320 pulses. Requires reset period between uses

#### Inverted Binary Divider/Counter
- **Dimensions**: 3x5x2 (30 blocks), flat, silent, stackable
- **Materials**: Repeaters, redstone torches, solid blocks
- **Input**: 2 off-ticks minimum between pulses
- **Build**: Uses repeater latching to create a two-state counter. Stacking multiple modules creates an n-bit counter that divides by 2^n
- **How it works**: Each module is a 1-bit counter that toggles on each input pulse and carries to the next module
- **Important notes**: Infinitely stackable. Each layer doubles the division ratio

#### 1-Tick Binary Counter/Divider (Java Edition)
- **Dimensions**: 1x3x(2n+1) for 1-tick input
- **Materials**: Repeaters, sticky pistons
- **Build**: Uses sticky piston spitting behavior for fast counting
- **How it works**: Each module exploits piston mechanics to count at 1-tick speed
- **Important notes**: Java Edition only. Infinitely extensible; each module doubles divider ratio

---

### Edge Detectors

React to signal transitions rather than signal levels.

#### Rising Edge Detectors (RED)

##### Circuit Breaker RED
- **Dimensions**: 1x3x3 (9 blocks)
- **Materials**: 1 sticky piston, 1 regular piston, 1 repeater
- **Timing**: 1-tick delay, 1-tick output pulse
- **Build**: Detects when input turns on. Adjustable repeater delay increases output pulse width
- **How it works**: Same circuit as the pulse generator — block removal cuts the pulse short after the rising edge

##### Observer RED
- **Dimensions**: 1x1x3, 1x1x1, or 1x2x2 (multiple variants)
- **Materials**: 1 observer, 1 piston, solid blocks
- **Timing**: 2-tick delay (Java) / 4-tick delay (Bedrock), 1-tick pulse
- **Build**: Observer detects piston block state change when input goes high
- **How it works**: Piston extends on rising edge; observer detects the movement
- **Important notes**: Multiple orientation options. Works across editions with different timing

##### Dust-Cut RED
- **Dimensions**: 1x5x3 (15 blocks)
- **Materials**: 1 piston, redstone dust, solid blocks
- **Timing**: 0-tick (instant) delay, 1-1.5 tick pulse
- **Build**: Block movement cuts output dust line after the rising edge passes through
- **How it works**: Signal propagates instantly through dust, then piston disconnects the path
- **Important notes**: Instant response makes this the fastest rising edge detector

##### Subtraction RED
- **Dimensions**: 2x4x2 (16 blocks), flat, silent
- **Materials**: 1 comparator, repeaters, solid blocks
- **Timing**: 1-2 tick delay, 1-tick pulse
- **Build**: Comparator in subtraction mode detects the moment input exceeds the delayed reference
- **How it works**: Brief window where direct input is higher than the subtracted delayed copy

##### NOR-Gate RED
- **Dimensions**: 1x4x3 (12 blocks), silent
- **Materials**: 1 repeater, 1 redstone torch, solid blocks
- **Timing**: 2-tick delay, 1-tick pulse
- **Build**: Compares current input to delayed inverted copy
- **How it works**: Output is on only during the delay period before the inverted copy arrives

#### Falling Edge Detectors (FED)

##### Dust-Cut FED
- **Dimensions**: 1x4x3 (12 blocks), instant
- **Materials**: 1 piston, 1 repeater, solid blocks
- **Timing**: 0-tick delay, 2-tick output pulse
- **Build**: Piston retraction cuts the signal from a powered repeater
- **How it works**: When input drops, piston retraction creates a brief output before the repeater depowers

##### Moved-Observer FED
- **Dimensions**: 1x2x3 (6 blocks), 1-wide or flat variants
- **Materials**: 1 sticky piston, 1 observer, redstone dust
- **Timing**: 2-tick (Java) / 4-tick (Bedrock) delay, 1-tick pulse
- **Build**: Observer detects piston retraction when input turns off. Use glass block to prevent clock formation
- **How it works**: Sticky piston retracts on falling edge; observer detects the block movement
- **Important notes**: Glass block is critical to prevent unintended oscillation

##### Locked-Repeater FED
- **Dimensions**: 2x3x2 (12 blocks), flat, silent
- **Materials**: Repeaters, solid blocks
- **Timing**: 2-tick delay, 1-tick output pulse
- **Build**: Repeater locking detects signal cutoff
- **How it works**: Locked repeater releases its stored state when the locking signal drops

##### Subtraction FED
- **Dimensions**: 2x5x2 (20 blocks), flat, silent
- **Materials**: 1 comparator, 1 repeater, solid blocks
- **Timing**: 1-tick delay, 1-tick pulse
- **Build**: Mirror of the subtraction RED, detecting when delayed copy exceeds the now-off direct input

#### Dual Edge Detectors (DED)

##### Moving-Block DED
- **Dimensions**: 1x3x3 (9 blocks), 1-wide
- **Materials**: 1 sticky piston, 1 repeater, redstone dust
- **Timing**: 1-tick delay, 1-tick output pulse on both edges
- **Build**: Block movement triggers output on both piston extension and retraction
- **How it works**: Piston moves block on rising edge and retracts on falling edge; both actions produce output
- **Important notes**: Remove block above torch for 1.5-tick pulse variant

##### Observer DED (Simple)
- **Dimensions**: 1x1x1 (single block)
- **Materials**: 1 observer
- **Timing**: 1-tick delay, 1-tick pulse on each edge
- **Build**: Observer facing the signal source directly
- **How it works**: Observer inherently detects all block state changes — both on and off transitions
- **Important notes**: The observer is a natural dual edge detector by design

---

### Pulse Length Detectors

React only to pulses within a specific duration range.

#### Long Pulse Detector
- **Dimensions**: 2x6x3 (36 blocks) silent, or 2x5x2 (20 blocks) flat
- **Materials**: AND gate, repeaters, solid blocks
- **Build**: AND gate between the beginning and end of a repeater delay line
- **How it works**: Output is on only when both the direct input AND the delayed input are simultaneously active — meaning the pulse lasted longer than the delay
- **Important notes**: Output pulse is shortened by the delay amount (minimum 1 tick). Pulses shorter than the delay produce no output

#### Pulse Length Differentiator
- **Dimensions**: Varies
- **Materials**: Repeaters, solid blocks
- **Build**: Long and short pulses are routed to different outputs
- **How it works**: Delay lines of different lengths create multiple detection windows
- **Important notes**: Maintains tick-length of signals. Useful for Morse code systems

---

## Memory Circuits

Memory circuits maintain their output state until they receive a signal to change.

### RS Latches (Set/Reset)

The most fundamental memory circuit. Two inputs: Set (turns output ON) and Reset (turns output OFF).

#### RS-NOR Latch — Design A (Basic)
- **Dimensions**: 4x2x3
- **Materials**: 2 redstone torches, 6 redstone dust
- **Build**: Two torches cross-connected so each one's output feeds the other's input. Set/reset on one side, inverse output readable on opposite side
- **How it works**: Setting one torch OFF forces the other ON, and vice versa. The circuit is bistable — it stays in whichever state it was last set to
- **Important notes**: Most fundamental RS-NOR latch. Duplex inputs/outputs (I/O shared on same lines)

#### RS-NOR Latch — Design B (Compact)
- **Dimensions**: 3x2x3
- **Materials**: 2 redstone torches, 4 redstone dust
- **Build**: Slightly smaller version with opposite ends serving reset and inverse output
- **How it works**: Same cross-coupled torch principle as Design A
- **Important notes**: More compact but less flexible I/O routing

#### RS-NOR Latch — Design C (Isolated)
- **Dimensions**: 2x3x3
- **Materials**: 2 redstone torches, 4 redstone dust, 2 repeaters
- **Build**: Uses torches and repeaters to isolate outputs from inputs
- **How it works**: Repeaters provide signal isolation so output loads don't affect the latch state
- **Important notes**: Isolated outputs prevent external circuits from inadvertently changing latch state

#### RS-NOR Latch — Design D (Smallest Isolated)
- **Dimensions**: 2x3x2
- **Materials**: 2 redstone torches, 2 repeaters (no dust needed)
- **Build**: Most compact isolated design. Repeaters handle both isolation and signal routing
- **How it works**: Same principle with minimal materials
- **Important notes**: Most compact isolated RS latch possible

#### RS-NOR Latch — Design F (Vertical 1-Wide)
- **Dimensions**: 3x1x4
- **Materials**: 2 redstone torches, 3 redstone dust
- **Build**: One-block-wide vertical configuration. Duplex I/O with isolated outputs at alternate locations
- **How it works**: Vertical torch arrangement with dust connections running up and down
- **Important notes**: Ideal for fitting into 1-wide walls

#### Piston RS Latch — Design M
- **Dimensions**: 4x3x2
- **Materials**: 2 normal pistons, 1 redstone torch (no redstone dust)
- **Build**: Two pistons physically push a block back and forth between two positions
- **How it works**: Block position determines output state. Set input pushes block one way, reset pushes it back
- **Important notes**: No inverse output. Isolated inputs/outputs. No redstone dust needed

#### Piston RS Latch — Design N (Redstone Block)
- **Dimensions**: 4x1x1
- **Materials**: 2 normal pistons, 1 redstone block (no dust, no repeaters)
- **Build**: Redstone block between two opposing pistons. The block's position determines which side is powered
- **How it works**: Set fires one piston pushing the redstone block toward reset side (powering that output); reset fires the other piston pushing it back
- **Important notes**: Incredibly compact — just 4 blocks in a line. Dual outputs. Fully isolated I/O

#### Dropper RS Latch — Design P
- **Dimensions**: 3x1x2
- **Materials**: 2 droppers, 2 comparators
- **Build**: Two droppers face each other with comparators reading their contents. An item moves between them
- **How it works**: Set moves item to one dropper, reset moves it to the other. Comparators read which dropper contains the item
- **Important notes**: Small and tileable. Activates on rising edge

---

### T Flip-Flops (Toggle)

Single input toggles output between ON and OFF. Essential for converting buttons into toggle switches.

#### Copper Bulb T Flip-Flop ("Cop-Flop")
- **Dimensions**: 1x2x1
- **Materials**: 1 copper bulb, 1 comparator
- **Build**: Comparator reads the copper bulb's light state. Pulse the copper bulb to toggle
- **How it works**: Copper bulbs have a built-in toggle property — each redstone pulse flips their state. Comparator reads the current state as output
- **Important notes**: Revolutionary compact design introduced in Java 1.21. Called "Cop-Flop" or "Copper Flopper" by the community. Smallest possible T flip-flop

#### Observer T Flip-Flop — Design O1 (Horizontal)
- **Dimensions**: 6x1x1
- **Materials**: 1 observer, 1 redstone block, 2 sticky pistons
- **Build**: Two sticky pistons face each other with a redstone block between them. Observer triggers the toggle
- **How it works**: Each pulse causes one piston to push the redstone block to the other side. Observer detects the state change
- **Important notes**: Java Edition only. Rising edge triggered. 2-tick delay

#### Observer T Flip-Flop — Design O1 (Vertical)
- **Dimensions**: 3x4x1
- **Materials**: 1 observer, 1 redstone block, 2 sticky pistons
- **Build**: Same as horizontal but oriented vertically
- **How it works**: Same redstone block shuttle mechanism in vertical orientation
- **Important notes**: Java Edition only. Useful when horizontal space is limited

#### Observer T Flip-Flop — Design O3
- **Dimensions**: 4x2x1
- **Materials**: 1 observer, 1 redstone block, 2 sticky pistons
- **Build**: Compact observer-piston arrangement
- **How it works**: Falling edge triggered variant
- **Important notes**: Java Edition only. Triggers on signal off instead of signal on

#### Hopper/Dropper T Flip-Flop — Variant A (Grizdale's)
- **Dimensions**: 1x2x3
- **Materials**: 2 hoppers or droppers, 1 comparator, 1 item
- **Build**: Two hoppers/droppers stacked with a comparator reading the bottom one. Place a single item in either container
- **How it works**: Each input pulse moves the item between containers. Comparator reads whether the bottom container has the item
- **Important notes**: Compact and tileable in all three dimensions. One of the most practical T flip-flop designs

#### Hopper/Dropper T Flip-Flop — Variant B (Inline)
- **Dimensions**: 2x2x2 (or 4x2x2 with powered I/O)
- **Materials**: 2 droppers, 1 comparator
- **Build**: Two droppers facing each other with comparator output. Can be tiled in line, side-by-side, vertically, or all three
- **How it works**: Item shuttles between droppers on each pulse
- **Important notes**: Core delay only 1 tick. Highly tileable

#### Piston T Flip-Flop — Design M (Linear Tilable)
- **Dimensions**: 1x7x3
- **Materials**: 3 repeaters, 1 redstone torch, 2 sticky pistons
- **Build**: Hidden piston forms a monostable circuit. 1-tick signal lets piston toggle block position
- **How it works**: Each input pulse causes the pistons to shuttle a block to the opposite position
- **Important notes**: Can be tiled adjacent for multi-bit applications. Rising edge triggered

#### Piston T Flip-Flop — Design O (Quasi-Connectivity)
- **Dimensions**: 3x4x4
- **Materials**: 2 pistons, 2 redstone torches, 2 redstone dust, 1 redstone block
- **Build**: Uses quasi-connectivity for compact design. Only 10 blocks before inputs/outputs. 1-wide, vertical
- **How it works**: Quasi-connectivity causes piston to respond to indirect power, enabling a compact toggle
- **Important notes**: Java Edition only. Falling edge triggered

#### Piston T Flip-Flop with Reset — Design R
- **Dimensions**: 4x5x4
- **Materials**: 3 sticky pistons, 1 redstone torch, 8 redstone dust
- **Build**: Variation of Design O with an additional reset input
- **How it works**: Toggle input flips state; reset input forces a known state
- **Important notes**: Useful when you need both toggle and force-reset capability

#### Repeater-Latched T Flip-Flop — Design L3
- **Dimensions**: 3x4x2
- **Materials**: 2 redstone torches, 2 redstone dust, 3 repeaters
- **Build**: Uses repeater latching mechanic for the toggle
- **How it works**: Repeater locks capture the toggled state. High-level triggered
- **Important notes**: Responds to stone button but not wooden button (oscillates if held too long)

#### Repeater-Latched T Flip-Flop — Design L4
- **Dimensions**: 2x3x1
- **Materials**: 2 redstone dust, 3 repeaters (no torches)
- **Build**: Designed for off-pulses. Customizable 2-8 redstone tick durations via top repeater
- **How it works**: Falling edge triggered. Repeater delay settings control accepted pulse width
- **Important notes**: Adjust top repeater per the trigger duration table. Most compact repeater-based TFF

#### Classic Torch T Flip-Flop — Design A
- **Dimensions**: 7x9x3
- **Materials**: 10 redstone torches, 28 redstone dust
- **Build**: All torches and dust, no repeaters or pistons. The original T flip-flop design
- **How it works**: Cross-coupled NOR gates with feedback paths create a toggle on each rising edge. 4-tick delay
- **Important notes**: Large footprint. Historical reference design

---

### D Latches and D Flip-Flops

Data (D) input is captured when the clock signal is active.

#### Modern Gated D Latch — Design G
- **Dimensions**: 2x1x2
- **Materials**: 2 repeaters (no torches, no dust)
- **Build**: Two repeaters arranged so one locks the other. Clock input controls the locking repeater
- **How it works**: When clock is HIGH, the data repeater is unlocked and passes the D input through. When clock goes LOW, the repeater locks, holding its last value
- **Important notes**: Most compact D latch possible. Introduced in Java 1.4.2 with repeater locking mechanic

#### Modern D Flip-Flop — Design H
- **Dimensions**: 3x2x2
- **Materials**: 4 repeaters, 1 redstone torch (no dust)
- **Build**: Master-slave configuration using two gated D latches. Rising edge triggered
- **How it works**: Master latch captures D when clock is LOW; slave latch transfers to output when clock goes HIGH. Data is captured only at the rising edge
- **Important notes**: Block/torch can be reversed for falling edge variant. True edge-triggered behavior

#### Analog D Latch — Design J
- **Dimensions**: 6x4x2
- **Materials**: Comparators, repeaters, dust
- **Build**: Low level-triggered analog latch
- **How it works**: Signal strength of output Q matches the signal strength of input D when triggered. For maximum strength (15) signals, behaves identically to a digital latch
- **Important notes**: Preserves analog signal strength. 3-tick circuit delay

#### Vertical Torch D Latch — Design C
- **Dimensions**: 6x1x5
- **Materials**: 5 redstone torches, 5 redstone dust
- **Build**: One-block-wide vertical design. Sets output to D while clock is ON
- **How it works**: Torch ladder with gating logic. High level-triggered
- **Important notes**: Repeatable in parallel for multi-bit data storage

---

### JK Flip-Flops

J input sets, K input resets, both inputs together toggle. The "universal" flip-flop.

#### JK Flip-Flop — Design A (Edge-Triggered)
- **Dimensions**: 9x2x11
- **Materials**: 12 redstone torches, 30 redstone dust
- **Build**: Full torch-and-dust implementation with rising edge trigger
- **How it works**: J=1,K=0 sets output ON. J=0,K=1 sets output OFF. J=1,K=1 toggles. J=0,K=0 holds state. Triggered on rising clock edge
- **Important notes**: No inverse output accessible. Large footprint

#### JK Latch — Design C (Level-Triggered)
- **Dimensions**: 7x4x5
- **Materials**: 11 redstone torches, 23 redstone dust
- **Build**: Level-triggered variant with accessible inverse output
- **How it works**: Same J/K logic but responds to clock level rather than edge
- **Important notes**: Race condition when J and K are both HIGH — output oscillates while clock is active

#### JK Flip-Flop — Design D (Compact Edge-Triggered)
- **Dimensions**: 5x2x7
- **Materials**: 8 redstone torches, 16 redstone dust, 6 repeaters
- **Build**: More compact edge-triggered design using repeaters for timing
- **How it works**: Rising edge triggered with accessible inverse output
- **Important notes**: Uses repeaters for proper edge detection, avoiding race conditions

---

### Counters

Hold more than two states, cycling through them with each input pulse.

#### Analog Counter (Comparator-Based)
- **Dimensions**: Varies
- **Materials**: Comparators, redstone dust
- **Inputs**: Increment (I), Decrement (D), Set (S)
- **Output**: Q (analog signal strength 0-15)
- **Build**: Uses analog RS latch property of comparators
- **How it works**: While Increment is active, signal strength increases by 1 every two ticks until maximum (15). While Decrement is active, signal strength decreases until 0. Highest signal strength at output Q is memorized
- **Important notes**: 16 states (0-15) in a single circuit. Useful for analog control systems

#### Binary Counter (Stacked Dividers)
- **Dimensions**: 3x5x(2n) for n-bit counter
- **Materials**: Repeaters, redstone torches, solid blocks (per stage)
- **Build**: Stack inverted binary divider modules. Each module is one bit of the counter
- **How it works**: Each stage toggles on each pulse from the previous stage, creating a binary count
- **Important notes**: n-bit counter counts from 0 to 2^n - 1. Infinitely stackable

---

## Advanced Circuits

Complex circuits for specialized applications.

### Binary to 1-of-8 Converter (3-bit Decoder)
- **Dimensions**: Largest unit 5x5x3
- **Materials**: Redstone torches (1-4 per output), redstone dust (7-10 per output)
- **Build**: Series of logic gates where each output activates only for its corresponding binary value. Place diodes before each input to prevent signal feedback
- **How it works**: Each of the 8 outputs uses AND/NAND combinations of the 3 input bits. Output 0 requires all inputs OFF; Output 7 requires all inputs ON
- **Important notes**: Diodes between inputs are mandatory to prevent feedback. Expandable principle

### Binary to 1-of-16 Converter (4-bit Decoder)
- **Dimensions**: Largest unit 3x5x2
- **Materials**: Redstone torches (1-5 per output), 2 redstone dust per output
- **Build**: Same principle as 1-of-8 but with 4 input bits and 16 outputs
- **How it works**: Each of 16 outputs uses AND/NAND combinations of 4 input bits
- **Important notes**: Can be truncated to 1-of-10 for decimal applications

### 1-of-16 to Binary Converter (4-bit Encoder)
- **Dimensions**: Varies
- **Materials**: Four 8-input OR gates
- **Build**: Each OR gate combines the input lines where a specific bit position contains '1'. Isolating OR gates prevent signal feedback
- **How it works**: Reverse of the decoder. Each of 4 output bits is the OR of the 8 input lines that should produce a '1' in that bit position
- **Important notes**: Requires signal isolation on all OR inputs

### Piston Mask Demultiplexer
- **Dimensions**: Varies (3-bit input to 8 outputs)
- **Materials**: Pistons with slime blocks, solid blocks
- **Build**: Three layers of "punch card" masks move via pistons. Signals propagate only when all three mask layers align correctly
- **How it works**: Each bit controls a mask layer. A signal passes through only when the combination of mask positions creates an unblocked path for that specific output. Uses the principle: Output 0 = NOT(bit2) AND NOT(bit1) AND NOT(bit0)
- **Important notes**: Reversible design can function as a multiplexer. Physical "punch card" approach is visually intuitive

### Timer Circuit
- **Dimensions**: Varies (chain of locked repeaters)
- **Materials**: Locked repeaters, redstone dust, redstone torch
- **Build**: First signal travels through a chain of locked repeaters. Second signal unlocks them. Count powered repeaters to read elapsed time
- **How it works**: First event starts a signal traveling through locked repeaters at 1 repeater per tick. Second event unlocks the chain, freezing the signal position. If 5 repeaters are powered, 0.4-0.5 seconds elapsed
- **Important notes**: Data preserved between uses. Must obstruct circuit (mine a torch) between measurements to reset. Repeater delay must be set to 2 ticks for duration measurement
- **Variants**: Duration timer (measures how long a signal lasts), signal replenishment section for high-scale measurements

### Sorting Device
- **Dimensions**: 5x5 tileable center (expandable)
- **Materials**: Logic gates, redstone dust
- **Build**: Bottom and right sides are inputs; top and left sides are outputs. Sorts binary inputs, placing 1s at bottom and 0s at top
- **How it works**: Counts the number of HIGH inputs and arranges outputs so all HIGHs are contiguous at one end
- **Important notes**: Tileable and expandable for any input count

### 3-Digit Hexadecimal Combination Lock
- **Dimensions**: Large (multiple subsystems)
- **Materials**: OR gates, XNOR gates, RS NOR latches, repeaters, binary converters
- **Build**: Uses 4-bit binary input for hexadecimal digits. Comparison logic checks each digit sequentially. Wrong digit triggers reset
- **How it works**: Player enters digits via 1-of-16 input (buttons). Circuit converts to binary, compares against stored code using XNOR gates. All digits correct = unlock. Wrong digit = reset
- **Important notes**: Code is changeable without circuit modification. Expandable by copying comparison circuits. Can disable digits by setting code to 0000. For n-digit key with m-bit input: m^(2^n) possible combinations

### D Flip-Flop Serial Interface Lock
- **Dimensions**: Varies
- **Materials**: RS NOR latches, D flip-flops, hidden programming levers
- **Build**: D flip-flops shift values left-to-right on clock pulses. Hidden levers set the code. Player toggles D input and clock lever to enter code
- **How it works**: Each clock pulse shifts the current D value into the chain. After entering all bits, the chain contents are compared against the hidden code
- **Input sequence example** (for code 1-0-1-0): D=1 then toggle C twice, D=0 then toggle C twice, D=1 then toggle C twice, D=0 then toggle C twice (12 lever toggles total for 4-bit code)
- **Important notes**: Not very practical as a security lock (slow input), but excellent for puzzle/challenge maps

---

## Quick Reference: Recommended Builds by Use Case

| Use Case | Recommended Circuit | Key Advantage |
|----------|-------------------|---------------|
| Simple fast clock | Single Observer 4gt Clock | 1 observer + dust, toggleable |
| Adjustable clock | 8-20gt Subtraction Clock | Change repeater for different speeds |
| Very long timer | Multiplicative Hopper-Dropper Clock | Hours to days of delay |
| Button to toggle | Copper Bulb T Flip-Flop | 2 blocks total |
| Button to toggle (pre-1.21) | Hopper/Dropper TFF Variant A | 1x2x3, tileable |
| Set/Reset memory | Piston RS Latch Design N | 4x1x1, no dust needed |
| Short pulse from long input | NOR-Gate Pulse Limiter | 1-wide, silent |
| Extend a short pulse | Dropper-Latch Extender | 5 ticks to 256 seconds |
| Detect signal turning on | Dust-Cut RED | Instant (0-tick) response |
| Detect signal turning off | Moved-Observer FED | 6 blocks, 1-wide |
| Detect both edges | Observer (single block) | Built-in dual edge detection |
| Store data bit | Modern Gated D Latch | 2x1x2, just 2 repeaters |
| Count pulses (binary) | Stacked Binary Dividers | Infinitely extensible |
| Count pulses (analog 0-15) | Analog Counter | 16 states, single circuit |
| Decode binary address | Binary to 1-of-16 Converter | Clean 4-bit decoding |
| Security/combination lock | Hex Combination Lock | Changeable code, expandable |

---

## Edition Compatibility Notes

Many circuits behave differently between Java and Bedrock editions:

- **Java-only circuits**: 0-tick piston clocks, 2gt repeater loop, quasi-connectivity designs, 1-tick binary counter, sticky piston "spitting" behavior
- **Bedrock timing differences**: Observer pulses are 2gt longer, hopper clocks have different periods, some piston behaviors differ
- **Cross-edition safe**: Comparator clocks, torch clocks, hopper clocks (with adjusted timing), repeater-based memory circuits, dropper-based flip-flops

Always test critical timing circuits in your target edition.
