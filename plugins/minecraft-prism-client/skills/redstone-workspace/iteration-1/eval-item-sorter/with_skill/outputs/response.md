# Automatic Item Sorter -- Taming Your Chest Chaos

Sorting items automatically is one of the most satisfying things you can build in Minecraft. The good news: the standard hopper-based item sorter is a well-proven design that is completely silent, works in survival, and can be expanded to handle as many item types as you want just by repeating the same module over and over.

I have generated an interactive build viewer for you -- open `item-sorter-viewer.html` in your browser to see the layer-by-layer layout. Below is the full explanation.

---

## What This Build Does

You dump all your items into a single input chest. From there, items flow through a chain of hoppers (the "item pipe"). Below the pipe, one sorting module per item type filters out that item and sends it down into its own dedicated storage chest. Any items that do not match any filter simply pass through to the end of the line, where you can place a "catch-all" chest for unsorted stuff.

The build shown in the viewer is a 3-channel sorter, but the design tiles -- you can add as many channels as you need by repeating the same 1-wide slice.

---

## Materials (Per Sorting Channel)

| Block | Count | Notes |
|-------|-------|-------|
| Hopper | 3 | 1 pipe hopper + 1 sorting hopper + 1 output hopper |
| Chest | 1 | Storage for sorted items (use a double chest for more capacity) |
| Stone | 3 | Structural blocks for redstone |
| Comparator | 1 | Reads the sorting hopper's contents |
| Redstone Dust | 3 | Connects comparator to torch circuit |
| Redstone Torch | 1 | Locks the output hopper until the right item arrives |

For 3 channels, that totals 9 hoppers, 3 chests, 9 stone, 3 comparators, 9 redstone dust, and 3 redstone torches, plus 2 cobblestone for the pipe endpoint.

Hoppers are the most expensive part -- each one needs 5 iron ingots and a chest. An iron farm will help enormously if you plan a large sorter.

---

## How to Build It (Layer by Layer)

Face **north** when starting the build. In the viewer, the top of the grid is north and the left side is west.

### Layer 1 (Y=0) -- Storage Chests

Place your storage chests in a row running east-west. One chest per sorting channel. You can use double chests by placing two side-by-side (extending south), giving you 54 slots of storage per item type.

### Layer 2 (Y=1) -- Output Hoppers

Directly above each chest, place a hopper pointing **down** into the chest below it. These are the "output hoppers" -- they will be locked most of the time and only unlock when the right item needs to come through.

### Layer 3 (Y=2) -- Redstone Wiring

This is the brain of each sorting channel. Behind each output hopper (one row south), place a **stone block**. On the south side of that stone block, place a **redstone torch** -- this torch will power the stone block, which in turn locks the output hopper via redstone signal.

One row further north (between the output hopper and the sorting hopper above), place a **comparator** facing south (toward the torch). The comparator reads the contents of the sorting hopper directly above/behind it.

Between the comparator's output and the torch's stone block, place **redstone dust** to carry the signal.

The signal path is: sorting hopper contents -> comparator -> dust -> stone block -> torch turns OFF -> output hopper unlocks.

### Layer 4 (Y=3) -- Sorting Hoppers

Place a hopper pointing **west** (into a stone wall block). This is critical: the sorting hopper must point sideways into a solid block, NOT downward. If it pointed down, all items would fall straight through without being filtered.

The stone block it points into acts as a dead end -- items cannot leave through a solid block.

### Layer 5 (Y=4) -- Item Pipe

Place a row of hoppers pointing **east**, chaining from one to the next. Items enter from the west end and flow east through the pipe. Each pipe hopper sits directly above a sorting hopper. As items pass through, matching items get pulled down into the sorting hopper below.

At the east end of the pipe, place a solid block or a chest to catch anything that was not sorted.

---

## Setting Up the Filters

This is the most important step and where most people make mistakes.

For each sorting hopper (the ones on Layer 4 pointing west):

| Slot | What to Put In |
|------|---------------|
| Slot 1 | **41 of the item you want to sort** (e.g., 41 cobblestone) |
| Slot 2 | 1 renamed stick |
| Slot 3 | 1 renamed stick |
| Slot 4 | 1 renamed stick |
| Slot 5 | 1 renamed stick |

**The sticks must be renamed at an anvil.** Name them something like "filler" or "sort" -- anything works, as long as they have a custom name. This prevents them from ever matching incoming items in the pipe. Without renaming, regular sticks flowing through the pipe would match your filler sticks and corrupt the filter.

**Why 41 items?** The magic is in the math. 41 target items + 4 filler items = 45 total items in a 5-slot hopper. This produces a comparator signal strength of exactly 2. When one more matching item enters from the pipe above (making it 46 items), the signal rises to exactly 3. Signal strength 3 is just enough to travel through the dust and disable the redstone torch, unlocking the output hopper. Once the extra item drains out, the signal drops back to 2 and the torch re-engages, locking the output hopper again.

If the signal ever reached 4, it would bleed into adjacent channels and break neighboring sorters. The 41 + 4 ratio is specifically designed to prevent that.

---

## How the Redstone Works (Signal Trace)

Here is the complete signal path for one channel:

1. The **comparator** constantly reads the sorting hopper's contents
2. With 45 items (41 target + 4 filler), the comparator outputs signal strength **2**
3. Signal strength 2 travels through **1 block of redstone dust** (losing 1 strength, becoming 1)
4. Strength 1 is NOT enough to power the stone block that the torch is on -- the **torch stays ON**
5. The lit torch powers the stone block next to the output hopper, which **locks the output hopper** (hoppers stop transferring when powered by redstone)
6. When a 46th matching item enters the sorting hopper from the pipe, the comparator output rises to **3**
7. Strength 3 travels through the dust (becomes 2), which IS enough to power the torch's block
8. The torch **turns OFF**, removing power from the output hopper
9. The output hopper **unlocks** and pulls items from the sorting hopper down into the chest
10. Once the sorting hopper drops back to 45 items, signal returns to 2, the torch turns back on, and the output hopper locks again

This cycle happens automatically, continuously, with no player intervention needed.

---

## Expanding the System

To sort more item types, just add more 1-wide slices to the east:

- Each new channel adds: 1 pipe hopper, 1 sorting hopper, 1 output hopper, 1 chest, 1 comparator, 3 stone, 3 redstone dust, 1 redstone torch
- All pipe hoppers chain east, passing items along
- At the very end, place a "catch-all" chest or hopper feeding into a chest for unsorted items

You can realistically sort 20-30 item types before the system gets too long. For larger systems, consider using a water stream to deliver items to the pipe instead of chaining hoppers the entire length, since long hopper chains cause more server lag.

---

## Common Mistakes to Avoid

1. **Sorting hopper pointing down instead of sideways.** This is the number one mistake. If the sorting hopper points down, items bypass the filter entirely. It MUST point into a solid block (sideways).

2. **Forgetting to rename the filler sticks.** If you use plain sticks, any sticks flowing through the pipe will enter the filter slots and break the signal calibration.

3. **Using too many or too few filler items.** Exactly 4 filler items, one per slot (slots 2-5). More or fewer breaks the overflow protection.

4. **Trying to sort unstackable items.** Items that do not stack (tools, armor, potions, enchanted books) cannot be sorted with this design. They would produce a signal strength far too high and break adjacent channels.

5. **Placing redstone components on glass or slabs.** Use opaque blocks (stone, cobblestone, dirt) for any block that needs to carry a redstone signal. Transparent blocks like glass cannot be powered.

6. **Not leaving space between the torch and adjacent channels.** Each channel is exactly 1 block wide. The torch's signal must not reach the neighboring channel's output hopper. The stone block layout in the viewer ensures proper isolation.

---

## Tips for Your Storage Room

- **Label your chests** with item frames showing what is inside each one
- **Use double chests** for high-volume items like cobblestone, dirt, and common ores
- **Put the most common items first** (closest to the input) so the pipe does not have to carry them far
- **Add a "junk" chest at the end** for items you did not set up filters for
- **Build in a straight line** to keep the system simple and easy to extend
- **Test in creative mode first** if you are unsure -- build a 2-channel test version to make sure you understand the layout before committing survival resources

This design is completely silent (no pistons, no observers), runs at 2.5 items per second per channel, and will sort items indefinitely without maintenance. Once it is set up, you can dump an entire inventory into the input chest and walk away.
