# Simple Hidden Piston Door (2x1 Flush)

This is a beginner-friendly hidden entrance that uses sticky pistons to pull two blocks into the ground, revealing a doorway. When closed, it looks like a normal wall.

## What You Need

- 2 Sticky Pistons
- 2 Blocks (matching your wall -- e.g., stone, dirt, whatever your base is made of)
- 1 Lever (or button, pressure plate, etc.)
- 4-6 Redstone Dust
- A few solid blocks for wiring

## How It Works

The two sticky pistons face upward, hidden beneath the floor. Each one has your wall block sitting on top of it. When powered, the pistons retract downward, pulling the wall blocks down with them and opening a 2x1 gap you can walk through. Flip the lever again and the blocks pop back up, sealing the entrance.

## Step-by-Step Build

### Step 1: Dig the Hole

Stand where you want the doorway. Dig a 2-block-wide, 3-block-deep trench in front of your wall. The trench should be 1 block wide (front to back) and 2 blocks wide (left to right).

```
Side view (cross-section):

  [W][D][D][W]     W = Wall, D = where the door blocks are
  [W][  ][  ][W]    (empty space behind = your base entrance)
  [W][  ][  ][W]
  [G][G][G][G]     G = Ground level
```

### Step 2: Place the Pistons

At the bottom of the trench (3 blocks below ground level), place 2 sticky pistons facing UP. They should be side by side.

```
Side view of trench:

  Ground level -->  [  ][  ]
                    [  ][  ]
                    [SP][SP]    SP = Sticky Piston (facing up)
```

### Step 3: Place Your Wall Blocks

Put one matching wall block on top of each sticky piston. These are the blocks that will move up and down. When the pistons are extended (default, unpowered state), these blocks should sit flush with the rest of your wall at ground level.

```
  Ground level -->  [DB][DB]   DB = Door Block (sits flush with ground)
                    [  ][  ]
                    [SP][SP]
```

Wait -- this means the pistons need to be 2 blocks below ground level (not 3), because the piston itself is 1 block, and when extended, the piston head + the door block = 2 blocks high, reaching ground level.

Let me correct the layout:

```
  Ground level -->  [DB][DB]   DB = Door Block (flush with wall)
                    [SP][SP]   SP = Sticky Piston (facing up, extended)
```

When powered (piston retracts), the door blocks drop down by 1:

```
  Ground level -->  [  ][  ]   (open! walk through here)
                    [DB][DB]   Door blocks pulled down
                    [SP][SP]
```

Hmm, that only opens 1 block of space -- you need 2 blocks tall to walk through. Let me redesign this properly.

## Revised Design: Sideways Pistons (Simpler and Better)

The easiest hidden door for a beginner is actually **two sticky pistons facing inward from each side**, pulling wall blocks sideways. This creates a 1-wide, 2-tall doorway.

### Layout

```
Top-down view:

  [W][W][W][W][W]
  [W][W][D][W][W]     D = Door blocks (2 high, stacked)
  [W][SP-->][D][<--SP][W]   SP = Sticky pistons behind the wall
  [W][W][W][W][W]

Actually, let me just describe it clearly:
```

### Clear Step-by-Step

**1. Build your wall.** Make it at least 3 blocks wide and 2 blocks tall. Leave 1 column empty in the middle (2 blocks tall) -- this is where the door blocks will go.

**2. Behind the wall, on each side of the gap, place a sticky piston** facing toward the center gap. You need 2 on the left side (stacked vertically) and 2 on the right side (stacked vertically) -- 4 sticky pistons total.

```
View from inside your base, looking at the back of the wall:

  [W] [SP->] [  ] [<-SP] [W]     Top row
  [W] [SP->] [  ] [<-SP] [W]     Bottom row
       Left         Right
```

**3. Place your disguise blocks.** Put one block on each piston head (the sticky face). Use the same block type as your wall. When the pistons extend, they push these blocks into the center, closing the doorway.

```
Pistons extended (door CLOSED, viewed from outside):

  [W] [D] [D] [W]     Looks like a normal wall
  [W] [D] [D] [W]     D = disguise blocks pushed by pistons
```

Wait -- that makes the door 2 wide instead of sealed. Each side pushes 1 block inward, so with both sides, you get 2 blocks filling a 2-wide gap. If you want a 1-wide gap, each side pushes 1 block inward and they meet in the middle. But two blocks can't occupy the same space.

### Final Correct Design: 2-Wide Door

The simplest version: a **2-wide, 2-tall** door.

**Materials:**
- 4 Sticky Pistons
- 4 Wall-matching blocks
- 1 Lever
- ~10 Redstone Dust
- ~6 solid blocks (for wiring channel)

**Step 1:** Build your wall. Leave a 2-wide, 2-tall gap where the door will be.

**Step 2:** On each side of the gap, dig 1 block into the wall to make room for pistons. Place 2 sticky pistons on the left side (stacked, facing right) and 2 on the right side (stacked, facing left).

```
Back view of the wall (from inside your base):

        Left piston    Gap    Right piston
  [W]   [SP ->]      [  ][  ]    [<- SP]   [W]
  [W]   [SP ->]      [  ][  ]    [<- SP]   [W]
```

**Step 3:** Attach 1 wall block to each piston's sticky face. When powered, each piston pushes its block 1 space inward, filling the gap.

```
Door CLOSED (pistons extended):

  [W] [SP|DB]  [DB|SP] [W]
  [W] [SP|DB]  [DB|SP] [W]

From the front this looks like:
  [W] [DB] [DB] [W]
  [W] [DB] [DB] [W]   -- seamless wall
```

```
Door OPEN (pistons retracted):

  [W] [SP+DB] [  ][  ] [SP+DB] [W]
  [W] [SP+DB] [  ][  ] [SP+DB] [W]

  The gap is open, walk through!
```

**Step 4:** Run redstone. Dig a channel under the floor (or behind/above the wall) to connect all 4 pistons to a single lever.

The easiest wiring method:
- Place a line of redstone dust under the floor that runs beneath all 4 pistons
- Each piston needs a redstone signal reaching the block adjacent to it or directly beneath it
- Dig a trench 1 block below the pistons, place redstone dust along it, and bring it up to a lever somewhere convenient

```
Wiring (side cross-section, simplified):

  [SP]  [    ]  [    ]  [SP]    Piston level
  [RB]  [ RD ]  [ RD ]  [RB]   1 below: Redstone on blocks
                                RB = redstone on block below piston
                                RD = redstone dust connecting them

  Route one end up to a lever on the wall.
```

**Step 5:** Place your lever on a nearby wall. Flip it -- all 4 pistons should retract, pulling the disguise blocks with them and opening the doorway. Flip again to close.

## Tips

- **Lever vs. button:** A lever stays on/off (good for doors you leave open). A button gives a short pulse (door opens briefly then closes). For a hidden entrance you walk through, a lever is easier.
- **Pressure plate trick:** Put a pressure plate on the inside so you can walk out easily, and a hidden lever on the outside to get in.
- **Keep it flush:** Make sure the disguise blocks match your wall exactly. Nobody will notice the door exists.
- **Test it:** Before building the wiring into the floor, test with a redstone torch placed next to a piston to confirm the pistons are facing the right direction and the blocks move correctly.

## Common Problems

| Problem | Fix |
|---------|-----|
| Pistons don't move | Check that redstone signal reaches them. Redstone must be on a block adjacent to the piston (not on the piston itself). |
| Only some pistons fire | The redstone line may be too long (signal weakens after 15 blocks). Add a repeater if needed. |
| Blocks don't come back | Make sure you used **sticky** pistons, not regular ones. |
| Door looks weird when open | The piston heads may be visible. You can hide them by recessing the pistons 1 more block into the wall and pushing 2 blocks each instead of 1. |

This is about the simplest hidden piston door you can build. Once you're comfortable with it, you can upgrade to a "flush" design (where the pistons are completely invisible even when open) or add a Jeb door (seamless on all sides), but those require more complex redstone.
