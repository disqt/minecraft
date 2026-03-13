# Simple Hidden Piston Entrance

Great choice for a first redstone project! A hidden piston door is one of the most satisfying things to build -- your base entrance looks like a normal wall until you flip a lever, and then part of the wall slides away to reveal a secret passage.

## What We're Building

A **1-wide, 2-tall hidden entrance** in a wall. From the outside, it looks like a completely normal stone wall. When you flip a lever (which you can hide behind a painting), two stone blocks slide sideways into the wall, revealing a doorway you can walk through.

**Difficulty:** Easy
**Dimensions:** 5 wide x 4 deep x 4 tall
**Works in:** Minecraft Java Edition (uses quasi-connectivity, will not work in Bedrock)

## Materials List

| Material | Count | How to Get |
|----------|-------|------------|
| Stone | 20 | Smelt cobblestone in a furnace |
| Cobblestone | 1 | Mine any stone |
| Sticky Piston | 2 | 3 wood planks + 4 cobblestone + 1 iron + 1 redstone + 1 slimeball |
| Redstone Dust | 4 | Mine redstone ore (y-level -64 to 15) with iron pickaxe or better |
| Redstone Torch | 1 | 1 redstone dust + 1 stick |
| Repeater | 1 | 3 stone + 2 redstone torches + 1 redstone dust |
| Lever | 1 | 1 stick + 1 cobblestone |

**Total: about 30 blocks.** Very achievable in early survival.

## How to Build It

**Face east before you start building.** The door will open to your left (north) and the lever will be on the wall face in front of you. In the layer viewer (see the HTML file), north is the top of the grid and east is the right side.

### Layer 1 (Y=0) -- Ground Level

This is the floor of your hidden entrance. Build a 5-wide, 3-deep rectangle of stone for the wall structure. Leave two air gaps in the middle row (row 1) on either side of the sticky piston -- the piston needs room to retract.

- The sticky piston at row 1, column 2 faces **east**. This is one of your two door pistons (the bottom one).
- The air gaps at columns 1 and 3 (same row) are the cavity the piston arm moves through.
- Row 0 is the back of the wall. Row 2 is the front wall face. Row 3 is open air where you stand.

### Layer 2 (Y=1) -- Top Piston Level

Same layout as Layer 1, but with two additions:

- A **cobblestone block** at row 0, column 1. This is the block the redstone torch attaches to. I used cobblestone so you can tell it apart from the stone, but you can use any opaque block.
- A **redstone torch** at row 1, column 1. Place this on the **south face** of the cobblestone block above. The torch sits in the air gap next to the piston.
- A second **sticky piston** at row 1, column 2, facing **east** (same as the bottom one).

The redstone torch provides constant power to the top piston (Y=1) directly, since it's adjacent. The bottom piston (Y=0) gets powered through **quasi-connectivity** -- a Java Edition mechanic where pistons respond to power sources that would power the block space directly above them. Since the top piston's space is powered by the torch, the bottom piston detects this and activates too.

### Layer 3 (Y=2) -- Solid Wall Above the Door

This layer is entirely stone. It forms the wall above the 2-tall doorway. No redstone here -- just fill in the full 5x3 rectangle of stone matching the footprint of layers 1 and 2 (rows 0-2, columns 0-4).

### Layer 4 (Y=3) -- Wiring on Top

This is where the lever signal reaches the torch. Only the middle section has blocks:

1. Place **redstone dust** at row 2, column 2 (on top of the wall face).
2. Place **redstone dust** at row 1, column 3 (on top of the wall structure).
3. Place a **repeater** at row 1, column 2, **facing west** (output pointing toward column 1). Right-click the repeater once to set it to 2-tick delay.
4. Place **redstone dust** at row 1, column 1 (on top of the cobblestone block from Layer 2).
5. Place a **lever** at row 3, column 2. This goes on the **north face** of the wall (the side facing the player).

## How It Works

Here's the signal path, step by step:

1. **Lever OFF (default state):** The redstone torch is ON, providing signal strength 15. It powers the top sticky piston directly (adjacent block). The bottom sticky piston is powered via quasi-connectivity. Both pistons are **extended**, pushing two stone blocks east into the wall face. The wall looks solid.

2. **You flip the lever ON:** The lever sends a signal through the redstone dust on top of the wall. The dust travels to the repeater, which carries it to the dust sitting on the cobblestone block. This powers the cobblestone block.

3. **Torch turns OFF:** The redstone torch is attached to the cobblestone block. When its attachment block is powered, a torch turns off -- this is called a **NOT gate** or **inverter**. It's the most fundamental redstone circuit.

4. **Pistons retract:** With the torch off, both pistons lose power. Sticky pistons pull the block in front of them when they retract. The two door blocks slide east-to-west (back into the wall cavity), revealing a 1-wide, 2-tall opening.

5. **Flip the lever OFF again** to close the door. The torch turns back on, pistons extend, blocks slide back into the wall.

## Key Concepts Explained

### What's a NOT gate?
A NOT gate (or inverter) flips the signal: input ON = output OFF, and vice versa. A redstone torch on a block is the simplest NOT gate. Power the block = torch turns off.

### What's quasi-connectivity?
In Java Edition, pistons, dispensers, and droppers can be activated by anything that would power the space **one block above them** -- even if nothing is directly touching them. This is why one torch can power two stacked pistons. The top piston is directly adjacent to the torch. The bottom piston checks: "would the block above me be powered?" -- and since the top piston IS powered by the torch, the answer is yes.

**Important:** The bottom piston only responds when it receives a "block update" -- a notification that something nearby changed. It gets this update when the top piston moves. So you'll see the top piston move a split second before the bottom one. This is normal and expected.

### Why the repeater?
The repeater serves two purposes:
1. It **resets the signal to full strength** (15), ensuring the torch block receives enough power.
2. It acts as a **one-way valve** (diode), preventing the torch's signal from feeding back into the lever circuit.

## Common Mistakes

- **Piston facing the wrong way:** Both sticky pistons must face **east** (toward the right side of the grid). If they face the wrong direction, the door blocks won't move correctly.
- **Torch on the wrong block:** The torch must be on the **south face of the cobblestone block**, not on top of it. If it's on top, it won't be adjacent to the piston and the circuit won't work.
- **Using regular pistons instead of sticky:** Regular pistons push blocks but don't pull them back. You need **sticky** pistons (crafted with a slimeball) so the door blocks return when the pistons retract.
- **Forgetting to set the repeater delay:** The repeater should be set to 2 ticks (one right-click after placing). This ensures clean timing.
- **Building on Bedrock Edition:** This design relies on quasi-connectivity, which is a Java-only mechanic. On Bedrock, the bottom piston won't fire and you'd need to wire it separately.

## Hiding the Lever

The lever sticking out of the wall is a giveaway. Here are some ways to hide it:

1. **Painting trick:** Place the lever first, then place a painting over it. You can still right-click the lever through the painting.
2. **Item frame:** Place an item frame next to the lever with a decorative item to draw attention away.
3. **Behind a bookshelf:** If your wall uses bookshelves, the lever blends in among the shelf edges.

## Testing It

I recommend building this in a **creative mode test world** first:

1. Create a new world: Creative mode, Superflat preset
2. Build the four layers following the guide
3. Place the two door blocks in front of the extended piston heads (they should be at columns 3 in the wall face once the pistons extend)
4. Flip the lever and watch the blocks retract
5. Once it works, count your materials and build it for real in survival

Open the **hidden-piston-entrance.html** file in your browser for an interactive layer-by-layer view of the build. You can click through each layer, hover over blocks to see what they are, and toggle the "ghost layer" checkbox to see the layer below for reference.
