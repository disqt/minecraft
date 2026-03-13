# Redstone Tutorials - Batch 2
## Extracted from Minecraft Wiki Tutorial Pages (2026-03-10)

---

# 1. TRAPS

## Explosive Traps

### Bog-Standard Landmine
- **Dimensions:** 1x1x2 (single block footprint)
- **Materials:** 1 pressure plate, 1+ TNT
- **Build steps:**
  1. Place one or more TNT blocks in the ground
  2. Place a pressure plate on top
- **How it works:** Stepping on the plate ignites the TNT below.
- **Notes:** Non-lethal by itself. Water sources at the bottom reduce landscape damage but also reduce effectiveness.

### Instant Landmine (Dispenser + Minecart TNT)
- **Dimensions:** 3x3x3 hole
- **Materials:** 1 dirt block, 1 rail, 1 minecart with TNT, 1 dispenser, 1 flint and steel, TNT blocks, 1 pressure plate
- **Build steps:**
  1. Dig a 3x3x3 hole, stand on a corner
  2. Place dirt block in center with rail on top
  3. Place minecart with TNT on rail
  4. Destroy block under rail to derail the minecart (drops one block)
  5. Place dispenser above minecart, load with flint and steel
  6. Surround minecart with TNT
  7. Cover completely, place pressure plate on top
- **How it works:** Pressure plate triggers dispenser, which uses flint and steel to ignite the TNT minecart -- instant explosion with no escape time.
- **Notes:** Careful placement required to avoid accidental triggering.

### Instant Landmine (End Crystal Variant)
- **Dimensions:** 3x3x3 hole
- **Materials:** 1 end crystal, 1 dispenser, arrows, TNT blocks
- **Build steps:**
  1. Follow the Instant Landmine setup above
  2. Replace the wool block with an end crystal
  3. Load the dispenser with arrows instead of flint and steel
- **How it works:** Dispenser shoots arrow at end crystal, creating an instant explosion with no escape window.
- **Notes:** More expensive but truly instant.

### Sculk Proximity Landmine
- **Dimensions:** 2x2 wide, 3 blocks deep
- **Materials:** Powered rails (unpowered), 2+ TNT minecarts, wool blocks, 1 sculk sensor, carpets
- **Build steps:**
  1. Dig 2x2 hole, 3 blocks deep
  2. Seal top with blocks matching the surrounding terrain
  3. Surround with 2-block-high wool walls, leaving one gap for your escape
  4. Dig escape route away from the mine through that gap
  5. Place powered rails (leave them unpowered) along the wall opposite the escape
  6. Carefully place 2+ TNT minecarts on the same powered rail (right-click the side hitbox)
  7. **Hold Shift the entire time** while placing sculk sensor adjacent to or in front of the escape hole
  8. Sneak into the escape hole and seal the gap with wool
- **How it works:** The sculk sensor detects any vibrations (footsteps, block breaks) and triggers the TNT minecarts.
- **Notes:** One wrong move makes you the victim. Never step over the landmine. Carpets and wool muffle vibrations. Extremely dangerous to build.

### Tree Trap
- **Dimensions:** Tree-sized
- **Materials:** 1 observer, TNT, existing tree
- **Build steps:**
  1. Place observer directly under a tree's log blocks, facing the logs
  2. Place TNT connected to the observer's output
- **How it works:** When someone chops the tree, the observer detects the log block change and ignites the TNT.
- **Notes:** Alternative: use lever + NOT gate if you lack quartz for the observer.

### Cake Trap (Observer)
- **Dimensions:** 1x1, 3 blocks deep
- **Materials:** 1 observer, 1 cake, TNT
- **Build steps:**
  1. Dig down 2 blocks in a flat area
  2. Place observer in the top position, facing up
  3. Place cake on top of the observer
  4. Place TNT under the observer
- **How it works:** When someone eats the cake, the observer detects the block state change and ignites the TNT.
- **Notes:** Place the cake BEFORE the TNT to avoid premature detonation.

### TNT Floor House
- **Dimensions:** Room-sized
- **Materials:** TNT blocks, carpet, 1 iron door, pressure plates, redstone repeaters
- **Build steps:**
  1. Build the base structure of a house
  2. Make the floor entirely out of TNT blocks
  3. Cover all TNT with carpet so it looks normal
  4. Place iron door at entrance with pressure plate
  5. Wire the pressure plate signal to basement TNT
  6. Optional: add repeaters to delay the fuse for dramatic effect
- **How it works:** When anyone steps on the pressure plate (seemingly to open the door), the TNT floor ignites.
- **Notes:** Extra delay via repeaters prevents immediate escape.

### Exploding Furnace
- **Dimensions:** 1x1x3
- **Materials:** 1 furnace, 1 redstone comparator, TNT
- **Build steps:**
  1. Place furnace
  2. Place comparator directly behind it (pointing away)
  3. Place TNT behind the comparator
- **How it works:** When an item is added to the furnace, the comparator detects the inventory change and outputs a signal that detonates the TNT.
- **Notes:** Alternative version: pre-load the furnace and use a redstone torch inverter so it explodes when the item is *removed*.

### C4 Trap
- **Dimensions:** Variable (stack-based)
- **Materials:** TNT (stacked), 1 dispenser, fire charges, button or pressure plate
- **Build steps:**
  1. Stack TNT vertically or horizontally
  2. Place dispenser one block above (vertical) or beside (horizontal) the stack
  3. Fill dispenser with fire charges
  4. Connect button or pressure plate to dispenser
- **How it works:** Fire charge from the dispenser ignites the TNT stack instantly.
- **Notes:** Similar to a flaming arrow hitting a stack from above.

### Warehouse Trap
- **Dimensions:** ~50x50 floor
- **Materials:** TNT, 1 pressure plate, redstone repeaters (15-second delay worth)
- **Build steps:**
  1. Build large warehouse (~50x50)
  2. Place TNT in a checkerboard pattern underneath the floor
  3. Place entrance pressure plate connected to a chain of repeaters totaling ~15 seconds of delay
  4. Wire the repeater chain to the TNT ignition circuit
- **How it works:** Player enters, pressure plate starts a long fuse. By the time TNT starts going off, the player is deep inside with no escape route.
- **Notes:** The progressive ignition is what makes this deadly -- the exit is destroyed first.

---

## Pitfall Traps

### Chest Pitfall
- **Dimensions:** 2x2 hole to lethal depth
- **Materials:** 4 hoppers, 4 chests
- **Build steps:**
  1. Dig a 2x2 hole to lethal fall depth (24+ blocks)
  2. Place one hopper per block at the bottom, all pointing into chests below
  3. Build an access hallway to reach the chests from the side
- **How it works:** Victim falls to their death. Items land on hoppers and get collected into chests automatically.
- **Notes:** Useful for collecting drops from defeated players.

### Fence Pitfall
- **Dimensions:** Hallway length, pit depth varies
- **Materials:** Fence posts, sand or gravel, pit
- **Build steps:**
  1. Construct a hallway (diagonal layout works best)
  2. Place fence posts across the path underneath where the floor will be
  3. Drop sand/gravel onto the fences to create a "floor"
  4. Dig a deep pit below the fences
- **How it works:** Sand on fences are entities, not solid blocks. Players walk onto them and fall through into the pit.
- **Notes:** Sand on fences sits half a block higher than normal -- observant players may notice.

### Fake Water Pitfall
- **Dimensions:** 2x2 minimum, 30+ blocks deep
- **Materials:** Blue wool, lapis block, or blue glass (1 block)
- **Build steps:**
  1. Dig a 2x2 hole at least 30 blocks deep
  2. Place a blue block (lapis, blue wool, blue glass) at the very bottom
- **How it works:** From above, the blue block looks like water. Players jump down expecting a safe water landing and die from fall damage.
- **Notes:** 30 blocks is the minimum for a guaranteed kill. Experienced players will be suspicious.

### Fake Elevator
- **Dimensions:** 1x1 shaft, 30-40 blocks deep
- **Materials:** Water (1 bucket), signs (optional, for floor countdown)
- **Build steps:**
  1. Create a vertical shaft 30-40 blocks deep
  2. Place water ONLY at the very top block (no water column below)
  3. Optional: place signs on the walls counting down floors ("35", "34", "33"...)
  4. Optional: place hoppers with chests at the bottom for loot collection
- **How it works:** Looks like a bubble elevator from the top, but there is no water column. Victim steps in and free-falls to death.
- **Notes:** 30-40 blocks deep guarantees a kill from fall damage.

### Piston Pit
- **Dimensions:** Variable, up to 12+ rows
- **Materials:** 1 piston, signs, sand/gravel, pressure plate or lever
- **Build steps:**
  1. Place piston aimed at the block that signs are attached to
  2. Stack sand/gravel on the signs (up to 12 rows)
  3. Leave an empty block space at the end of the piston's push range
  4. Wire the piston to a pressure plate or lever
- **How it works:** Piston pushes the support block, breaking all signs. Sand/gravel falls, taking the victim with it.
- **Notes:** Use sticky piston + NOT gate for more than 12 rows.

### False-Floor Bridge Trap
- **Dimensions:** Bridge length x 2+ blocks wide x pit depth
- **Materials:** TNT, torches, sand/gravel, pressure plates, surrounding blocks
- **Build steps:**
  1. Dig a long, deep pit
  2. Build a bridge across using TNT blocks (minimum 2 wide)
  3. Replace some TNT blocks with torches (these are the safe path)
  4. Place sand/gravel on the torches
  5. Cover the remaining TNT with matching blocks
  6. Place pressure plates over the sand/gravel sections
- **How it works:** Unauthorized players step on a pressure plate over TNT, the bridge explodes. Authorized players know to walk on the torch-supported sections.
- **Notes:** Only the builder knows the safe path.

---

## Lava Traps

### Lava Staircase
- **Dimensions:** Standard staircase
- **Materials:** 1 stone pressure plate, redstone dust, 1 dispenser, 1 lava bucket
- **Build steps:**
  1. Dig a standard staircase downward
  2. Place a stone pressure plate partway down (blends with stone)
  3. Run redstone dust upward from the pressure plate
  4. Connect to a dispenser containing a lava bucket, positioned at the top of the stairs
- **How it works:** Stepping on the plate triggers the dispenser, which dumps lava that flows down the staircase toward the victim.
- **Notes:** Can be reversed as an escape mechanism if the pressure plate faces the opposite direction.

### Chest Lava Trap
- **Dimensions:** Room-sized
- **Materials:** 2 rows of sticky pistons (4 blocks apart), solid blocks, redstone torches, 1 trapped chest, lava
- **Build steps:**
  1. Build 2 rows of sticky pistons facing each other, 4 blocks apart
  2. Attach solid blocks to the piston faces
  3. Wire the piston rows to redstone torches
  4. Connect the trapped chest to the redstone torches
  5. Dig a hole below the pistons and fill with lava
  6. Decorate around the chest to look inviting
- **How it works:** Opening the trapped chest sends a redstone signal. Pistons retract, dropping the player into lava below.
- **Notes:** Decoration is key to making the chest look worth opening.

### Trapdoor Lava Pit
- **Dimensions:** Pit-sized
- **Materials:** Trapdoors, 1 pressure plate, lava
- **Build steps:**
  1. Dig a pit and fill the bottom with lava
  2. Cover the pit with closed trapdoors
  3. Place a pressure plate on the surface nearby, wired to the trapdoors
- **How it works:** Stepping on the pressure plate opens the trapdoors. Victim falls into lava.
- **Notes:** Once triggered, escape is nearly impossible.

---

## Water Traps

### Fake Water Elevator (Drowning)
- **Dimensions:** Room height
- **Materials:** Soul sand, water, optional magma blocks
- **Build steps:**
  1. Create a soul sand bubble column (upward flow)
  2. Do NOT provide an exit at the top -- seal the ceiling
  3. Optional: use magma blocks for downward suction variant
- **How it works:** Bubble column forces player upward against the sealed ceiling. They cannot break blocks while submerged and being pushed, so they drown.
- **Notes:** Very effective because players cannot easily escape the bubble column force.

### Pufferfish Pit
- **Dimensions:** 1x1x2
- **Materials:** 1 magma block, 4 trapdoors, 4 buckets of pufferfish, water
- **Build steps:**
  1. Dig 1x1x1 pit with magma block as the floor
  2. Replace the 4 adjacent blocks at ground level with trapdoors
  3. Open the trapdoors inward (toward the magma, to prevent escape)
  4. Place one pufferfish in each trapdoor opening
  5. Fill the pit with water
- **How it works:** Magma block pulls the victim down (bubble column) and deals fire damage. Pufferfish inflate and deal poison + damage.
- **Notes:** Can be disguised as a secret elevator entrance.

---

## Capture Traps

### Shallow Pitfall (Mob Farm)
- **Dimensions:** 5x5 minimum, 1 block deep
- **Materials:** Fences (for inside edge) OR half-slabs (for outside edge)
- **Build steps:**
  1. Dig a 1-block-deep pit (at least 5x5)
  2. Place fences along the inside edge of the pit
  3. Optional: add water currents leading to a mob grinder
- **How it works:** Fences are 1.5 blocks tall. Mobs can walk in (they see it as ground level), but cannot jump out over the fence height.
- **Notes:** Does not capture spiders (they climb). Mobs exposed to sky will burn during daytime (zombies/skeletons).

### Honeycomb Block Trap
- **Dimensions:** Pit-sized
- **Materials:** 2 sticky pistons, 1 honeycomb block, clock circuit
- **Build steps:**
  1. Wire two sticky pistons to a clock circuit for rapid push/pull
  2. Place honeycomb block between the pistons
- **How it works:** The honeycomb block is rapidly pushed back and forth. Tools do not affect its breaking speed (even with enchantments), so the victim cannot break free.
- **Notes:** Purely a containment trap -- needs to be combined with a killing mechanism.

### Netherite Block Live-Capture Trap
- **Dimensions:** 1x1 shaft from bedrock to surface
- **Materials:** 2+ netherite blocks, 3 pistons, tripwire hooks, string, cobweb, redstone repeaters, pulse shortener, repeater clock
- **Build steps:**
  1. Locate a 1x1 hole at bedrock level
  2. Dig vertical 1x1 shaft to the surface
  3. Build a surface trap that forces the target into the shaft
  4. Place tripwire 10-15 blocks above bedrock
  5. Wire tripwire down to bedrock level with minimal delay
  6. Place netherite block on one bedrock block
  7. Place second netherite block on a different (non-opposite) bedrock block
  8. Place piston adjacent to and facing the first netherite block
  9. Place piston adjacent to and facing the second netherite block
  10. Place a disposable block opposite the first netherite block
  11. Place piston facing the disposable block toward the hole
  12. Remove the disposable block
  13. Wire the tripwire through two repeaters (1-tick and 4-tick delays)
  14. Wire the 1-tick repeater directly to piston #2 (step 9)
  15. Wire the 4-tick repeater through a pulse shortener
  16. Create a basic repeater clock (two 1-tick repeaters)
  17. Wire the pulse shortener output to the clock
  18. Wire one clock output to piston #1 (step 8)
  19. Wire other clock output to piston #3 (step 11)
  20. Place cobweb at the bottom to prevent fall damage
- **How it works:** Pistons repeatedly shift the netherite blocks faster than the victim can break them, trapping the player indefinitely at bedrock level.
- **Notes:** Extremely expensive to build. Target remains trapped until the mechanism is disabled or they die.

---

## Trigger Mechanisms

### Trapped Ore (Observer)
- **Dimensions:** 1x1x3
- **Materials:** 1 observer, 1 ore block, TNT
- **Build steps:**
  1. Place the ore block
  2. Place observer behind/below the ore, facing it
  3. Place TNT behind the observer
- **How it works:** Mining the ore triggers the observer, which fires a pulse that ignites the TNT.
- **Notes:** Observer is visible near the ore if the player looks carefully.

### Redstone Ore Mine
- **Dimensions:** 1x1 surface
- **Materials:** Redstone ore, 1 daylight sensor or observer, TNT
- **Build steps:**
  1. Place redstone ore as part of the floor
  2. Place daylight sensor or observer above the ore (or below, hidden)
  3. Wire to TNT
- **How it works:** Walking on redstone ore causes it to light up (block state change). The daylight sensor or observer detects this and fires the TNT.
- **Notes:** Very hard to detect. Works with light sources or open sky above.

### Furnace Trap (Looting Trigger)
- **Dimensions:** 1x1x3
- **Materials:** 1 furnace, coal/iron/food, 1 comparator, redstone dust, 1 redstone torch, TNT
- **Build steps:**
  1. Fill the furnace with coal, iron, or food
  2. Place comparator leading away from furnace (it outputs signal because furnace has items)
  3. Place a block in front of the comparator
  4. Place redstone torch on the far side of that block (torch is OFF because comparator powers the block)
  5. Run redstone from the torch to TNT
- **How it works:** When a player loots the furnace, the comparator signal drops, the torch turns ON, and the TNT detonates.
- **Notes:** Catches people off-guard because they only expect chest traps.

### Anvil Trap
- **Dimensions:** Porch-width
- **Materials:** 2 iron doors, redstone torches, 2 pressure plates, redstone dust, 2 pistons, 2 anvils
- **Build steps:**
  1. Place 2 iron doors sideways with redstone torches underneath (keeps doors closed)
  2. Place 2 pressure plates in front of the doors
  3. Run redstone dust from the plate area up to the roof
  4. Connect dust to 2 pistons on the roof, each holding an anvil
  5. Create a hole through the roof above the entrance
- **How it works:** Stepping on the plates does NOT open the doors (they are held closed). Instead, the signal goes to the roof pistons, which release the anvils through the hole above.
- **Notes:** Exploits the fact that players almost never look up.

### Invisible Tripwire
- **Dimensions:** 3+ block tall hallway
- **Materials:** 2 tripwire hooks, string, TNT
- **Build steps:**
  1. Create a hallway at least 3 blocks tall
  2. Place tripwire hooks on opposite walls at the 3rd block height
  3. Connect string between hooks
  4. Wire to TNT
- **How it works:** String at the third block level is invisible from ground level. Players who jump trigger it.
- **Notes:** If the victim spots the tripwire hooks, they will likely mine the block to disarm it.

---

## Miscellaneous Traps

### Wither Rose / Sweet Berry Field
- **Dimensions:** Large perimeter
- **Materials:** Wither roses or sweet berry bushes, optional cobwebs, optional soul sand
- **Build steps:**
  1. Plant wither roses or sweet berry bushes in a wide field around your base
  2. Leave a single-block-wide safe path (or build a hidden underground tunnel)
  3. Optional: place cobwebs on top of the plants to slow mobs further
  4. Optional: plant roses on soul sand for speed reduction
- **How it works:** Hostile mobs take constant damage walking through the field. Wither roses apply the Wither effect; sweet berries deal thorns damage and slow.
- **Notes:** Only effective against mobs, not players (players can use a water bucket to clear a path).

### Spike Trap
- **Dimensions:** 1x1x1
- **Materials:** 1 dispenser, arrows (optionally tipped), 1 stone pressure plate
- **Build steps:**
  1. Dig 1x1x1 hole
  2. Place dispenser facing up inside the hole
  3. Fill with arrows
  4. Place stone pressure plate on top
- **How it works:** Stepping on the plate fires an arrow straight up into the victim.
- **Notes:** Use tipped arrows with Harming or Poison for much greater lethality.

---
---

# 2. FLYING MACHINES

## Core Mechanics

- **Piston push limit:** A single piston can push or pull up to 12 blocks total. Extensions bypass this by dividing structure among multiple pistons.
- **Slime blocks vs Honey blocks:** They do NOT stick to each other. Slime blocks are solid (transmit redstone), bounce entities away. Honey blocks are transparent, drag entities along with the machine.
- **Observer mechanics:** Observers detect block updates on their face and output a 1-tick pulse from their back. Two observers facing each other create an oscillating clock.

---

## Java Edition Designs

### Simple Two-Way Engine
- **Dimensions:** ~2x1x3 (compact)
- **Materials:** 2 observers, 2 slime blocks, 2 sticky pistons
- **Build steps:**
  1. Place 2 sticky pistons facing opposite directions
  2. Attach a slime block to each piston head
  3. Place an observer on each slime block, each facing outward
  4. Each observer directly powers a slime block
- **How it works:** Direction depends on which observer is updated first. Updating one observer starts a chain reaction: observer fires, powers slime, piston pushes, other observer detects movement, fires back, repeat.
- **Notes:** A dock with a trapdoor can reverse the machine by covering the incoming observer's face. Total block count must stay under 12.

### Rideable Engine
- **Dimensions:** Compact (14 blocks total)
- **Materials:** 8 slime blocks, 2 honey blocks, 2 sticky pistons, 2 observers
- **Build steps:**
  1. Build the basic two-way engine core
  2. Attach honey blocks to the sides where passengers will ride
  3. Players stand on honey blocks during flight
- **How it works:** Honey blocks drag the player along with the machine (unlike slime blocks which bounce you off).
- **Notes:** Getting on and off requires a separate boarding/docking station.

### Turbo Engine A
- **Dimensions:** 2x2x6
- **Materials:** 14 blocks (specific composition not listed on wiki)
- **Build steps:**
  1. Build the turbo engine frame (2x2x6)
  2. Place a sign as a latch mechanism
  3. Breaking the sign starts the engine
- **How it works:** Uses zero-ticking pistons for maximum speed in Java Edition. The sign acts as a start trigger.
- **Notes:** Same speed as normal flyers in Bedrock Edition (zero-ticking is Java-only). Single direction only.

### Diagonal Engine
- **Dimensions:** Custom (follows rail path)
- **Materials:** Multiple observers, slime blocks, pistons, obsidian (for guide rails)
- **Build steps:**
  1. Build a guide rail out of obsidian (immovable blocks) along the desired path
  2. Construct the engine to move along the slime-block diagonal
  3. Use obsidian barriers on upper levels to guide direction (straight or curved)
- **How it works:** Machine moves diagonally along its slime-block axis. Obsidian rails prevent deviation.
- **Start method:** Activate either top observer via block placement or flint-and-steel.

---

### Driveable Machine A: 2-Way Controllable
- **Dimensions:** 8x4 (collapsed)
- **Materials:** 4 observers, 10 slime blocks, 2 sticky pistons, 2 regular pistons, 4 note blocks, 2 fences, 2 minecarts
- **Build steps:**
  1. Place central observer core
  2. Attach sticky pistons to observers (one at each end, facing outward)
  3. Arrange slime blocks around piston heads
  4. Attach note blocks to observer faces:
     - Rear note block = start (in your travel direction)
     - Front note block = brake
  5. Place fences on the platform, then minecarts on the fences (seating)
- **How it works:** Clicking the rear note block updates the observer, starting the engine in that direction. Spam-clicking the front note block extends a piston that blocks movement, acting as a brake.
- **Notes:** Minecarts provide stable seating to prevent falling through the platform due to server lag.

### Driveable Machine B: 2-Way with Cargo & Roof
- **Dimensions:** 10x6, 2-5 blocks high
- **Materials:** Machine A components + 2 two-way splitter extensions
- **Build steps:**
  1. Build Driveable Machine A as the base
  2. Attach two-way extension #1 for a protective roof
  3. Attach two-way extension #2 for cargo (with two minecarts)
  4. Place optional slabs for passenger shelter
- **How it works:** Extensions carry additional structure (roof, cargo) alongside the main engine. Retract extensions before travel.
- **Notes:** Starred minecart = pilot seat. Retract roof and cargo extensions before moving.

### Driveable Machine C: 2/4-Way Reconfigurable
- **Dimensions:** 8x10, 3 blocks high
- **Materials:** 20 slime blocks, multiple observers and pistons, logs (markers)
- **Build steps:**
  1. Build the east-west engine with dual open-faced observers
  2. Attach cargo bays with minecarts
  3. Position starred pistons (marked with logs below for identification)
  4. Place starred observers facing specific directions
- **Operation (east movement):**
  1. Set fire behind the west observer (using flint and steel)
  2. Sit in the eastern minecart
  3. Click the nearest note block before the fire goes out (this releases the brake)
  4. Fire burning out triggers the observer, starting the engine
  5. Spam the same note block to stop
- **To switch to north-south:** Mine the starred pistons and observers, rotate them a quarter-turn clockwise (still facing outward), replace, and repeat.
- **Notes:** In-field reconfigurable by mining/replacing just four blocks.

### Driveable Machine D: 4-Way Compact
- **Dimensions:** 7x5, 4 blocks high (or 5x5x5 alternate layout)
- **Materials:** 13 observers, 26 slime blocks, 8 sticky pistons, 8 regular pistons, 1 redstone torch, 1 immovable block
- **Build steps:**
  1. Start with two central slime blocks (layers 2-3), at least 2 blocks above ground
  2. Place upper sticky pistons facing outward; use those to position lower pistons facing inward
  3. Add downward-facing observer on top, then four-high slime pillars outside the pistons
  4. Use pillars to place downward observers on layer 1
  5. Extend pillars into T-shapes: top T on two opposing sides, bottom T on the other two
  6. Place regular pistons at T-bar ends facing inward
  7. Add layer-2 observers against pillars, layer-4 observers against T-bars
- **Operation:** Stand on surrounding pistons with redstone torch in hand. Place torch on the observer face corresponding to desired direction to start. Reapply torch to stop.
- **Notes:** Possible to fall through corner holes -- step carefully.

### Driveable Machine E: 4-Way Compact with Honey (Java 1.16+)
- **Dimensions:** 4x4x4
- **Materials:** 4 observers, 4 sticky pistons, 15 honey blocks (+ 4-5 optional), 1 minecart, 1 rail, 1 temporary block
- **Build steps:**
  1. Place all honey blocks and sticky pistons first
  2. Install observers; brake honey block B prevents piston push when powered
  3. Optional: add minecart via temporary block T (place rail, add cart, remove T)
- **Operation:** Stand on northwest honey block (or sit in minecart). Identify piston facing desired direction, update its observer via torch/button on its face.
- **How it works:** Honey blocks drag the player along. Upon hitting an immovable block, the machine changes direction predictably:
  - North -> shifts West
  - West -> shifts North
  - South -> shifts East
  - East -> shifts South
- **Notes:** MUST be built aligned north-facing due to update order mechanics. Does NOT work with slime blocks (honey only). Settles into northwest or southeast corners naturally.

---

## Bedrock Edition Designs

### Simple Engine 1 (Bedrock)
- **Dimensions:** Compact
- **Materials:** 1 observer, 1 redstone block, slime blocks, 1 piston
- **Build steps:**
  1. Place piston facing the travel direction
  2. Attach slime blocks to the piston
  3. Place observer on the slime structure, facing the redstone block
  4. Place redstone block where the observer can detect it
- **How it works:** Observer detects redstone block, powers piston through slime. Piston pushes everything forward, observer detects movement again, cycle repeats.
- **To stop:** Remove the redstone block, or place obsidian in front of the observer.

### Simple Engine 2 (Bedrock)
- **Dimensions:** Narrow and long
- **Materials:** 1 observer, slime blocks, 1 piston, 1 sticky piston
- **Build steps:**
  1. Build with piston at front, sticky piston pulling from rear
  2. Connect via slime blocks with observer detecting movement
- **How it works:** Uses less redstone than other designs. Can push up to 9 blocks on the front end.
- **To reverse:** Move one slime block to the back, swap piston/sticky piston orientation.

### Simple Engine 2 with Trailer (Bedrock)
- **Materials:** Simple Engine 2 base + additional observer, sticky piston per trailer
- **Build steps:**
  1. Build Simple Engine 2
  2. Attach observer + sticky piston to the side of the base engine
  3. Multiple trailers can attach simultaneously (top, bottom, sides)
- **How it works:** Trailers extend cargo capacity without exceeding the 12-block push limit (each piston handles its own section).
- **Notes:** Can be used for TNT duplication, cargo transport, and minecart transport.

---

## Extension Types (Java)

### One-Way Extension
- **Materials:** 1 piston, slime blocks, power source
- **How it works:** Front part powers rear piston. Gap between engine and extension allows independent movement.

### Two-Way Extension
- **Materials:** 1 observer, 1 sticky piston
- **How it works:** Observer powers sticky piston. Direction depends on initial retraction state. Allows cargo to be carried in either direction.

---
---

# 3. QUASI-CONNECTIVITY (QC)

## What Is Quasi-Connectivity?

Quasi-connectivity is a mechanic that allows **pistons**, **dispensers**, and **droppers** to be activated by anything that would activate the space directly above them, even if that space is empty or contains a non-conductive block.

Think of it like the bottom half of a door: anything that activates a door's top half also activates its bottom half. A piston responds to an "invisible ghost block" one block above it.

**Affected blocks:** Pistons (normal and sticky), Dispensers, Droppers.
**NOT affected:** Crafters (despite similarity to dispensers/droppers).

## The Ghost Block Concept

Imagine an invisible mechanism component occupying the space directly above the piston. Any redstone signal that would power that invisible block will also activate the piston below. This is the "activation zone" extending one block upward.

## Two Types of QC Activation

### Type 1: Immediate QC Activation

Some redstone components update blocks up to two spaces away (taxicab distance), allowing them to both power the ghost block AND send an update to the piston simultaneously.

**Components capable of immediate QC:**
- Redstone torches
- Redstone dust
- Redstone repeaters
- Redstone comparators
- Buttons, levers, pressure plates, weighted pressure plates, detector rails, trapped chests

**Example -- Dust line above a piston:**
```
[Dust]---[Dust]---[Dust]
          |
       [Block]
          |
       [Piston]
```
When the dust powers up:
1. Dust has a two-block update range
2. It activates the block space above the piston (QC activation)
3. It also sends an update directly to the piston (within 2 blocks)
4. Piston extends immediately -- no delay

### Type 2: Update-Based QC Activation

When a redstone component is too far away to send an update signal to the piston, it can still power the ghost block. But the piston will NOT activate until it receives a separate block update from something else.

**Components that cause update-based QC:**
- Powered blocks (activated by buttons, levers, repeaters, comparators, dust)
- Redstone blocks (permanent power, moved via pistons)
- Buttons/levers/tripwire hooks attached to the sides of blocks

**Example -- Powered block too far from piston:**
```
[Lever] --> [Powered Block]    (2+ blocks from piston)
                 |
              [Air]
                 |
              [Piston]
```
When the lever is activated:
1. Lever powers the block
2. Powered block would activate the ghost space above the piston
3. BUT the piston does not know it is powered (no update reached it)
4. Piston only extends when something else sends it an update (e.g., block placed/broken nearby, repeater changing state)

## Practical Examples

### Torch Key (Hidden Door)
Place a redstone torch in a specific location above ground level. The torch immediately QC-activates a hidden piston beneath the surface, triggering a secret door. Works because redstone torches provide both QC power and updates within range.

### Block Update Detector (BUD)
A piston in "update-based QC state" (powered via ghost block but not yet updated) will extend when any adjacent block changes. This makes it a detector for block updates -- any change nearby (crop growing, water flowing, block placed) triggers the piston.

**Build:**
1. Power a piston via QC (e.g., powered block above)
2. Ensure no update reaches the piston
3. The piston is now "primed" -- it will fire on the next block update it receives

### Compact Piston Doors
QC allows piston doors to be more compact because the activation mechanism can be positioned above or behind the door rather than directly adjacent to every piston.

## Common Pitfalls

### Problem: Running Redstone Over Pistons
Running redstone dust directly over a piston will accidentally activate it via QC. You cannot fix this with a top slab either.

### Solution 1: Go Up One Block
```
    [Dust on top slab]
           |
       [Full Block]
           |
      [Piston]   (not activated -- dust is now 2 blocks up)
```
Raise the dust line one block higher using a top slab (non-conductive) so the dust no longer sits in the ghost block position.

### Solution 2: Use a Repeater as Insulation
```
    [Repeater facing away] -->
           |
       [Block]
           |
      [Piston]   (not activated)
```
Repeaters and comparators only update in the direction they face. A repeater facing away from the piston will not send an update to it. Adds 2+ ticks of delay.

### Solution 3: Move a Cauldron Past a Comparator
Use a piston to move a cauldron past a comparator. The comparator outputs a signal without directly powering the ghost block above your piston. Adds 2-4 ticks of delay.

## Key Takeaways

1. QC extends the activation range of mechanism components by exactly one block upward
2. Immediate QC works automatically; update-based QC requires a separate block update
3. QC is an official feature, not a bug ("works as intended")
4. Always be aware of QC when routing redstone near pistons, dispensers, or droppers
5. QC enables creative builds (hidden doors, BUDs, compact contraptions) when used intentionally

---
---

# 4. HOPPER MECHANICS AND CIRCUITS

## Basic Hopper Behavior

- **Transfer rate:** 2.5 items per second (1 item every 8 game ticks)
- **Cooldown:** 0.4 seconds (8 game ticks) after each transfer
- **Priority:** Hoppers search for input items BEFORE outputting to containers
- **Locking:** Hoppers lock when powered by any redstone signal. When locked, they cannot pull or push items.
- **Direction:** Hoppers pull from the container above and push into the container they point at.

---

## Item Sorter Designs

### Basic Hopper Item Sorter
- **Dimensions:** 1-wide, tileable
- **Transfer rate:** 2.5 items/second
- **Materials:** ~10 redstone dust components
- **Build steps:**
  1. Place a top hopper (the filter hopper) in the item stream
  2. Load the filter hopper with: 41 of the target item + 4 different stackable junk items (1 each in the remaining slots)
  3. Place a bottom hopper below the filter hopper
  4. Wire the bottom hopper to lock when the filter hopper has low signal strength
  5. Point the bottom hopper into a chest (sorted output)
- **How it works:** When the filter hopper fills with enough target items, the comparator output reaches signal strength 3, which unlocks the bottom hopper. The bottom hopper then pulls excess target items down into the sorted chest. The 41+4 configuration ensures only the correct items pass through.
- **Notes:** The 4 junk items must be different stackable items, 1 per slot. Signal strength of 3 is the threshold that unlocks the bottom hopper without affecting adjacent sorter modules.

### Double-Speed Hopper Sorter
- **Dimensions:** 1-wide, tileable
- **Transfer rate:** 5 items/second
- **Materials:** ~10 redstone dust components
- **Build steps:**
  1. Stack two filter hoppers vertically
  2. Top hopper: 41 of target item + 4 different stackable junk items
  3. Second hopper: 64 of target item + 4 different stackable items (different from top hopper junk)
  4. Wire both hoppers with the same comparator logic
- **How it works:** Dual-hopper stacking doubles the throughput by processing items through two filters simultaneously.

### Compact Hopper Sorter
- **Dimensions:** 1-wide, tileable (narrower than basic)
- **Transfer rate:** 2.5 items/second
- **Materials:** ~9 redstone dust components
- **Build steps:**
  1. Place filter hopper with: 1 target item + 21 cheap stackable items
  2. For 16-stack materials: 1 target item + 15 cheap items
  3. Remove the center column (compared to basic design)
- **How it works:** Same comparator-based filtering but with a smaller footprint.
- **Notes:** NO overflow protection. If the system backs up, items can leak into wrong channels.

---

## Hybrid Sorter Designs

### Hybrid Sorter h-A & h-B
- **Dimensions:** Alternating ABABAB pattern, tileable
- **Transfer rate:** 2.5 items/second
- **Materials:** ~23 redstone dust components per A+B pair
- **Redstone delay:** h-A = 3 ticks, h-B = 4 ticks
- **Hopper setup:**
  - Filter hoppers contain: 1 target item + 21 cheap items each
  - "F" = filter hopper, "O" = output hopper
- **How it works:** Alternating circuit designs provide complete isolation between adjacent sorter modules, preventing signal bleed.
- **Notes:** More expensive per slot but eliminates inter-module interference.

### Resource-Optimized Hybrid (OH) Type I & II
- **Materials Type I:** 12 redstone torches + 7-10 dust
- **Materials Type II:** 2 comparators + 2 repeaters + 2 torches + 5-6 dust (19-20 RSD total)
- **Redstone delay:** 4 ticks
- **Filter hopper contents:**
  - 64-stack items: 2 target items + 20 cheap items
  - 16-stack items: 2 target items + 14 cheap items
- **Notes:** Supports an optional master on/off circuit for the entire array. Floating blocks maintain circuit isolation.

### OH Type III
- **Materials:** 17 redstone dust components per A+B pair
- **Redstone delay:** 4 ticks
- **Build notes:**
  - Uses composters on the hopper pipe to reduce lag
  - Furnace above second pipe (optional for multi-line stacking)
  - Stone slabs can be replaced with solid blocks
- **Setup requirement:** Any oh3-B filter hopper can ONLY be filled after at least one neighboring oh3-A has been initialized first.
- **Overflow behavior:** When oh3-A overflows, it locks adjacent oh3-B tiles. They retain items but cannot output until resolved.

### OH Type IV
- **Materials:** 16 redstone dust components per pair
- **Redstone delay:** 4 ticks
- **Notes:** Prone to redstone torch burnout in Java 1.18+ under sustained 2.5 ips load. A/B tiles are completely isolated and can operate independently.

### OH Type V
- **Materials:** 23 redstone dust components per pair
- **Redstone delay:** Flexible (3-6 ticks)
- **Compatible with:** Java 1.18+ and Bedrock Edition
- **Features:**
  - All torches protected by repeaters (no burnout risk)
  - Supports double-hopper speed (5 items/second)
- **Double-speed setup:** Full stack in first filter hopper slot + different filler items in slots 2-5. Minimum 18 items total for lag safety.

---

## Special Item Filters

### Unstackable Item Filter
- **Dimensions:** 1-wide, silent
- **Transfer rate:** 2.5 items/second
- **Materials:** 3 hoppers (A, B, C)
- **Build steps:**
  1. Hopper A: input hopper (receives all items)
  2. Hopper B: output hopper (locked normally, unlocks only for unstackable items)
  3. Hopper C: optional safety hopper for overflow
- **How it works:** Unstackable items (potions, tools, etc.) generate a different signal strength than stackable items. This difference unlocks hopper B selectively.
- **Notes:** Tileable versions available for both Java and Bedrock.

### Potion / Book / Shulker Box Filter
- **Dimensions:** 1-wide, silent
- **Transfer rate:** 2 items/second
- **Circuit delay:** 5 redstone ticks
- **Materials:** Hoppers, brewing stand / chiseled bookshelf / shulker box (as selective container), redstone repeater (3-tick delay)
- **Build steps:**
  1. Hopper A: input
  2. Hopper B: allowed items output
  3. Hopper C: restricted items output
  4. Place the selective container (brewing stand accepts only potions, chiseled bookshelf accepts only books, shulker box accepts anything)
  5. Wire with repeater on 3-tick delay
- **How it works:** The selective container only accepts specific item types. Items that don't fit bypass to the restricted output.

---

## Hopper Clocks

### Looped Hopper Clock
- **Output:** 4 ticks ON, 12 ticks OFF
- **Period:** 16 ticks total
- **Build steps:**
  1. Chain 4 hoppers in a loop (each pointing to the next)
  2. Place 1 item in any hopper
  3. Attach a comparator to one hopper to detect when the item passes through
- **How it works:** The single item circulates through the 4-hopper loop. Each time it passes the comparator's hopper, a pulse is output.
- **Adjustability:** Add or remove hoppers to change the period. Add more items to change the ON duration.

### Delayed Hopper Clock
- **Period range:** 40 ticks to 256 seconds
- **Build steps:**
  1. Place 2 hoppers facing each other
  2. Load exactly 5 stacks of stackable items into one hopper
  3. Place a redstone torch that activates when the source hopper empties
- **How it works:** Items transfer from one hopper to the other. When the source empties, the torch activates, which locks the destination and unlocks the source (reversing flow). Cycle repeats.
- **Adjustability:** Reduce the number of stacks to shorten the period. 5 stacks = maximum duration.

---

## Item Counter
- **Dimensions:** 1x5x4
- **Transfer rate:** 1.25 items/second
- **Build steps:**
  1. Place a dropper above a hopper
  2. Wire the dropper to fire items into the hopper
  3. Attach a comparator to the hopper to detect each item
  4. Each item passing through generates a short redstone pulse
- **How it works:** The dropper fires items one at a time. The comparator detects each arrival, outputting a countable pulse.
- **Notes:** Compatible with scoreboards and command blocks for automated quantity tracking.

---

## Item Transportation Methods

### Hopper Pipe
- Chain of hoppers, each pointing into the next
- Reliable but very iron-expensive (5 iron + 1 chest per hopper)
- Bedrock Edition: small percentage of items may skip filters at full throughput

### Item Streams (Water-Based)
- Water flowing over hoppers with items dropped via dropper
- Use ice blocks and non-flowing blocks (signs, fence gates, slabs, trapdoors) to carry items across gaps
- Cheaper than hopper pipes (especially with Silk Touch for ice)
- Risk: too many items passing a filter simultaneously may cause sorting failures

### Minecart Transport
- Hopper-minecarts or chest-minecarts on rails above filter hoppers
- Most reliable method but significantly slower than pipes or streams

---

## Bedrock Edition Adjustments

- Hopper pipes at full load may push a percentage of items past filters
- With 21 items in the filter, the system tends to run the single-item filter through as well
- Recommended: 20 items for the B filter (14 items for 16-stack materials)
- Named junk items prevent accidental sorting of identical items into the wrong channel

---
---

# 5. TNT CANNONS

*Note: The Minecraft Wiki's TNT cannon tutorial pages are structured as classification taxonomies rather than build guides. The subpages (Manual, Automatic, Damage Types) contain category descriptions without step-by-step build instructions. Below is a synthesis of the core mechanics and a practical basic cannon design derived from the technical data available.*

## Core TNT Mechanics

- **Fuse time:** 80 game ticks (4 seconds) when activated by redstone or fire. 10-30 ticks (0.5-1.5 seconds) when activated by another explosion.
- **Explosion power:** 4.0 (default)
- **Entity spawn offset:** When ignited, primed TNT spawns at +0.5, +0.0, +0.5 from the block's corner position
- **Initial velocity:** 0.02 blocks/tick in a random horizontal direction, 0.2 blocks/tick upward
- **Entity size:** 0.98 x 0.98 blocks
- **Gravity:** Yes, TNT entities are affected by gravity
- **Water interaction (Java):** TNT cannot destroy blocks underwater. Exception: if a gravity block (sand, gravel) is on top of the TNT when it detonates.
- **Water interaction (Bedrock):** TNT cannot destroy underwater blocks under any circumstances.

## Cannon Terminology

- **Charge TNT (Propellant/Booster):** TNT that explodes in water to generate force without destroying blocks. The explosion pushes the projectile.
- **Projectile TNT:** The TNT that gets launched. Placed so it is NOT in water, allowing it to be pushed by the charge explosion.
- **Launch point:** Where the charge TNT explodes. Can be on a platform (on blocks) or ejector-style (mid-air).
- **Water containment:** Water placed over charge TNT prevents block damage while still transferring the explosion's kinetic energy to the projectile.

## Cannon Categories (from Wiki taxonomy)

### By Loading Method
| Type | Description |
|------|-------------|
| **Manual** | All TNT placed by hand. Subtypes: Underfoot, Overhead, Crossbow, Sustainable, Buffer, Semi-auto |
| **Preloaded** | A manual cannon pre-loaded and activated once automatically |
| **Machine Gun** | Preloaded crossbow variant, fires up to 1 shot per tick |
| **Duper** | Uses TNT duplication glitches (common in survival) |
| **Dispenser** | Uses dispensers to supply TNT (for servers banning duping) |

### By Damage Pattern
| Type | Description |
|------|-------------|
| **Shotgun** | Multiple projectiles in a spread pattern |
| **Ripple** | Sequential detonations across a line |
| **Mortar** | Arcing trajectory, limited to ~20 blocks depth for downward damage |
| **Scatter** | Wide-area dispersal |
| **Tunnler** | "The most effective in a lot of situations" -- bores tunnels through structures |
| **Nuke** | Maximum single-point destruction |
| **Multi-impact** | Multiple hits on the same target |

### By Trajectory
| Type | Description |
|------|-------------|
| **Straight** | Unguided after leaving cannon (Ascend, Descend, Central, Shift, Artillery) |
| **Mid-air maneuvering** | Uses injector TNT that explodes near projectiles in flight to alter course |

### Special Purpose Variants
- **Pearl cannons:** Launch ender pearls for player teleportation over vast distances
- **Arrow launchers:** TNT-accelerated arrows can one-shot any entity without Totem of Undying
- **Sand cannons:** Launch falling blocks; towers form up to the height of their velocity (rounded up)
- **Player cannons:** Launch players hundreds to tens of thousands of blocks
- **Piercing cannons:** Penetrate through shielding
- **Instant cannons:** Fire without fuse delay

## Practical Basic Cannon Design

### Simple Water-Trough Cannon
- **Dimensions:** 7x3x2 (LxWxH)
- **Materials:** ~20 solid blocks (any blast-resistant material; obsidian ideal), 1 water bucket, 1 redstone dust, 1 repeater (set to 4 ticks), 1 button, 6+ TNT per shot
- **Build steps:**
  1. Build a trough (channel) 7 blocks long, 1 block wide, 1 block deep out of solid blocks
  2. Place walls 1 block high on both long sides of the trough
  3. Place water at the far end of the trough (opposite from where you will fire). Let it flow toward the open end but stop it 1 block short of the end using a half-slab or sign
  4. At the open (dry) end, leave 1 block of dry trough floor -- this is the projectile position
  5. Behind the trough (far end, behind the water source), place a button
  6. Run redstone dust from the button along the outside wall
  7. Place a repeater in the redstone line, set to 4 ticks delay, positioned so it delays the signal reaching the projectile end
  8. Branch the redstone to reach under the water-covered section (charge TNT positions) AND the dry end (projectile position) with the repeater delaying the projectile side
  9. **To fire:** Place 4-5 TNT in the water (charge), place 1 TNT on the dry block (projectile), press the button
- **How it works:** The button ignites the charge TNT (in water) first. Water absorbs the block damage from the charge explosion. 4 ticks later, the projectile TNT is ignited. The charge explodes, pushing the still-intact projectile TNT out of the cannon. The projectile flies through the air and explodes on impact area.
- **Notes:**
  - More charge TNT = more range (but diminishing returns past ~5)
  - The 4-tick delay on the repeater is critical: the charge must explode BEFORE the projectile, but the projectile must be ignited before the charge goes off so it becomes an entity that can be pushed
  - All charge TNT must be submerged in water or the cannon destroys itself
  - The projectile must NOT be in water or it will not deal block damage on landing
  - Range: approximately 30-60 blocks with 4-5 charges

### Key Timing Principle
The fundamental timing equation for any TNT cannon:
1. **Charge TNT** is ignited first (t=0)
2. **Projectile TNT** is ignited with a delay (typically 4 ticks / 0.2 seconds later)
3. Charge TNT explodes at t=80 ticks, pushing the projectile (which was ignited at t=4 and has 76 ticks remaining on its fuse)
4. Projectile flies through the air and explodes 76 ticks after launch

If the projectile is ignited too early, it explodes inside the cannon. If too late, the charge explosion pushes an un-ignited TNT block (which just drops as an item). The delay must ensure the projectile is a primed entity (ignited) when the charge detonates.

## Advanced Techniques (Referenced)

- **Lazy Acceleration:** Projectiles in lazy-loaded chunks accumulate acceleration from propellants without the entity ticking down its fuse, enabling extreme range with fewer TNT.
- **TNT Duping:** Exploits block duplication glitches to provide unlimited TNT from a single source block. Common in survival applications where TNT is expensive.
- **Accuracy improvement:** Rebounding TNT or shooting straight forward achieves very high accuracy. Pixel-precision and subpixel-precision alignment techniques exist for competitive play.
- **Shielding/Armor:** Defensive structures using high blast-resistance blocks. Counter-types include ATOX, Pergola, Spikes, Heavy, Layered, and Active shielding.

---
---

# APPENDIX: Quick Reference

## Trap Effectiveness Tiers

| Tier | Traps | Notes |
|------|-------|-------|
| **Instant Kill** | Instant Landmine (End Crystal), TNT Floor House, Warehouse Trap | No escape time |
| **High Lethality** | Fake Water Pitfall (30+ blocks), Fake Elevator, Lava Staircase | Requires specific depth/setup |
| **Containment** | Netherite Live-Capture, Honeycomb Trap, Fake Water Elevator (drowning) | Traps without immediate kill |
| **Deterrent** | Wither Rose Field, Shallow Pitfall, Spike Trap | Area denial / mob farming |

## Flying Machine Speed Reference (Java Edition)

| Type | Speed | Direction Control |
|------|-------|-------------------|
| Simple Two-Way | Normal | 2-way (update-dependent) |
| Turbo Engine A | Maximum (zero-tick) | 1-way only |
| Driveable A | Normal | 2-way (note block control) |
| Driveable D | Normal | 4-way (torch control) |
| Driveable E (Honey) | Normal | 4-way (torch/button, 4x4x4) |

## Hopper Sorter Comparison

| Design | Speed | Materials (RSD) | Overflow Safe | Edition |
|--------|-------|-----------------|---------------|---------|
| Basic | 2.5 ips | 10 | Yes | Both |
| Double-Speed | 5 ips | 10 | Yes | Both |
| Compact | 2.5 ips | 9 | No | Both |
| OH Type III | 2.5 ips | 17 | Partial | Both |
| OH Type V | 5 ips | 23 | Yes | Both (1.18+) |
