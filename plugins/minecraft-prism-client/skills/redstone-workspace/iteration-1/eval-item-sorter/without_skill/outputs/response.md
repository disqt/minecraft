# Automatic Item Sorting in Minecraft

Sorting items by hand is painful once you have more than a few chests. The good news is that vanilla Minecraft has a well-known redstone design that automatically routes items into the correct chest. No mods required.

---

## How It Works (The Concept)

The standard automatic item sorter uses **hoppers with specific item filters**. Each column of the sorter is dedicated to one item type (e.g., cobblestone, iron ingots, diamonds). Items flow through a line of hoppers at the top, and when an item matches a filter, it drops down into the correct chest.

The key mechanic: a hopper only pulls items that match what is already inside it, **if** it is locked/unlocked by a redstone signal in the right way. The filter hopper holds a precise arrangement of items to ensure only the target item drops through.

---

## What You Need (Per Sorted Item Type)

For each item you want to sort, you need:

- 2 chests (or 1 double chest)
- 2 hoppers
- 1 redstone comparator
- 1 redstone repeater (optional in some designs, but recommended)
- 2 redstone dust
- 1 redstone torch
- Some building blocks (any solid block)

For the top input line:

- 1 hopper per slot (they chain together across the top)
- 1 or more input chests at the start of the line

---

## Step-by-Step Build Guide

### Step 1: Build the Frame

Build a wall that is 2 blocks tall and as wide as the number of item types you want to sort. Each column is one item type.

### Step 2: Place the Chests

At the bottom of each column, place a double chest (two chests side by side or stacked). These are your storage chests.

### Step 3: Place the Bottom Hopper

On top of each double chest, place a hopper pointing **down into the chest**. (Crouch/sneak and click on the chest to attach the hopper to it.)

### Step 4: Place the Filter Hopper

On top of the bottom hopper, place another hopper pointing **down into the hopper below it**. This is your filter hopper.

### Step 5: Load the Filter

This is the critical step. Open the filter hopper and place items like this:

| Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 |
|--------|--------|--------|--------|--------|
| 1x target item | 1x junk item | 1x junk item | 1x junk item | 1x junk item |

- **Slot 1**: Place exactly **1** of the item you want this column to sort (e.g., 1 cobblestone).
- **Slots 2-5**: Place **1 each** of an item that you will never sort and that does not stack with the target. Renamed items work great for this -- just rename any junk item on an anvil to something like "filler" so it is unique and will never match anything flowing through the system.

**Why this arrangement?** The comparator reads the fill level of the hopper. With 4 filler items and 1 target item, the signal strength is exactly 1. When a matching item enters (bringing slot 1 to 2+), the signal strength increases, which unlocks the hopper below to pull the item through. The filler items never get pulled because nothing downstream is requesting them.

### Step 6: Add the Redstone Circuit

Behind each filter hopper column, build this circuit:

```
Side view (looking at the back of the sorter):

[Filter Hopper]
[Solid Block] [Comparator ->] [Solid Block]
                               [Redstone Torch on side, pointing at bottom hopper]
[Bottom Hopper] ............. [Redstone Dust on ground]
[Chest]
```

More precisely:

1. Place a **solid block** directly behind the filter hopper.
2. Place a **comparator** coming **out of** that block (the comparator reads the hopper's contents through the block). The comparator should point away from the hopper.
3. Place a **solid block** where the comparator output points.
4. On the side of that second block (facing the bottom hopper), place a **redstone torch**.
5. Place **redstone dust** on the ground connecting as needed.

The logic: when the filter hopper has only the base items (signal strength 1), the torch stays ON, which **locks** the bottom hopper (preventing it from passing items). When a matching item enters the filter hopper and raises the signal to 2+, the comparator output increases, the torch turns OFF, the bottom hopper unlocks, and the item flows down into the chest.

### Step 7: Build the Input Line

Across the top, place a chain of hoppers all pointing into each other in a line, feeding into the first filter hopper column. At the start of this line, place one or more chests where you dump all your unsorted items.

Items flow along the hopper line. When they pass over a filter hopper that matches, they drop down. If nothing matches, they continue along to the end.

### Step 8: Add an Overflow Chest

At the **end** of the hopper line, place a chest. Any items that do not match any filter will end up here. This prevents the system from clogging.

---

## Layout Diagram (Top-Down View)

```
[Input Chest] > [Hopper] > [Hopper] > [Hopper] > [Hopper] > [Overflow Chest]
                   |           |           |           |
               [Filter]   [Filter]   [Filter]   [Filter]
                   |           |           |           |
               [Chest]    [Chest]    [Chest]    [Chest]
              Cobblestone    Iron      Diamond     Dirt
```

---

## Tips and Common Mistakes

1. **Hopper direction matters.** Always crouch-click on the block you want the hopper to point into. If a hopper points the wrong way, break it and replace it.

2. **Do not put stackable items as filler.** If your filler items could come through the input line, they will get caught by the filter. Use renamed items or items you will genuinely never put in (like renamed sticks).

3. **The system handles stackable items only (by default).** Items that stack to 16 (like ender pearls, snowballs) need a slightly different filter ratio. Non-stackable items (armor, tools) cannot be filtered this way -- send those to the overflow chest and sort manually.

4. **Expandability.** You can extend the input hopper line as far as you want. Just keep adding columns. Hoppers transfer items at about 2.5 items/second, so very long lines may be slow. For large systems, consider multiple parallel input lines.

5. **Chunk loading.** The sorter only works when the chunks it is in are loaded (i.e., a player is nearby). If you walk far away, items will stop flowing until you return.

6. **Labeling.** Place item frames on the front of each chest with one of the target item inside. This makes it easy to see what goes where at a glance.

---

## Quick Reference: Materials for a 10-Type Sorter

| Material | Quantity |
|----------|----------|
| Chests | 20 (for 10 double chests) + 1 input + 1 overflow |
| Hoppers (filter + bottom) | 20 |
| Hoppers (input line) | 10 |
| Comparators | 10 |
| Redstone torches | 10 |
| Redstone dust | ~20 |
| Solid blocks | ~20 |
| Filler items (renamed) | 40 (4 per filter) |
| Iron ingots (for hoppers/comparators) | A lot -- each hopper is 5 iron |

Iron is the main bottleneck. 30 hoppers = 150 iron ingots. An iron farm is strongly recommended before building a large sorter.

---

## What About Mods?

If you are open to mods, there are some that make storage dramatically easier:

- **Tom's Simple Storage** -- network-based storage where all chests are accessible from one terminal. No redstone needed.
- **Applied Energistics 2 (AE2)** -- digital storage system (more complex, very powerful).
- **Refined Storage** -- similar to AE2 but simpler to set up.

But the vanilla hopper sorter works perfectly well and is a satisfying build. Start with a small 5-10 type sorter for your most common items, then expand as you get more iron.

---

If you want, I can help you figure out which items to prioritize sorting, or help you plan the layout dimensions for your storage room.
