# Redstone Tutorials - Batch 1
## Scraped from Minecraft Wiki Tutorial Pages
### Date: 2026-03-10

---

# Page 1: Mechanisms (Tutorial:Mechanisms)

## Utility Mechanisms

### Potion Dispenser
- **Dimensions:** Compact (roughly 1x1x2)
- **Materials:** 1 dispenser, 1 fence, pressure plates, splash potions
- **Build steps:**
  1. Place dispenser one block above floor level
  2. Position fence on the dispenser's output side
  3. Place pressure plates on top of fence
  4. Load dispenser with splash potions
- **How it works:** Pressure plate activation triggers the dispenser to fire splash potions outward through the fence opening. Entities walking over the fence receive the potion effect.
- **Notes:** Good for automated healing stations or trap defenses.

### Rapid Pit Bomber
- **Dimensions:** Variable (depends on rail length)
- **Materials:** 1 dispenser, redstone clock circuit, 1 hopper, powered rail, 1 block of redstone, minecarts with TNT, 1 chest
- **Build steps:**
  1. Build a redstone clock and attach it to a dispenser
  2. Connect a hopper feeding into the dispenser
  3. Place a powered rail on top of a block of redstone
  4. Place a chest above the hopper and fill with TNT minecarts
  5. Position the dispenser to launch carts onto the powered rail
- **How it works:** The clock rapidly pulses the dispenser, which launches TNT minecarts down the powered rail track for rapid-fire explosive mining.
- **Notes:** Effective for strip-mining or clearing large areas. Consumes minecarts with TNT quickly.

---

## Hidden Entrances

### Hidden Floor Staircase
- **Dimensions:** Width of staircase x depth of staircase x (stair count + 2)
- **Materials:** Sticky pistons (1 per step, increasing extender complexity), redstone torches, building blocks
- **Build steps:**
  1. Below the first floor block, place a face-up sticky piston powered in the OFF state (via redstone torch providing inverted signal)
  2. Below the next floor block, build a double-piston extender, also powered when OFF
  3. Continue with triple-piston extender for the third step, and so on
  4. Each successive step requires one more piston in its extender stack
- **How it works:** Sticky pistons powered by redstone torches (inverted logic) hold floor blocks in place normally. When activated, the torches turn off and pistons retract, pulling blocks downward sequentially to reveal descending stairs.
- **Notes:** Complexity scales with stair count. Each additional step needs a more complex piston extender.

### Hidden Chest/Store Room
- **Dimensions:** Room size + piston mechanism depth (typically 3-4 blocks behind wall)
- **Materials:** Sticky pistons, lever, building blocks matching wall
- **Build steps:**
  1. Build a room behind a wall containing chests, furnaces, crafting tables
  2. Use sticky pistons to move wall blocks aside when activated
  3. Wire to a lever on the visible side
  4. Remove lever when leaving to present a bare wall
- **How it works:** Sticky pistons retract wall blocks to reveal the hidden room. Removing the lever makes it undetectable.
- **Notes:** Bulky mechanism but fully concealable. Good for multiplayer base defense.

---

## Vertical Transport

### Piston One-Way Elevator (4x4)
- **Dimensions:** 4x4 footprint, variable height
- **Materials:** Multiple pistons, redstone repeaters, building blocks
- **Build steps:**
  1. Build 4x4 shaft
  2. Arrange pistons to push player upward in sequence
  3. Set repeaters to delay 3 ticks (not 2) for proper timing
  4. First repeater in chain should be set to 4 ticks
- **How it works:** Sequential piston firing pushes the player upward one level at a time. Repeater timing ensures each piston fires after the previous one completes.
- **Notes:** Blocks line of sight -- best for enclosed shafts. One-way only (up).

---

## Signal / Logic Circuits

### Two Wire Control System
- **Dimensions:** Variable (depends on number of outputs)
- **Materials:** Redstone repeaters (many), AND gates, buttons, redstone wire
- **Build steps:**
  1. Run a top wire and a bottom wire with repeaters along the length
  2. On one side, place repeaters between buttons on the top wire
  3. On the bottom wire, use no repeaters (or as needed for timing)
  4. At each output point, build an AND gate receiving from both wires
- **How it works:** Pressing a specific button sends signals along both wires. The repeater delays are calibrated so signals arrive at the correct AND gate simultaneously, activating only that output.
- **Notes:** Requires precise repeater delay matching. Useful for selecting one of many outputs from a distance.

### One-Way Redstone Pulse
- **Dimensions:** Compact (fits in narrow passageway)
- **Materials:** 1 monostable circuit, 1 sticky piston, 2 pressure plates, redstone repeaters, 1 output block
- **Build steps:**
  1. Build a monostable circuit
  2. Place a sticky piston one block away from the monostable
  3. Position two pressure plates one block apart along the path
  4. Connect bottom layers with repeaters
  5. Output is the block pushed by the sticky piston
- **How it works:** The output activates when a player walks from one pressure plate to the other, but only in one direction. Walking the opposite direction does not trigger.
- **Notes:** Useful for one-way doors, directional traps, or asymmetric access control.

---

## Traps

### Disappearing Floor Trap
- **Dimensions:** Variable width x variable length x 2+ deep
- **Materials:** Sticky pistons (1 per trap block), building blocks matching floor, redstone, pressure plate or lever, optional: lava, dispensers with arrows
- **Build steps:**
  1. Dig a 2-block-deep pit under the trap area
  2. From each trap floor position, mine 2 blocks horizontally
  3. Place a sticky piston at the back of each horizontal hole, facing toward the floor position
  4. Attach matching floor blocks to each piston
  5. Wire pistons to a NOT gate connected to a pressure plate (piston extends = floor present; signal retracts floor)
  6. Below the pit, add hazards: long drop, lava, or dispensers with arrows
- **How it works:** Normally, pistons are extended, holding floor blocks in place. When the pressure plate is triggered, the NOT gate inverts the signal, retracting pistons and dropping the floor out from under the target.
- **Notes:** Add repeater delays to ensure the target is positioned over the pit. Trap auto-resets when pressure plate signal ends. Refillable variant uses sand/gravel for self-refilling.

### Suffocation Trap
- **Dimensions:** Tunnel width x tunnel length x 3 high (tunnel + 2 above)
- **Materials:** Sticky pistons (1 per trap section), building blocks matching ceiling, pressure plate or lever, optional RS-NOR latch
- **Build steps:**
  1. In a tunnel, mine the ceiling an additional 2 blocks higher
  2. Place a sticky piston at the top of the expanded ceiling, facing downward
  3. Attach a block matching the ceiling material to the sticky piston
  4. Wire to a pressure plate in the middle of the trap area
  5. Optional: add RS-NOR latch for manual reset control
- **How it works:** When triggered, sticky pistons push blocks down into the player's head space, dealing suffocation damage. The block occupies the same space as the entity's head hitbox.
- **Notes:** Most effective in tunnels (confined spaces). Works on aggressive non-baby mobs. Adding a slab below the pushed block prevents escape. RS-NOR latch prevents premature reset.

### Floodgate Trap
- **Dimensions:** Variable (tunnel + fluid reservoir)
- **Materials:** Pistons, pressure plates, RS-NOR latch, lava or water source blocks
- **Build steps:**
  1. Build a tunnel with pressure plate trigger
  2. Wire pressure plate to RS-NOR latch
  3. Use latch output to both seal the tunnel (block player in) and open floodgates
  4. Position fluid source blocks behind piston-controlled gates
- **How it works:** Stepping on the pressure plate triggers the RS-NOR latch, which simultaneously locks the player in the tunnel and releases lava/water. Fluids don't destroy pressure plates, making them ideal as triggers.
- **Notes:** One-shot trap unless manually reset via the latch.

### Hidden Bridge (Inverse Trap)
- **Dimensions:** Bridge length x width (typically 1-3 wide)
- **Materials:** Sticky pistons, building blocks, lever, redstone repeaters
- **Build steps:**
  1. Build pistons facing upward/sideways to push blocks into a bridge formation
  2. Normally retracted -- appears as lava pit or long fall
  3. Wire to a lever with repeater delays for sequential extension
- **How it works:** The reverse of a disappearing floor. Activating the lever extends pistons to create a walkable bridge over a hazard. Deactivates after delay or manual toggle.
- **Notes:** Repeater delays are adjustable (0-4 ticks per repeater) for dramatic sequential reveal.

---

## Self-Destructing Mechanisms

### TNT Self-Destruct
- **Dimensions:** Variable (under entire structure)
- **Materials:** TNT blocks, lever or button, building blocks
- **Build steps:**
  1. Lay TNT two blocks deep under all critical areas of the structure
  2. Create a 1x1 TNT column from the buried layer up to the surface
  3. Place a lever or button on top of the surface TNT block
- **How it works:** Activating the trigger detonates the surface TNT, which chain-reacts downward and outward through the buried layer, destroying the structure.
- **Notes:** Burying TNT two blocks deep prevents accidental detonation from surface activities. Test with lamps/pistons before placing TNT.

---

## Light Switches

### Piston Light Switch
- **Dimensions:** Varies (1x1x2 minimum per light)
- **Materials:** Pistons (regular or sticky), glowstone or redstone lamps, lever or button + T flip-flop, building blocks
- **Build steps:**
  1. Place light source (glowstone) behind a wall or floor
  2. Position piston to cover/uncover the light source
  3. Wire to a lever (toggle) or button through a T flip-flop (toggle from momentary input)
- **How it works:** Piston moves an opaque block to cover or reveal the light source, toggling room lighting.
- **Notes:** Redstone lamps are more resource-friendly than glowstone+piston combos. Lava can substitute as light source (contain in glass tubes). Light level changes affect mob spawning -- useful for mob farm toggle.

---

## Mining

### Cave Detection System
- **Dimensions:** 1x1x1 per test point (mechanism is the piston itself)
- **Materials:** 1 piston, 1 redstone torch (or lever), optional: sticky piston + 2-3 torches for mobile version
- **Build steps:**
  1. Place a piston on ground/ceiling/wall facing the direction you want to test
  2. Power the piston with a redstone torch or lever
  3. Observe result:
     - Piston extends = cavity exists within 12 blocks
     - Piston does not extend = solid blocks for 12+ blocks
  4. Advanced 1x2 passage version: place torches on wall above pistons, use side-facing and forward-facing pistons for multi-directional detection
- **How it works:** Pistons can only extend if there's space within their 12-block push limit. If all 12 blocks ahead are solid, the piston cannot push and stays retracted.
- **Notes:** 12-block detection range limits effectiveness. Useful for finding caves, ravines, or dungeons while mining.

---

## Miscellaneous

### Locking Chest
- **Dimensions:** 1x1x3 (chest + block above + piston)
- **Materials:** 1 sticky piston, 1 opaque block, 1 chest, lever or combination lock
- **Build steps:**
  1. Place chest
  2. Position sticky piston above or to the side, with an opaque block attached
  3. When activated, piston pushes opaque block directly above the chest
  4. Wire to lever or combination lock circuit
- **How it works:** An opaque block directly above a chest prevents it from being opened. The sticky piston moves this block on/off.
- **Notes:** Not griefer-proof -- players can break the blocking block or the chest itself. Combine with combination lock for added security.

### Garbage Disposal (Piston Incinerator)
- **Dimensions:** 3x1x2 (plus lava pit)
- **Materials:** 3 cobblestone blocks, 1 piston (facing right), 1 button, lava bucket, 2-block-deep hole
- **Build steps:**
  1. Place a row of three cobblestone blocks
  2. On the left: cobblestone. In the middle: piston facing right. Right side: empty
  3. Dig a 2-block-deep hole at the end (right side)
  4. Place lava in the hole
  5. Place button on the top-left block
- **How it works:** Items dropped in front of the piston get pushed into the lava pit when the button is pressed.
- **Notes:** Only incinerates dropped items, not placed blocks. Simpler alternatives exist (just drop items into lava manually).

### Piston Table
- **Dimensions:** 1x1x2
- **Materials:** 1 piston (upward-facing), 1 redstone torch
- **Build steps:**
  1. Place a redstone torch on the ground
  2. Place an upward-facing piston on top of the redstone torch
- **How it works:** The redstone torch permanently powers the piston, keeping it extended. The extended piston head looks like a table surface.
- **Notes:** Purely decorative. Chairs (stairs) can be placed around it.

---

# Page 2: Piston Uses (Tutorial:Piston_uses)

## Piston Doors

### Simplest 1x2 Piston Door
- **Dimensions:** 1x2 opening
- **Materials:** 2 horizontal pistons, 1 block, 1 lever, 1 redstone dust (Bedrock only)
- **Build steps:**
  1. Stack two horizontal pistons facing the same direction, one on top of the other
  2. Place a block next to the top piston
  3. Place a lever on this block
- **How it works:** The lever powers the block, which quasi-powers the top piston (Java). The top piston extends, and quasi-connectivity powers the bottom piston too.
- **Notes:** Bedrock Edition lacks quasi-connectivity -- add a piece of redstone dust below the block to power the bottom piston directly.

### Compact 2x3 Piston Door
- **Dimensions:** 2x3 opening
- **Materials:** Multiple pistons, redstone, building blocks (detailed schematic on sub-page)
- **Notes:** Video tutorial and detailed schematic available on linked sub-page.

### 3x3 Piston Door
- **Dimensions:** 3x3 opening
- **Notes:** Requires more complex wiring. Video tutorial available.

### 4x4 Piston Door
- **Dimensions:** 4x4 opening
- **Notes:** Video tutorial available.

### 5x5 Piston Door
- **Dimensions:** 5x5 opening
- **Notes:** Good combination of compact mechanism and fast operation. Video tutorial available.

### Scalable Piston Door (1.12+, up to 15x7)
- **Dimensions:** Scalable up to 15x7
- **Materials:** Observer blocks, pistons, redstone
- **Build steps:** Uses observer blocks for a design that scales easily by repeating modular sections.
- **How it works:** Observers detect piston state changes and propagate signals, creating a chain reaction that scales without additional wiring complexity.
- **Notes:** Resource-efficient enough for survival mode. Requires Minecraft 1.12+.

### Flush Seamless 2x2 Piston Door
- **Dimensions:** 2x2 opening
- **Materials:** Pistons, redstone torch, redstone, building blocks
- **Build steps:** Fully hidden mechanism -- no pistons or redstone visible from either side. Can be activated from both sides.
- **How it works:** Pistons first retract door blocks flush with the wall, then move them sideways out of the opening.
- **Notes:** Not overly complicated or resource-heavy despite the seamless appearance.

### Smallest 3x3 Piston Door (56 blocks)
- **Dimensions:** 3x3 opening, 56 total blocks
- **Materials:** Pistons, redstone, building blocks (56 blocks total)
- **Notes:** Created by SacredRedstone. Smallest possible seamless 3x3 design.

### 3x3 Spiraling Iris Door
- **Dimensions:** 3x3 opening
- **Notes:** Spiral/iris closing animation. Video tutorial available.

### Piston Lava Door
- **Dimensions:** Variable
- **Materials:** Pistons, redstone, pressure plates, lava
- **How it works:** Pistons hold back lava that serves as the "door." When pistons retract, lava flows down. When extended, passage is safe.
- **Notes:** Allows safe entry without burning. Pressure plate activation.

### Self-Resetting Sand Door
- **Dimensions:** Variable
- **Materials:** Sand, pistons, redstone
- **How it works:** Uses gravity-affected sand blocks. After piston retracts, sand falls back into place automatically.
- **Notes:** Self-resetting without complex redstone.

### Castle Gate
- **Dimensions:** Variable
- **Notes:** Video tutorial available.

---

## Piston Extenders

### Double Piston Extender (Tileable, Upward)
- **Dimensions:** 1-wide, tileable
- **Materials:** 2 pistons, redstone, building blocks
- **Notes:** "Everything but the input is flush." Small tileable horizontal double extender.

### Triple Piston Extender
- **Dimensions:** Larger than double
- **Materials:** 3 pistons, redstone, timing circuit
- **Notes:** Smallest horizontal triple extender design may be out of date.

### Ceiling Double Extender (Tileable)
- **Dimensions:** 1-wide, tileable
- **Notes:** Ceiling-mounted variant for downward extension.

### 1-Wide Downward Double Extender
- **Dimensions:** 1-wide
- **Notes:** Extends blocks downward.

---

## Structures

### Piston Draw Bridge
- **Dimensions:** Bridge length x width
- **Materials:** Sticky pistons, building blocks, redstone, lever
- **How it works:** Sticky pistons extend to push bridge blocks across a gap (lava, water, or pit). Retracting hides the bridge.
- **Notes:** Functions as a moat. Max bridge length limited by piston push limit (12 blocks).

### Scrolling Display
- **Dimensions:** Up to 12 blocks wide (piston limit), unlimited height
- **Materials:** Pistons, colored blocks for display, redstone clock
- **Build steps:**
  1. Create two rows of movable material
  2. Build your image/message into the block pattern
  3. Use pistons to move blocks: across, back, across opposite direction, return to front
  4. Clock circuit drives the cycle
- **How it works:** Pistons push rows of blocks in a loop, creating a scrolling banner effect.
- **Notes:** Width limited to 12 blocks (piston push limit). Height is unrestricted.

### Dry Dock (Boat Storage)
- **Dimensions:** 1+ wide pool area
- **Materials:** 1 piston (upward-facing), lever, 1-block-deep water pool, optional: soul sand
- **Build steps:**
  1. Build a 1-block-deep pool of water
  2. Place an upward-facing piston in the pool floor
  3. Wire the piston to a lever
  4. When activated, piston raises, lifting the boat out of water
- **How it works:** Piston pushes boat above water level, preventing drift and collision damage.
- **Notes:** Soul sand on contact surfaces helps preserve boat durability.

### Variable Enchantment Room
- **Dimensions:** Variable (room + piston mechanism)
- **Materials:** Bookshelves, pistons, redstone, lever/buttons
- **How it works:** Pistons move bookshelves closer to or farther from the enchanting table, allowing the player to select low/medium/high enchantment levels.
- **Notes:** Three settings: low-level, medium-level, high-level.

### Self-Repairing Structure
- **Dimensions:** Up to 12 blocks (piston push limit)
- **Materials:** Cobblestone generator (water + lava), pistons, redstone clock, building blocks
- **Build steps:**
  1. Build a cobblestone generator (water meets lava to create cobblestone)
  2. Build a redstone clock to pulse the generator
  3. Connect pistons to push generated cobblestone into position
- **How it works:** Cobblestone generator endlessly creates blocks. Pistons push them into a wall/floor/bridge formation. If blocks are destroyed, new ones fill the gap.
- **Notes:** Piston push limit of 12 blocks limits scale. Chests, note blocks, obsidian, bedrock, monster spawners, and furnaces cannot be pushed (use as stoppers/endpoints). Works for bridges, floors, and walls.

---

## Traps (Piston-Based)

### Disappearing Floor Trap (Piston Version)
- **Dimensions:** Variable
- **Materials:** Sticky pistons, building blocks, NOT gate, pressure plate
- **Notes:** Same as described in Mechanisms page. See above for full build.

---

## Technical Notes (Piston Mechanics)

- **Piston push limit:** 12 blocks maximum
- **Unpushable blocks:** Chests, note blocks, obsidian, bedrock, monster spawners, furnaces
- **Quasi-connectivity (Java only):** Pistons can be powered by blocks that would power the space above them. Does NOT work in Bedrock Edition.
- **Slime blocks (1.8+):** Adjacent blocks attach to slime blocks when pushed by pistons, enabling flying machines
- **Observer blocks (1.12+):** Detect block state changes, enabling scalable and self-propagating piston designs

---

# Page 3: Item Sorting (Tutorial:Item_sorting)

## Design 1: Basic Hopper Item Sorter (Overflow-Protected)

### Basic Hopper Item Sorter
- **Dimensions:** 1-wide per module, tileable horizontally
- **Materials (per module):** 2 hoppers, 1 redstone torch, 1 redstone dust, 8 building blocks (~10 redstone dust equivalent total)
- **Speed:** 2.5 items per second, silent operation
- **Build steps:**
  1. Place a bottom hopper pointing into a chest (storage)
  2. Place a top hopper on top, pointing AWAY from the bottom hopper (into the main item stream/pipe)
  3. Place a redstone torch on the side of a block adjacent to the bottom hopper (powers the bottom hopper to lock it)
  4. Place redstone dust to connect the comparator output from the top hopper to the torch
  5. The comparator reads the top hopper's contents
- **Hopper contents -- TOP hopper (filter):**
  - Slot 1: 41 of the item you want to sort
  - Slots 2-5: 1 renamed stick each (4 total, renamed so they never match incoming items)
- **Hopper contents -- BOTTOM hopper:**
  - Starts empty; locked by redstone torch power
- **How it works:** The top hopper holds 41 target items + 4 filler items. This produces a comparator signal strength of 2 (not enough to unlock the bottom hopper). When a 42nd target item enters from the item stream, signal strength rises to 3, which is just enough to disable the redstone torch, unlocking the bottom hopper. The bottom hopper pulls items from the top hopper into storage. Once the top hopper drops back to 41 items, signal returns to 2 and the torch re-engages, re-locking the bottom hopper.
- **Important notes/gotchas:**
  - Top hopper MUST point away from bottom hopper, otherwise it pushes items directly into the bottom hopper bypassing the filter
  - Use renamed junk items (sticks) to ensure they never accidentally match incoming items
  - Signal strength of 3 unlocks only the target hopper; signal strength of 4 would bleed into adjacent modules and break the system
  - 1 full stack (64) + 4 junk items = signal strength 3 (safe). More junk items per slot reduces overflow protection margin
  - Chests are typically placed sideways to the right of the bottom hopper
  - Additional hoppers below or right of the bottom hopper can feed more chests

---

## Design 2: Double-Speed Hopper Item Sorter

### Double-Speed Item Sorter
- **Dimensions:** 1-wide, tileable
- **Materials (per module):** 3 hoppers, 1 redstone torch, 1 redstone dust (~10 RSD)
- **Speed:** 5 items per second, silent
- **Build steps:**
  1. Same as basic design but with an additional hopper stacked between top and bottom
  2. Middle hopper also contains filter items
- **Hopper contents -- TOP hopper:**
  - Slot 1: 41 of target item
  - Slots 2-5: 1 renamed stick each
- **Hopper contents -- MIDDLE hopper:**
  - Slot 1: 64 of target item (full stack)
  - Slots 2-5: 1 renamed tropical fish each (DIFFERENT junk item than top hopper)
- **Hopper contents -- BOTTOM hopper:**
  - Starts empty; locked by redstone
- **How it works:** Two filter hoppers can both output simultaneously, doubling throughput from 2.5 to 5 items per second. The middle hopper uses a different junk item type to prevent cross-contamination.
- **Important notes:** Must use different junk items in each filter hopper to prevent items migrating between them.

---

## Design 3: Compact Item Sorter (No Overflow Protection)

### Compact Item Sorter
- **Dimensions:** 1-wide, tileable
- **Materials (per module):** 2 hoppers, 1 redstone dust (~9 RSD)
- **Speed:** 2.5 items per second, silent
- **Hopper contents -- TOP hopper:**
  - Slot 1: 1 of target item
  - Slots 2-5: 18 renamed sticks total (distributed across slots)
- **How it works:** Removes the center column of blocks from the basic design to save resources. Functions the same way but without overflow protection.
- **Important notes/gotchas:**
  - NO OVERFLOW PROTECTION: If the input hopper fills up, signal strength reaches 3, which unlocks adjacent hoppers and breaks the system
  - Only suitable for systems where overflow is impossible (controlled input rates)

---

## Design 4: Hybrid Sorter (h-A / h-B Alternating)

### Hybrid Sorter
- **Dimensions:** 1-wide per module, must alternate A-B-A-B pattern
- **Materials (per A+B pair):** 2 comparators, 2 repeaters, 2 redstone torches, 10 redstone dust (~22 RSD per pair)
- **Speed:** 2.5 items per second, silent
- **Timing:** h-A = 3 tick delay, h-B = 4 tick delay
- **Hopper contents (both A and B):**
  - Slot 1: 1 of target item
  - Slots 2-5: 21 renamed cheap stackable items
- **How it works:** Complete circuit isolation between modules. Signals never interfere with adjacent tiles when used in strict A-B-A-B alternating pattern.
- **Important notes:** Must maintain alternating A-B pattern. Cannot use all A or all B modules.

---

## Design 5: Optimized Hybrid Type V (Recommended -- Java 1.18+ and Bedrock Compatible)

### Optimized Hybrid Type V (oh5-A / oh5-B)
- **Dimensions:** 1-wide, alternating A-B tileable
- **Materials (per A+B pair):** 2 comparators, 3 repeaters, 2 redstone torches, 6 redstone dust (~23 RSD per pair)
- **Speed:** 2.5 items/sec (upgradeable to 5 items/sec with double-speed variant)
- **Timing:** Variable, 3-6 tick delay
- **Hopper contents (both A and B):**
  - Slot 1: 2 of target item (for 64-stackable items) or 2 of target (for 16-stackable items)
  - Slots 2-5: 20 renamed cheap items (for 64-stack) or 14 renamed cheap items (for 16-stack)
- **How it works:** Completely isolated A and B tiles that can be used independently. All torches protected by repeaters, preventing torch burnout in Java 1.18+.
- **Double-speed variant:**
  1. Point the filter hopper downward
  2. In the hopper below the filter, place a full stack in slot 1 and different filler items in slots 2-5
  3. Use at least 18 items in the filter hopper's first slot for lag-safety (5 is NOT safe)
- **Important notes:**
  - Works in both Java 1.18+ AND Bedrock Edition (no torch burnout)
  - Floating solid block in oh5-A is required to keep circuits isolated
  - Glass block in oh5-B can be replaced with top slab or regular solid block
  - Completely isolated tiles -- can be used independently (no forced A-B alternating)

---

## Design 6: Other Optimized Hybrid Types (Summary)

### OH Type I & II
- **Materials per pair:** 2 comparators, 6 torches, 10 dust (~22 RSD) for Type I; 2 comparators, 2 repeaters, 2 torches, 5-6 dust (~19-20 RSD) for Type II
- **Hopper contents:** Slot 1: 2 items; Slots 2-5: 20 items (64-stack) or 14 items (16-stack)
- **Notes:** Type II saves dust but cannot add master on/off circuit.

### OH Type III
- **Materials per pair:** 2 comparators, 1 repeater, 4 torches, 4 dust (~17 RSD -- most resource-efficient)
- **Hopper contents:** Slot 1: 2 items; Slots 2-5: 20 items (64-stack) or 14 items (16-stack)
- **Critical setup requirement:** Any oh3-B filter hopper can ONLY be filled after at least one neighboring oh3-A has been initialized first
- **Overflow behavior:** When oh3-A overflows, it locks the two adjacent oh3-B tiles (they can still pull up to 62 items but cannot deposit into storage until overflow is resolved)

### OH Type IV
- **Materials per pair:** 2 comparators, 1 repeater, 2 torches, 5 dust (~16 RSD)
- **Warning:** Prone to redstone torch burnout in Java 1.18+. Burnout causes filter items to drain, breaking sorting entirely. Not an issue on Bedrock.

### OH Basic Type
- **Materials per pair:** 2 comparators, 2 repeaters, 2 torches, 7 dust (~21 RSD)
- **Hopper contents differ per module:**
  - oh-basic-A: Slot 1: 2 items; Slots 2-5: 20 or 14 cheap items
  - oh-basic-B: Slot 1: 2 items; Slots 2-5: 66 or 57 cheap items (significantly more filler needed)
- **Notes:** Eliminates one comparator but requires more filler items in B modules.

---

## Input Delivery Methods

### Hopper Pipe
- **Materials:** Chain of hoppers pointing at each other
- **Speed:** Full hopper speed
- **Pros:** Reliable, simple
- **Cons:** Iron-intensive, causes server lag at scale
- **Bedrock issue:** Transfers at full speed, pushing a small percentage of items past filters without sorting them

### Item Stream (Water-Based)
- **Materials:** Water source, ice blocks (Silk Touch), hoppers, dropper, signs/fence gates/top slabs/trapdoors/buttons (water stoppers)
- **Speed:** Can be faster than hoppers
- **Pros:** Cheaper than hopper pipes
- **Cons:** May generate more lag than hoppers; items can skip filters if too many pass simultaneously
- **Build tip:** Use ice under water for faster item transport. Use signs, open fence gates, top slabs, trapdoors, or buttons to stop water flow without blocking item entities.

### Minecart Delivery
- **Materials:** Chest minecarts or hopper minecarts, rails
- **Speed:** Typically much slower than other methods
- **Pros:** Reliable
- **Cons:** Slowest delivery method

---

## Bedrock Edition Adjustments

- **Hybrid h-A:** 21 non-filter items in slots 2-5
- **Hybrid h-B:** 20 non-filter items (NOT 21 -- using 21 causes filter items to drain through)
- **For 16-stack items:** h-A: 15 non-filter; h-B: 14 non-filter
- **General note:** With 21 items in B, the hopper tends to pass the filter item through. Use 20 to keep 1 filter item stable (may occasionally have 2).
- **Redstone signals:** Cannot travel down transparent blocks in Java Edition
- **Soft inversion:** Unique to Bedrock Edition

---

## Common Troubleshooting

- **Signal strength 3** is the safe operating threshold -- unlocks only the target hopper
- **Signal strength 4** bleeds into adjacent modules, breaking the entire system
- **Torch burnout (Java 1.18+):** Unprotected torches can burn out, draining filter items. Use Type V design or protect torches with repeaters.
- **Safety measure:** Use renamed junk items in the first sorter module to catch normal (unnamed) junk items. Add an overfill detector on storage that disables the entire sorter input.

---

# Page 4: Redstone Tips (Tutorial:Redstone_tips)

## Planning and Design

### Circuit Planning Methodology
- Determine your control method (player input, mob detection, timer, etc.)
- Identify all target mechanisms (doors, lights, pistons, dispensers)
- Plan signal transmission routes before placing any redstone
- Decide if signals need combining (AND/OR/XOR logic)
- **Gotcha:** Starting without a plan leads to inefficient designs that are hard to modify later

### Size vs. Function Trade-Off
- Build as small as possible while still functioning
- If you encounter problems at small scale, make it bigger -- do not force cramped designs
- Complex circuits (redstone computers) require substantial space
- Always overestimate materials and space rather than underestimate

---

## Construction Best Practices

### Color-Coding Circuits
- **Materials:** Wool, concrete, or terracotta in various colors
- **How to use:**
  - Assign different colors to: input blocks, output blocks, mobile/moving components, and distinct circuit sections
  - Example: red wool for inputs, blue for outputs, yellow for clock circuits
- **Benefits:** Helps remember circuit logic during debugging; enables others to replicate your design; makes modifications safer
- **Avoid:** Similar-looking blocks together (coal block vs. black concrete)
- **Advanced:** Use glass to display circuit internals while containing water/lava

### Structural Protection
- **Materials:** Use a dedicated block type (stone bricks, snow, wool, concrete) exclusively for redstone circuit housing
- **How it works:** When digging near circuits, recognizing the dedicated block type signals "stop -- circuit ahead"
- **Testing trick:** Place redstone lamps or pistons temporarily to test whether a space is powered before committing to final block placement

### TNT Safety Protocol
- ALWAYS place TNT last, after the rest of the circuit is complete and tested
- **Gotcha:** Redstone torches briefly power for one tick when placed on powered blocks -- this can detonate TNT during construction
- **Best practice:** Build and test the entire circuit with lamps/pistons substituting for TNT, then swap in TNT only when verified

---

## Troubleshooting Guide

### Signal Dropout Diagnosis
- Systematically work through the circuit testing each input
- Pinpoint exactly where the signal fails or appears unexpectedly
- **Common problems checklist:**
  1. **Timing misalignment:** Components fire out of sequence (adjust repeater delays)
  2. **Signal crossing:** Unintended redstone connections activating wrong outputs
  3. **Feedback loops:** Repeater output cycling back into its own input
  4. **Piston wire displacement:** Pistons moving blocks that carry redstone, breaking connections
  5. **Weak vs. strong power:** Weak-powered blocks cannot power adjacent redstone components -- add a repeater to convert to strong power
  6. **Non-opaque block transmission:** Power cannot transmit through glass, slabs, stairs, etc. -- replace with opaque blocks or route around
  7. **Burned-out redstone torches:** Indicates a short circuit (torch toggling too rapidly). Fix the feedback loop causing rapid toggling
  8. **Indirect powering:** Pistons, dispensers, and droppers can be powered indirectly (quasi-connectivity in Java)
  9. **Version incompatibility:** Old tutorial designs may not work in current Minecraft versions due to mechanic changes

---

## Optimization Techniques

### Speed Optimization
- Shorten signal delays by removing unnecessary repeaters
- Reduce pulse durations to minimum needed
- Minimize redstone dust line lengths (each dust block adds delay)
- Use newer components: comparators, locking repeaters, observers replace older multi-component designs

### Size Reduction
- Remove unnecessary components
- Shorten redstone dust lines
- Find alternative designs that accomplish the same function with fewer blocks
- Explore community-optimized designs for common circuits

### Robustness Testing Checklist
1. Activate with extremely short pulses -- does it still function correctly?
2. Rapidly activate and deactivate in succession -- does it maintain stability or enter a broken state?
3. If either test fails, add input filtering (pulse limiter/extender) to sanitize the input signal
4. Test that chunk unloading doesn't break constantly-running clocks (clock may freeze in an unintended state)

---

## Lag Reduction Techniques

### Redstone Dust Optimization
- **Problem:** Each redstone dust state change creates hundreds of block updates
- **Solution:** Reduce line lengths as much as possible
- **Alternative:** Use rail lines with observers instead of redstone dust (far fewer block updates)

### Hopper Lag Reduction
- **Problem:** Hoppers constantly check for items, generating updates every tick
- **Solution 1:** Power hoppers with redstone when not in use (disables their tick processing)
- **Solution 2:** Place a container (chest, barrel, composter) above each hopper to disable item-entity scanning

### Lighting Update Reduction
- **Problem:** Torches and lamps changing state trigger light recalculation across hundreds of blocks
- **Solution:** Conceal torches/lamps inside opaque blocks, or add permanent light sources nearby so toggling doesn't change the light level significantly

### Particle and Piston Overhead
- **Particles:** Too many redstone torches, active dust, or dispensed fireworks overload rendering
- **Pistons:** Minimize simultaneous block movement to reduce neighbor-checking overhead

---

## Resource Farming Guide (for Redstone Projects)

### Key Materials and Sources

| Material | Best Source | Alternative |
|----------|-----------|-------------|
| Redstone dust | Fortune III mining underground | Witch farms, raid farms, cleric villager trading |
| Iron ingots | Iron golem farm | Mining |
| Slimeballs | Slime farm (slime chunks) | Wandering trader |
| String | Spider farm | Piglin bartering |
| Nether quartz | Nether mining | Piglin bartering |
| Glowstone | Nether ceiling | Cleric/wandering trader trades |
| Stone/cobblestone | Generator or mining | Smooth stone for repeaters/comparators |
| Honey blocks | Bee farm | Used in mobile/flying constructions |

---

## Prototyping Workflow

### Creative Mode Testing Protocol
1. Create a superflat creative world with cheats enabled
2. Set gamerules: permanent day, disable mob spawning
3. Build your circuit at full scale
4. Test all input combinations
5. Press F3+N to enter spectator mode -- fly through the circuit to inspect internals
6. Identify improvements and count exact materials needed
7. Transfer the design to survival world with precise material list
- **Benefit:** Zero risk of resource loss; unlimited experimentation

---

# Appendix: Key Redstone Constants

| Property | Value |
|----------|-------|
| Redstone dust max signal strength | 15 blocks |
| Repeater delay options | 1, 2, 3, or 4 ticks (right-click to cycle) |
| Piston push limit | 12 blocks |
| Hopper transfer rate | 2.5 items/sec (1 item every 4 ticks) |
| Hopper collection cooldown | 8 game ticks |
| Redstone tick | 0.1 seconds (2 game ticks per redstone tick) |
| Comparator modes | Compare (front torch off) / Subtract (front torch on) |
| Unpushable blocks | Obsidian, bedrock, end portal frame, enchanting table, chest, barrel, furnace, brewing stand, beacon, anvil, grindstone, spawner, note block, jukebox |
