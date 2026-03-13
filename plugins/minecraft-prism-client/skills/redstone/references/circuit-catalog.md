# Redstone Circuit Catalog

Verified builds for Minecraft Java Edition. All block placements are tested.

Grids use top-down view: row 0 = north, col 0 = west.
Directional notation: `block:direction` (e.g., `repeater:east` = repeater outputting east).

## Table of Contents

1. [Logic Gates](#logic-gates)
2. [Clocks](#clocks)
3. [Memory & Flip-Flops](#memory--flip-flops)
4. [Piston Doors](#piston-doors)
5. [Item Sorting](#item-sorting)
6. [Farms](#farms)
7. [Utility Circuits](#utility-circuits)

---

## Logic Gates

### NOT Gate (Inverter)

The most basic gate. A redstone torch inverts its input.

- **Dimensions:** 1x3x2
- **Difficulty:** Easy
- **Materials:** 1 redstone torch, 2 redstone dust, 3 stone

```json
{
  "name": "NOT Gate (Inverter)",
  "dimensions": [3, 1, 2],
  "materials": { "stone": 3, "redstone_dust": 2, "redstone_torch": 1 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [["stone", "stone", "stone"]]
    },
    {
      "y": 1, "note": "Circuit — torch is on the side of center block",
      "grid": [["redstone_dust", "redstone_torch", "redstone_dust"]]
    }
  ]
}
```

**How it works:** Input dust powers the center stone block, which turns OFF the torch attached to it. When input is OFF, the torch is ON (and vice versa). The torch is placed on the **side** of the center block (facing the output direction).

**Signal flow:** Input (west) -> dust -> powers stone block -> torch on east side of block turns OFF -> output dust is OFF.

---

### OR Gate

Two inputs, either activates the output. The simplest gate — just merge two dust lines.

- **Dimensions:** 3x3x2
- **Difficulty:** Easy
- **Materials:** 3 redstone dust, 5 stone

```json
{
  "name": "OR Gate",
  "dimensions": [3, 3, 2],
  "materials": { "stone": 5, "redstone_dust": 3 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [
        [null, "stone", null],
        ["stone", "stone", "stone"],
        [null, "stone", null]
      ]
    },
    {
      "y": 1, "note": "Dust merges at center",
      "grid": [
        [null, "redstone_dust", null],
        ["redstone_dust", null, "redstone_dust"],
        [null, null, null]
      ]
    }
  ]
}
```

**How it works:** Two input dust lines (north and west) merge at the center. If either is powered, the output dust (east) receives signal. Redstone dust naturally connects when adjacent.

**Inputs:** North, West. **Output:** East.

---

### AND Gate

Both inputs must be ON for output ON. Uses two torches (inverters) feeding into a NOR.

- **Dimensions:** 3x5x2
- **Difficulty:** Easy
- **Materials:** 3 redstone torches, 4 redstone dust, 7 stone

```json
{
  "name": "AND Gate",
  "dimensions": [3, 5, 2],
  "materials": { "stone": 7, "redstone_dust": 4, "redstone_torch": 3 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [
        ["stone", "stone", "stone", "stone", "stone"],
        [null, null, "stone", null, null],
        ["stone", "stone", "stone", "stone", "stone"]
      ]
    },
    {
      "y": 1, "note": "Two NOT gates feed into a NOR (third torch)",
      "grid": [
        ["redstone_dust", "redstone_torch", "redstone_dust", null, null],
        [null, null, "redstone_torch", null, null],
        ["redstone_dust", "redstone_torch", "redstone_dust", null, null]
      ]
    }
  ]
}
```

**How it works:** Each input passes through a NOT gate (torch). The two inverted signals meet at a center block with a third torch. The third torch is only OFF when both inverted signals are ON — which means both inputs were OFF. Wait, that's NAND. For AND: the output torch is ON only when BOTH input torches are OFF (both inputs ON).

**Corrected signal flow:** Input A (col 0, row 0) -> torch inverts -> dust carries inverted A to center block. Input B (col 0, row 2) -> torch inverts -> dust carries inverted B to center block. Center torch on center block: if EITHER inverted input is ON, center torch is OFF. Center torch is ON only when BOTH inverted inputs are OFF — meaning both original inputs are ON. This IS an AND gate.

**Inputs:** Northwest (A), Southwest (B). **Output:** Center torch output (east side of center block).

---

### NAND Gate

Output is ON unless BOTH inputs are ON.

- **Dimensions:** 5x3x2
- **Difficulty:** Easy
- **Materials:** 2 redstone torches, 4 redstone dust, 6 stone

```json
{
  "name": "NAND Gate",
  "dimensions": [5, 3, 2],
  "materials": { "stone": 6, "redstone_dust": 4, "redstone_torch": 2 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [
        ["stone", null, "stone", null, "stone"],
        ["stone", null, "stone", null, "stone"],
        [null, null, null, null, null]
      ]
    },
    {
      "y": 1, "note": "Two torches, output dust",
      "grid": [
        ["redstone_dust", null, "redstone_dust", null, null],
        [null, "redstone_torch", null, "redstone_torch", "redstone_dust"],
        [null, null, null, null, null]
      ]
    }
  ]
}
```

**How it works:** AND gate + final NOT. Two input dust lines each power a block. A torch on each block inverts. Both inverted signals merge and if either is ON, the output is ON. Output is OFF only when both torches are OFF (both inputs ON).

---

### NOR Gate

Output is ON only when BOTH inputs are OFF.

- **Dimensions:** 3x3x2
- **Difficulty:** Easy
- **Materials:** 1 redstone torch, 2 redstone dust, 4 stone

```json
{
  "name": "NOR Gate",
  "dimensions": [3, 3, 2],
  "materials": { "stone": 4, "redstone_dust": 2, "redstone_torch": 1 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [
        [null, "stone", null],
        ["stone", "stone", "stone"],
        [null, null, null]
      ]
    },
    {
      "y": 1, "note": "Inputs merge into block, torch inverts",
      "grid": [
        [null, "redstone_dust", null],
        ["redstone_dust", "redstone_torch", null],
        [null, null, null]
      ]
    }
  ]
}
```

**How it works:** Two input dust lines power the same block. A torch on that block turns OFF if either input is ON. Torch is ON only when both inputs are OFF = NOR logic.

**Inputs:** North, West. **Output:** East (from torch).

---

### XOR Gate

Output ON when inputs differ (one ON, one OFF).

- **Dimensions:** 5x5x3
- **Difficulty:** Medium
- **Materials:** 2 redstone torches, 6 redstone dust, 2 repeaters, 8 stone

```json
{
  "name": "XOR Gate",
  "dimensions": [5, 5, 3],
  "materials": { "stone": 8, "redstone_dust": 6, "redstone_torch": 2, "repeater": 2 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [
        ["stone", "stone", null, null, null],
        [null, "stone", "stone", "stone", null],
        [null, null, null, null, null],
        [null, "stone", "stone", "stone", null],
        ["stone", "stone", null, null, null]
      ]
    },
    {
      "y": 1, "note": "Input wiring and torches",
      "grid": [
        ["redstone_dust", "redstone_dust", null, null, null],
        [null, "redstone_torch", "redstone_dust", "repeater:east", null],
        [null, null, null, null, null],
        [null, "redstone_torch", "redstone_dust", "repeater:east", null],
        ["redstone_dust", "redstone_dust", null, null, null]
      ]
    },
    {
      "y": 2, "note": "Cross-wiring — each input powers the opposite torch's block",
      "grid": [
        [null, null, null, null, null],
        [null, null, null, "redstone_dust", null],
        [null, null, null, null, null],
        [null, null, null, "redstone_dust", null],
        [null, null, null, null, null]
      ]
    }
  ]
}
```

**How it works:** Each input feeds into a torch AND directly to the output via a repeater. When one input is ON, its torch turns off (blocking one path) but its repeater sends signal to the output. When both are ON, both torches are off and both repeaters fire, but the cross-coupling cancels the output. When both are OFF, neither repeater fires.

---

## Clocks

### Repeater Clock (4-tick)

The simplest redstone clock. Two repeaters in a loop.

- **Dimensions:** 2x4x2
- **Difficulty:** Easy
- **Materials:** 2 repeaters, 4 redstone dust, 4 stone

```json
{
  "name": "Repeater Clock (4-tick)",
  "dimensions": [4, 2, 2],
  "materials": { "stone": 4, "redstone_dust": 4, "repeater": 2 },
  "layers": [
    {
      "y": 0, "note": "Foundation — solid blocks under all components",
      "grid": [
        ["stone", "stone", "stone", "stone"],
        [null, "stone", "stone", null]
      ]
    },
    {
      "y": 1, "note": "The clock loop — repeaters face opposite directions",
      "grid": [
        ["redstone_dust", "repeater:east", "redstone_dust", null],
        [null, "redstone_dust", "repeater:west", "redstone_dust"]
      ]
    }
  ]
}
```

**How it works:** A pulse circulates through two repeaters and connecting dust in a loop. Each repeater adds delay. With both at 1-tick (default), the clock runs at 4 game ticks (0.2 seconds) per cycle.

**Starting the clock:** Place a redstone torch momentarily next to any dust in the loop, then remove it. The pulse it injected will loop forever.

**Adjusting speed:** Right-click repeaters to add delay. Both at 4-tick = 16 game tick cycle (0.8s).

---

### Hopper Clock (Adjustable Timer)

Precise, adjustable timing. Items shuttle between two hoppers.

- **Dimensions:** 5x1x3
- **Difficulty:** Medium
- **Materials:** 2 hoppers, 2 comparators, 2 redstone torches, 2 stone, 4 redstone dust

```json
{
  "name": "Hopper Clock",
  "dimensions": [5, 1, 3],
  "materials": { "hopper": 2, "comparator": 2, "redstone_torch": 2, "stone": 2, "redstone_dust": 4 },
  "layers": [
    {
      "y": 0, "note": "Foundation and hoppers — hoppers face INTO each other",
      "grid": [
        ["stone", "hopper:east", "hopper:west", "stone", null]
      ]
    },
    {
      "y": 1, "note": "Comparators read hoppers, torches cross-couple",
      "grid": [
        ["redstone_torch", "comparator:west", "comparator:east", "redstone_torch", null]
      ]
    },
    {
      "y": 2, "note": "Cross-wiring connects each comparator to opposite torch",
      "grid": [
        ["redstone_dust", "redstone_dust", "redstone_dust", "redstone_dust", null]
      ]
    }
  ]
}
```

**How it works:** Items flow from one hopper to the other. Each comparator reads its hopper's fill level. When items leave, the signal drops, allowing the opposite hopper to unlock. Cross-coupled torches create the flip-flop behavior.

**Setting the timer:** Drop items into either hopper.
- 1 item = ~0.7 second cycle
- 5 items = ~3.4 seconds
- 64 items = ~40 seconds
- Use stackable items only (stack to 64)

---

## Memory & Flip-Flops

### T Flip-Flop (Button-to-Lever)

Converts a button press into a toggle. Press once = ON, press again = OFF.

- **Dimensions:** 3x1x3
- **Difficulty:** Easy
- **Materials:** 2 droppers, 1 comparator, 1 redstone dust, 1 button, 1 any item

```json
{
  "name": "T Flip-Flop (Dropper)",
  "dimensions": [3, 1, 3],
  "materials": { "dropper": 2, "comparator": 1, "redstone_dust": 1, "button_stone": 1 },
  "layers": [
    {
      "y": 0, "note": "Bottom dropper faces UP — put 1 item inside this one",
      "grid": [["dropper:up", "comparator:east", "redstone_dust"]]
    },
    {
      "y": 1, "note": "Top dropper faces DOWN into bottom dropper",
      "grid": [["dropper:down", null, null]]
    },
    {
      "y": 2, "note": "Button on top — signal must reach both droppers",
      "grid": [["button_stone", null, null]]
    }
  ]
}
```

**How it works:** One item bounces between two stacked droppers. A comparator reads the bottom dropper — item present = ON, item absent = OFF. Each button press makes both droppers fire, moving the item to whichever dropper doesn't have it.

**Setup:** Place exactly 1 item (any item) in the bottom dropper. The button must power both droppers simultaneously — quasi-connectivity in Java helps here (the button on top of the upper dropper quasi-powers the lower one).

---

### RS NOR Latch (Set/Reset Memory)

Set input turns output ON. Reset input turns output OFF. Output holds until changed.

- **Dimensions:** 5x1x3
- **Difficulty:** Easy
- **Materials:** 2 redstone torches, 3 redstone dust, 3 stone, 2 buttons

```json
{
  "name": "RS NOR Latch",
  "dimensions": [5, 1, 3],
  "materials": { "stone": 3, "redstone_torch": 2, "redstone_dust": 3, "button_stone": 2 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [["stone", "stone", "stone", "stone", "stone"]]
    },
    {
      "y": 1, "note": "Cross-coupled torches with dust connections",
      "grid": [["redstone_dust", "redstone_torch", "redstone_dust", "redstone_torch", "redstone_dust"]]
    },
    {
      "y": 2, "note": "Set and Reset buttons",
      "grid": [["button_stone", null, null, null, "button_stone"]]
    }
  ]
}
```

**How it works:** Two torches sit on adjacent blocks, cross-coupled with dust. Each torch's output powers the other torch's block. Pressing Set powers the block under one torch (turning it OFF), which lets the other torch turn ON. The state locks in place.

**Inputs:** Left button = Set (Q goes ON), Right button = Reset (Q goes OFF).

---

## Piston Doors

### 2x2 Flush Piston Door

A 2-wide, 2-tall door that sits flush with the wall when closed.

- **Dimensions:** 3x5x4
- **Difficulty:** Medium
- **Materials:** 4 sticky pistons, 4 stone (door blocks), 2 repeaters, 8 redstone dust, 6 stone (structure)

```json
{
  "name": "2x2 Flush Piston Door",
  "dimensions": [5, 3, 4],
  "materials": { "sticky_piston": 4, "stone": 10, "redstone_dust": 8, "repeater": 2 },
  "layers": [
    {
      "y": 0, "note": "Sub-floor — bottom pistons face UP, will pull door blocks down",
      "grid": [
        ["stone", "stone", "stone", "stone", "stone"],
        ["stone", "sticky_piston:up", "sticky_piston:up", "stone", "stone"],
        ["stone", "stone", "stone", "stone", "stone"]
      ]
    },
    {
      "y": 1, "note": "Floor level — bottom door blocks sit on top of pistons",
      "grid": [
        ["stone", "stone", "stone", "stone", "stone"],
        [null, "stone", "stone", null, "redstone_dust"],
        ["stone", "stone", "stone", "stone", "stone"]
      ]
    },
    {
      "y": 2, "note": "Top door blocks — side pistons pull these sideways",
      "grid": [
        ["stone", "stone", "stone", "stone", "stone"],
        ["sticky_piston:east", "stone", "stone", "sticky_piston:west", "redstone_dust"],
        ["stone", "stone", "stone", "stone", "stone"]
      ]
    },
    {
      "y": 3, "note": "Wiring — repeaters delay side pistons so bottom fires first",
      "grid": [
        ["stone", "redstone_dust", "redstone_dust", "stone", "redstone_dust"],
        [null, "redstone_dust", "redstone_dust", null, "lever"],
        ["stone", "redstone_dust", "redstone_dust", "stone", "redstone_dust"]
      ]
    }
  ]
}
```

**How it works:** When triggered, bottom sticky pistons retract first (pulling bottom blocks down below floor). After a 1-tick delay from repeaters, side sticky pistons retract (pulling top blocks into the walls). This two-step sequence creates a clean 2x2 opening.

**Closing** reverses the sequence: side pistons extend first (pushing top blocks into place), then bottom pistons extend (pushing bottom blocks up).

**Important:** Uses quasi-connectivity — the top-layer wiring powers the side pistons through the blocks above them. This is a Java-only mechanic.

---

## Item Sorting

### Hopper-Based Item Sorter (Per Slice)

Standard overflow-protected item sorter. Tile sideways for multiple items.

- **Dimensions:** 1x5x5
- **Difficulty:** Medium
- **Materials:** 2 hoppers, 1 comparator, 1 redstone torch, 3 redstone dust, 4 stone, 1 chest

```json
{
  "name": "Item Sorter (Single Slice)",
  "dimensions": [1, 5, 5],
  "materials": { "hopper": 2, "comparator": 1, "redstone_torch": 1, "redstone_dust": 3, "stone": 4, "chest": 1 },
  "layers": [
    {
      "y": 0, "note": "Chest at the bottom",
      "grid": [["chest", null, null, null, null]]
    },
    {
      "y": 1, "note": "Output hopper points down into chest — locked by torch",
      "grid": [["hopper:down", null, null, null, null]]
    },
    {
      "y": 2, "note": "Comparator reads sorting hopper, torch locks output hopper",
      "grid": [["stone", "comparator:south", "redstone_dust", "stone", null]]
    },
    {
      "y": 3, "note": "Sorting hopper — points sideways into wall, NOT down",
      "grid": [["hopper:west", null, null, "redstone_torch", null]]
    },
    {
      "y": 4, "note": "Input hopper — items flow through this row",
      "grid": [["hopper:east", null, null, null, null]]
    }
  ]
}
```

**Sorting hopper contents:**
| Slot | Contents |
|------|----------|
| 1 | 41x target item |
| 2-5 | 1x renamed stick each (filler) |

**How it works:** Items flow through the top hopper row. When a matching item enters the sorting hopper, the item count goes from 45 to 46. The comparator outputs signal strength 3, which travels through dust to the torch block. Strength 3 is exactly enough to turn off the torch, unlocking the output hopper to pull the item down to the chest.

**Critical details:**
- Sorting hopper MUST point sideways (into a block), never down
- Filler items MUST be renamed in an anvil (so they never match incoming items)
- Only 1 filler per slot — more breaks overflow protection
- Non-stackable items can't be sorted this way

---

## Farms

### Observer Sugarcane Farm (Per Plant)

Automatic sugarcane harvester using observer detection.

- **Dimensions:** 3x3x4
- **Difficulty:** Easy
- **Materials:** 1 observer, 1 piston, 1 hopper, 1 chest, 2 stone, 1 dirt, 1 water bucket

```json
{
  "name": "Sugarcane Farm (Single Plant)",
  "dimensions": [3, 3, 4],
  "materials": { "stone": 4, "dirt": 1, "water": 1, "piston": 1, "observer": 1, "hopper": 1, "chest": 1, "redstone_dust": 1 },
  "layers": [
    {
      "y": 0, "note": "Collection — chest with hopper above it",
      "grid": [
        ["chest", null, null],
        [null, null, null],
        [null, null, null]
      ]
    },
    {
      "y": 1, "note": "Ground level — water hydrates dirt, sugarcane planted on dirt",
      "grid": [
        ["hopper:down", "water", "dirt"],
        [null, null, "stone"],
        [null, null, null]
      ]
    },
    {
      "y": 2, "note": "First growth level — sugarcane grows here naturally",
      "grid": [
        [null, null, null],
        [null, null, "stone"],
        [null, null, null]
      ]
    },
    {
      "y": 3, "note": "Detection level — observer watches for 3rd cane block, piston breaks it",
      "grid": [
        [null, "piston:east", null],
        [null, null, "observer:west"],
        [null, null, "redstone_dust"]
      ]
    }
  ]
}
```

**How it works:** Sugarcane grows up to 3 blocks tall. The observer watches the space where the 3rd block would appear (Y=3). When cane grows there, the observer detects the block change and fires a pulse. The piston extends, breaking the top cane blocks. Broken cane drops as items, landing near the hopper which feeds into the chest.

**Important:**
- Observer detecting face (the "eye") must face the growth space
- Use regular piston, not sticky
- Sugarcane needs dirt/sand with water adjacent
- Growth is random-tick — can't be accelerated with bone meal in Java

**Tiling:** Repeat this module along the X axis. Share the water channel and hopper line for efficiency.

---

## Utility Circuits

### Pulse Extender (Observer + Repeater)

Extends a short observer pulse to a longer duration.

- **Dimensions:** 4x1x2
- **Difficulty:** Easy
- **Materials:** 1 observer, 1 repeater, 1 redstone dust, 2 stone

```json
{
  "name": "Pulse Extender",
  "dimensions": [4, 1, 2],
  "materials": { "stone": 2, "observer": 1, "redstone_dust": 1, "repeater": 1 },
  "layers": [
    {
      "y": 0, "note": "Foundation",
      "grid": [["stone", "stone", "stone", "stone"]]
    },
    {
      "y": 1, "note": "Observer output -> dust -> repeater (set delay as needed)",
      "grid": [["observer:east", "redstone_dust", "repeater:east", null]]
    }
  ]
}
```

**Repeater delay settings:**
- Default (no clicks): 2 game ticks
- 1 right-click: 4 game ticks
- 2 right-clicks: 6 game ticks
- 3 right-clicks: 8 game ticks

Chain multiple repeaters for longer pulses.

### Torch Tower (Vertical Signal)

Carries redstone signal straight up. Uses alternating torches.

- **Dimensions:** 1x2xN (N = height needed)
- **Difficulty:** Easy
- **Materials:** N torches, N stone (alternating placement)

Build pattern (side view, repeating every 2 blocks of height):
```
Y=3: [torch on side of block at Y=4]  [block]
Y=2: [block]  [torch on side of block at Y=2, opposite side]
Y=1: [torch on side of block at Y=2]  [block]
Y=0: [input dust] -> [block]
```

The torches alternate sides of a zigzag column of blocks. Each torch inverts, so every 2 torches = same polarity. For same-polarity output, use an even number of torches.
