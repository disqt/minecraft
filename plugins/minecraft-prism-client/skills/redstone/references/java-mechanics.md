# Java Edition Redstone Mechanics Reference

Comprehensive reference for Minecraft Java Edition redstone mechanics. Sourced from the Minecraft Wiki (minecraft.wiki) and verified against in-game behavior as of 1.21.x.

---

## 1. Signal Strength

Redstone signals operate on an integer scale from **0 to 15**.

- **0** = unpowered (no signal)
- **1-15** = powered (signal present, strength determines dust transmission range)

### How signal strength propagates

| Component | Output strength |
|-----------|----------------|
| Most power sources (lever, button, torch, redstone block) | 15 |
| Weighted pressure plates | 1-15 (proportional to entity count) |
| Target block | 1-15 (depends on projectile hit location) |
| Daylight detector | 1-15 (depends on time of day) |
| Comparator | Variable (depends on mode and inputs) |
| Sculk sensor | 1-15 (depends on vibration distance) |

### Dust attenuation

Redstone dust loses **1 signal strength per block** it travels. A signal entering dust at strength 15 reaches 0 after 15 blocks.

```
Source [15] -> Dust [14] -> Dust [13] -> ... -> Dust [1] -> Dust [0, dead]
```

Signal strength does **not** decrease when transmitted from dust to a solid block, or from dust to a redstone component (repeater, comparator, mechanism). The attenuation only occurs block-to-block within dust itself.

### Repeaters reset signal to 15

A repeater accepts **any** nonzero input signal and outputs **15**, regardless of the input strength. This is why repeaters are called "signal boosters" -- they restore full strength.

### Comparators preserve signal strength

In **compare mode** (default), a comparator outputs the rear input strength unchanged (if rear >= both side inputs). In **subtract mode**, it outputs `rear - max(sides)`, minimum 0.

---

## 2. Tick Timing

### Fundamental units

| Unit | Duration | Relationship |
|------|----------|-------------|
| 1 game tick (GT) | 0.05 seconds (50 ms) | Base unit; 20 per second |
| 1 redstone tick (RT) | 0.1 seconds (100 ms) | = 2 game ticks |

The game runs at **20 game ticks per second** (20 TPS). If the server cannot keep up, TPS drops and everything slows proportionally.

"Redstone tick" is a community term. The game code uses game ticks internally. When redstone players say "1 tick," they almost always mean 1 redstone tick (2 game ticks).

### Component timing

| Component | Delay | Notes |
|-----------|-------|-------|
| Redstone dust | 0 ticks | Instantaneous (within the same game tick) |
| Redstone torch | 1 RT (2 GT) | Time to toggle on/off |
| Redstone repeater | 1-4 RT (2-8 GT) | Configurable with right-click |
| Redstone comparator | 1 RT (2 GT) | Fixed delay |
| Observer | 1 RT (2 GT) | Delay before outputting pulse |
| Piston (extend) | 0 GT start + 2 GT to finish | Begins extending immediately, takes 2 GT to complete |
| Piston (retract) | 0 GT start + 2 GT to finish | Same as extension |

### Tick processing order within a game tick

Java Edition processes each game tick in this order:

1. **Scheduled tick execution** -- block ticks and fluid ticks fire (redstone repeaters, comparators, torches change state here)
2. **Block events** -- pistons extend/retract here
3. **Entity processing** -- mobs, items, players
4. **Block entity processing** -- hoppers, furnaces, etc.
5. **Chunk and world management**

This ordering matters because components processed earlier in the tick "see" the old state of components processed later, and vice versa. This is why certain circuits behave directionally or locationally.

### Scheduled tick priorities (Java-specific)

When multiple scheduled ticks fire on the same game tick, they execute by priority (lower number = earlier):

| Priority | Component |
|----------|-----------|
| -3 | Repeater facing into another repeater or comparator |
| -2 | Repeater turning off |
| -1 | Repeater (standard) |
| -1 | Comparator facing into another repeater or comparator |
| 0 | All other blocks (default) |

Ties within the same priority are broken by scheduling order (first scheduled = first executed).

---

## 3. Update Order

This is the single most confusing aspect of Java Edition redstone. There are three types of updates:

### Block updates (neighbor updates)

When a block changes state, it notifies its 6 immediate neighbors. Those neighbors then check whether they need to respond (e.g., a torch checks if it should toggle, dust checks if its power changed).

Some components also update the neighbors of the block they are attached to ("neighbors of neighbors"), effectively reaching blocks 2 taxicab-distance away.

### Shape updates

A newer system. When a block changes, it sends shape updates to its 6 neighbors. Observers detect shape updates (not block updates). Redstone dust uses shape updates for its connection changes.

### Scheduled ticks

Components like repeaters, comparators, and torches do not change state instantly upon receiving an update. Instead, they **schedule a tick** for a future game tick. When that tick arrives, the component changes state and sends block updates to its neighbors.

### Why update order causes confusion

When redstone dust changes power level, it sends block updates to all affected neighbors. The **order** in which these updates are sent depends on the **direction** the dust is oriented and the **position** of the dust in the world. This means:

- The same circuit can behave differently depending on which direction it faces (north/south vs east/west).
- Circuits that work in one location may break when moved or rotated.
- This is called **"locational" or "directional" behavior** and is a known Java quirk.

The internal update order for dust in Java Edition follows a fixed priority: west, east, north, south (for cardinal neighbors), then up, down. But because dust must also update the blocks that its signal passes through, the effective order becomes complex and direction-dependent.

### Key rule for beginners

If your circuit works facing one direction but not another, the cause is almost certainly update order. Solutions:
- Add a repeater to isolate the timing
- Redesign to avoid depending on simultaneous dust updates
- Test in all four orientations

---

## 4. Quasi-Connectivity (QC / BUD Behavior)

**Java Edition only.** This does not exist in Bedrock Edition.

### Definition

Quasi-connectivity means that **pistons, dispensers, and droppers** can be activated by anything that would power the block space directly above them, even if that space is empty or contains a non-conducting block.

### Why it exists

The mechanic originates from how doors work. A door occupies two blocks (top and bottom). Powering the top half activates the bottom half too. The game engine applies this same "check the space above" logic to pistons, dispensers, and droppers -- but unlike doors, these are single-block components. The result is that they respond to power sources that are seemingly not connected to them.

### What is affected

| Component | QC applies? |
|-----------|-------------|
| Pistons (regular and sticky) | Yes |
| Dispensers | Yes |
| Droppers | Yes |
| Crafters | No (explicitly excluded) |
| Note blocks | No |
| Doors, trapdoors, fence gates | No (they have their own 2-block logic) |
| Redstone lamps, hoppers | No |

### How it works mechanically

A piston checks for power in two ways:
1. **Normal check**: Is any of my 6 neighbors providing power to me?
2. **QC check**: Would any block provide power to the space one block above me?

If either check succeeds, the piston activates.

### The Update Problem

QC activation requires two things:
1. The power condition must be met (something powers the space above)
2. The piston must receive a **block update** to notice it

Many QC setups satisfy condition 1 but not condition 2. The piston is "quasi-powered" but does not know it yet. It will only activate when something else causes a block update nearby (placing/breaking a block, changing adjacent redstone, etc.). This is the basis of **BUD switches** (Block Update Detectors).

### Classic example

```
     [Redstone Dust]    <-- powers the block below it
     [Solid Block]      <-- this block is powered
     [AIR]              <-- this space WOULD be powered (by the block above)
     [Piston]           <-- QC: activates because the space above it would be powered
```

The piston fires even though no power source is directly adjacent to it.

### Common beginner problem

Running redstone dust over a block directly above a piston will activate the piston via QC, even though the player only intended the dust to pass through. This is the number one surprise for beginners working with pistons.

### Workarounds

1. **Use slabs**: Place a top slab above the piston, then run dust on top of that slab. The extra elevation breaks the QC connection.
2. **Use transparent blocks**: Glass, glowstone, and other transparent blocks cannot be powered, so they prevent QC.
3. **Route around**: Run your redstone wire around the piston rather than over it.
4. **Add repeaters**: Repeaters between the signal and the piston area can isolate the QC path (but add delay).

---

## 5. Repeater Mechanics

### Core behaviors

A redstone repeater has four functions:

1. **Signal repeating**: Accepts any nonzero input, outputs 15
2. **Delay**: Adds 1-4 redstone ticks (2-8 game ticks) of delay
3. **Diode**: Signals pass through in one direction only (back to front)
4. **Locking**: Can be locked by a powered repeater or comparator facing its side

### Delay settings

Right-clicking cycles through 4 delay settings:

| Setting | Delay (RT) | Delay (GT) | Delay (seconds) |
|---------|-----------|-----------|-----------------|
| 1 (default) | 1 | 2 | 0.1 |
| 2 | 2 | 4 | 0.2 |
| 3 | 3 | 6 | 0.3 |
| 4 | 4 | 8 | 0.4 |

### Locking

When another powered repeater or comparator faces into the side of a repeater, it becomes **locked**:
- The locked repeater freezes its current output state (on or off)
- Changes to the rear input are ignored while locked
- The visual indicator is a bedrock-colored bar across the top
- Unlocking happens instantly when the side power is removed

Locking is useful for memory circuits, multiplexers, and data storage.

### Pulse behavior

- A repeater set to 1 tick extends any incoming 0-tick or 1-tick pulse to match its delay (2 GT minimum output)
- A repeater set to 4 ticks extends short on-pulses to 4 RT and suppresses off-pulses shorter than 4 RT
- Only one scheduled tick can exist per repeater at a time; a second attempt is silently dropped

### What repeaters power

A powered repeater **strongly powers** the opaque block in front of it. This means:
- Dust on or adjacent to that block will be powered
- Mechanism components adjacent to that block will activate

---

## 6. Comparator Mechanics

### Two modes

Toggle between modes by right-clicking. The front torch indicates the mode:
- **Front torch OFF (down)** = Compare mode
- **Front torch ON (up)** = Subtract mode

### Compare mode

```
If rear >= max(left, right):
    output = rear
Else:
    output = 0
```

The comparator passes the rear signal through unchanged as long as neither side input exceeds it. If any side input is stronger, output shuts off entirely.

### Subtract mode

```
output = max(rear - max(left, right), 0)
```

The stronger side input is subtracted from the rear input. Output is never negative (floors at 0).

### Examples

| Mode | Rear | Left | Right | Output |
|------|------|------|-------|--------|
| Compare | 10 | 5 | 3 | 10 |
| Compare | 10 | 12 | 3 | 0 |
| Compare | 10 | 5 | 10 | 10 |
| Compare | 10 | 5 | 11 | 0 |
| Subtract | 10 | 5 | 3 | 5 |
| Subtract | 10 | 12 | 3 | 0 |
| Subtract | 15 | 7 | 4 | 8 |

### Reading containers

A comparator can read the contents of a container placed behind it (or behind a solid block behind it). The output signal strength reflects how full the container is.

#### Container signal strength formula

```
signal = floor(1 + (total_fullness / number_of_slots) * 14)
```

Where `total_fullness` is the sum of each slot's fullness:

```
slot_fullness = items_in_slot / max_stack_size_for_that_item
```

- Items that stack to 64: each item contributes 1/64
- Items that stack to 16 (snowballs, ender pearls): each item contributes 1/16 (equivalent to 4 of a 64-stackable)
- Unstackable items (tools, potions): each contributes 1/1 (equivalent to 64 of a 64-stackable)

**Empty container** = signal 0
**At least 1 item** = signal 1 minimum
**Completely full** = signal 15

#### Readable blocks (partial list)

| Block | Signal behavior |
|-------|----------------|
| Chest, barrel, shulker box, hopper | Fullness formula above |
| Double chest | Uses combined 54 slots |
| Furnace, blast furnace, smoker | 3 slots (input, fuel, output) |
| Brewing stand | 5 slots (3 potions, ingredient, blaze powder) |
| Dispenser, dropper | 9 slots |
| Lectern | `floor(1 + ((page - 1) / (total_pages - 1)) * 14)` |
| Cake | 2 per remaining slice (7 slices = 14 max) |
| Cauldron (water) | 0 (empty), 1 (1/3), 2 (2/3), 3 (full) |
| Cauldron (lava) | Always 3 |
| Composter | 0-8 (matches fill level) |
| Jukebox | 1-15 (varies by disc; 0 when empty) |
| Beehive/bee nest | 0-5 (honey level) |
| Chiseled bookshelf | Depends on which slots have books |
| Respawn anchor | 0-4 (charge level) |
| Item frame | 1-8 (0 empty, 1 item present, 2-8 based on rotation) |
| End portal frame | 0 (no eye), 15 (eye inserted) |

### Comparator timing

Comparators have a fixed delay of **1 redstone tick (2 game ticks)**. They cannot be adjusted.

### Reading through blocks

A comparator can read a container that is separated from it by one opaque block. The comparator reaches "through" the block to detect the container.

---

## 7. Piston Mechanics

### Push and pull limits

- Maximum push: **12 blocks**
- Maximum pull (sticky piston): **12 blocks** (but only the one block directly in front is "grabbed"; slime/honey blocks can chain more)
- Mojang has confirmed the 12-block limit is intentional and will not be changed

### Immovable blocks (cannot be pushed or pulled)

Obsidian, bedrock, barrier, reinforced deepslate, end portal, end portal frame, end gateway, nether portal, command block, structure block, jigsaw block, spawner, enchanting table, respawn anchor, crying obsidian, lodestone, moving piston (the B36 block during piston movement), extended piston head.

### Blocks that break when pushed

Torches, redstone torches, levers, buttons, rails (all types), carpets, pressure plates, tripwire, banners, signs, lanterns, candles, bells, flowers, mushrooms, saplings, vines, cave vines, glow lichen, coral, cactus, cake, beds, amethyst clusters, pointed dripstone, heads/skulls (wall-mounted), most small plant blocks.

### Container blocks

In Java Edition, most container blocks (chests, furnaces, dispensers, droppers, hoppers, barrels, brewing stands, etc.) **cannot be pushed by pistons**. This is a significant difference from Bedrock Edition, where many containers are movable.

### Timing

- Extension: **2 game ticks (1 RT)** to complete
- Retraction: **2 game ticks (1 RT)** to complete
- A piston begins responding within 0-1 game ticks of being powered, depending on the tick phase

### Slime blocks and honey blocks

When a piston pushes or pulls a slime block, all blocks attached to it (by adjacency) move together as a group, up to the 12-block limit. The same applies to honey blocks.

**Critical rule**: Slime blocks and honey blocks **do not stick to each other**. This allows building independent groups side-by-side.

**Glazed terracotta** does not stick to slime or honey blocks but can be pushed normally. This is useful for creating gaps in movable structures.

### 0-tick pistons (Java Edition)

A 0-tick piston event occurs when a piston receives a power signal and then loses it within the same game tick (0 ticks of being powered). In Java Edition:

- The piston extends and retracts within the same game tick
- Blocks moved by the piston during a 0-tick event experience unique behavior: crops and other growable blocks may advance their growth stage
- 0-tick farms exploit this mechanic for high-speed harvesting
- This is a Java-exclusive behavior that does not exist in Bedrock

### Quasi-connectivity

See Section 4 above. Pistons are the component most commonly affected by QC, because players frequently run redstone lines above pistons.

---

## 8. Observer Mechanics

### What observers detect

In Java Edition, observers detect **shape updates** (also called "block shape changes") in the single block they face. This includes:

- Block placement or removal
- Block state changes (door opening, lever toggling, crop growing, repeater delay changing, note block pitch changing)
- Fluid placement or removal
- Redstone component state changes
- Comparator or repeater locking/unlocking
- Shulker box opening/closing
- Jukebox disc insertion/removal

Observers do **not** detect:
- Entity changes (mobs moving, items landing)
- Light level changes
- Block updates that do not change the block state

### Pulse output

When triggered, an observer emits a **1 redstone tick (2 game tick) pulse** at **signal strength 15** from its back face (the face with the red dot).

There is a **1 redstone tick delay** between detecting the change and emitting the pulse.

### Facing and orientation

- The **observing face** (the one with the "face" texture) points toward the player when placed
- The **output face** (the red dot) is on the opposite side
- Observers can face all 6 directions (up, down, north, south, east, west)

### Observer chains and clocks

Two observers facing each other create a **2-tick clock** (each observer detects the other's state change, creating a perpetual loop). This is one of the simplest and most compact clocks in the game.

### Java vs Bedrock difference

When moved by a piston while emitting a signal, a Java Edition observer **turns off**. In Bedrock Edition, it continues emitting. This affects flying machine designs.

### Redstone properties

- Observers are **non-conductive** (they do not transmit power through themselves)
- They do not cut redstone wire connections
- They cannot be powered by external redstone to suppress detection

---

## 9. Soft Power vs Hard Power (Weak vs Strong)

This distinction is one of the most important concepts in Java Edition redstone and one of the least intuitive.

### Definitions

**Strong power** (hard power): A strongly powered block can:
- Activate adjacent mechanism components (pistons, lamps, etc.)
- Power adjacent redstone dust
- Power repeaters and comparators facing away from it

**Weak power** (soft power): A weakly powered block can:
- Activate adjacent mechanism components (pistons, lamps, etc.)
- Power repeaters and comparators facing away from it
- **CANNOT** power adjacent redstone dust

### What provides strong vs weak power to blocks

| Source | Power type to adjacent block |
|--------|------------------------------|
| Repeater (output into block) | Strong |
| Comparator (output into block) | Strong |
| Redstone torch (block above it) | Strong |
| Button, lever, pressure plate (attachment block) | Strong |
| Trapped chest, tripwire hook, detector rail | Strong |
| Redstone dust (block it sits on or points at) | **Weak** |

### The practical consequence

This is the key scenario beginners encounter:

```
[Lever ON] -> [Block A] -> [Dust on Block A] -> [Block B] -> [Dust on Block B]???
```

- The lever **strongly powers** Block A
- Dust on/adjacent to Block A receives power (because Block A is strongly powered)
- That dust **weakly powers** Block B
- Dust adjacent to Block B gets **nothing** (because Block B is only weakly powered -- weak power cannot activate dust)

To continue the signal through Block B, you need a **repeater** pointing into Block B. The repeater will strongly power it.

### Transparent (non-conductive) blocks

Transparent blocks like glass, slabs, stairs, glowstone, sea lanterns, and leaves **cannot be powered at all** (neither strongly nor weakly). Redstone signals cannot pass through them into a block.

However, redstone components can be placed on some transparent blocks and will function normally -- they just will not power the transparent block itself.

### Opaque (conductive) blocks

Opaque blocks like stone, dirt, wood planks, concrete, and wool can be powered. When powered, they can activate adjacent mechanisms and (if strongly powered) can power adjacent dust.

---

## 10. Common Beginner Mistakes

### Mistake 1: Not understanding signal strength attenuation

**What happens**: A player runs dust 20 blocks and wonders why the signal dies.

**The rule**: Dust loses 1 strength per block. Maximum range is 15 blocks. Place a repeater every 15 blocks (or fewer) to maintain the signal.

**Tip**: The brightness of the dust visually indicates its signal strength. Dark red = weak signal about to die.

### Mistake 2: Confusing weak and strong power

**What happens**: A player powers a block with dust, then expects dust on the other side to receive power. It does not.

**The rule**: Dust only weakly powers blocks. Weakly powered blocks cannot power other dust. Use a repeater to convert weak power to strong power.

**Diagnostic**: Place a redstone lamp next to the block -- if it lights up, the block IS powered (even weakly). Then check if the problem is that you need strong power for dust.

### Mistake 3: Quasi-connectivity surprises

**What happens**: A piston activates "for no reason" when redstone is run above it.

**The rule**: Pistons, dispensers, and droppers in Java Edition respond to power sources that would power the space above them. Running redstone over a block above a piston will activate it via QC.

**Fix**: Use transparent blocks (glass), add vertical spacing (slabs), or route wiring around the piston.

### Mistake 4: Not accounting for repeater/torch delay

**What happens**: A player builds a circuit that requires two things to happen simultaneously, but one path has more repeaters/torches than the other, so the signals arrive at different times.

**The rule**: Every repeater adds 1-4 RT delay. Every torch adds 1 RT delay. Count the total delay on each signal path and ensure they match when synchronization matters.

**Tip**: Comparators also add 1 RT of delay. Dust adds 0 delay.

### Mistake 5: Redstone torch burnout

**What happens**: A torch rapidly toggles on and off, then stops working entirely.

**The rule**: A redstone torch burns out if forced to toggle more than **8 times in 60 game ticks (3 seconds)**. It recovers when it receives a block update after the rapid toggling stops.

**Common cause**: Accidental feedback loops where a torch powers dust that powers the block the torch is attached to, creating an oscillating loop that burns out.

### Mistake 6: Building circuits that are direction-dependent

**What happens**: A circuit works perfectly, but when the player rebuilds it facing a different direction, it breaks.

**The rule**: Due to Java Edition's internal update order for dust (processing neighbors in a fixed cardinal order), some circuits behave differently depending on orientation. This is especially common with circuits that rely on simultaneous dust updates.

**Fix**: Test your circuit in all four orientations. If it fails in some, add repeaters to make the timing explicit rather than relying on update order.

### Mistake 7: Forgetting that pistons cannot push containers

**What happens (Java Edition)**: A player tries to push a chest or furnace with a piston and it does not move.

**The rule**: In Java Edition, most container blocks (chests, furnaces, dispensers, droppers, hoppers, barrels, etc.) cannot be pushed by pistons. This is different from Bedrock Edition.

### Mistake 8: Not understanding opaque vs transparent blocks

**What happens**: A player uses glass or a slab as a building block in their circuit, then wonders why redstone signals do not pass through it.

**The rule**: Transparent blocks (glass, slabs, stairs, leaves, glowstone) cannot be powered. Redstone signals cannot travel through them. Use opaque blocks (stone, dirt, wood planks) for any block that needs to carry a redstone signal.

**Exception**: Redstone dust can transmit diagonally upward through a transparent block (dust goes up a step when the upper block is transparent), but not diagonally downward.

### Mistake 9: Placing TNT before the circuit is complete

**What happens**: Circuits under construction can briefly power up during building, detonating any TNT already placed.

**The rule**: Always finish and test your redstone circuit fully before placing TNT or other destructive mechanism components.

### Mistake 10: Ignoring 1-tick pulse behavior

**What happens**: A button press works, but a observer pulse (1 RT) is too short to activate the circuit reliably.

**The rule**: Some components produce very short pulses (observers: 1 RT). Many mechanisms need longer pulses to function. Use a **pulse extender** (repeater chain or RS latch) to lengthen short pulses, or a **pulse limiter** (torch-based) to shorten long ones.

---

## Quick Reference Card

### Power source strengths

| Source | Strength | Duration |
|--------|----------|----------|
| Lever | 15 | Toggle (stays until flipped) |
| Button (stone) | 15 | 10 RT (1 second) |
| Button (wood) | 15 | 15 RT (1.5 seconds) |
| Pressure plate (stone) | 15 | While stepped on + 10 RT |
| Pressure plate (wood) | 15 | While stepped on + 15 RT |
| Redstone torch | 15 | Continuous (until block is powered) |
| Redstone block | 15 | Continuous (always) |
| Observer | 15 | 1 RT pulse |
| Daylight detector | 1-15 | Varies with sun position |
| Tripwire hook | 15 | While tripwire is crossed |
| Trapped chest | 1-15 | While open (strength = player count) |
| Detector rail | 15 | While minecart is on it |
| Lightning rod | 15 | 8 RT after lightning strike |

### Delay cheat sheet

| Component | Delay |
|-----------|-------|
| Dust | 0 (instant) |
| Repeater | 1-4 RT (configurable) |
| Comparator | 1 RT (fixed) |
| Torch | 1 RT (fixed) |
| Observer | 1 RT (detect-to-output delay) |
| Piston | 0 GT to start, 2 GT to complete |

### Blocks that CANNOT be pushed by pistons (Java Edition)

Obsidian, bedrock, barrier, reinforced deepslate, end portal (frame), nether portal, command block, structure block, jigsaw block, spawner, enchanting table, respawn anchor, crying obsidian, lodestone, anvil, grindstone, beacon, chest, trapped chest, furnace (all types), dispenser, dropper, hopper, barrel, brewing stand, ender chest, jukebox, shulker box (when extended piston is in the way).

### Container signal strengths (comparator output)

**Formula**: `floor(1 + (total_fullness / slots) * 14)` where `slot_fullness = count / max_stack`.

| Container | Slots | Items for signal 1 | Items for signal 15 |
|-----------|-------|--------------------|--------------------|
| Chest | 27 | 1 | 27 * 64 = 1728 |
| Double chest | 54 | 1 | 54 * 64 = 3456 |
| Hopper | 5 | 1 | 5 * 64 = 320 |
| Dropper/Dispenser | 9 | 1 | 9 * 64 = 576 |
| Furnace | 3 | 1 | Depends on slot types |
| Barrel | 27 | 1 | 27 * 64 = 1728 |
| Shulker box | 27 | 1 | 27 * 64 = 1728 |
