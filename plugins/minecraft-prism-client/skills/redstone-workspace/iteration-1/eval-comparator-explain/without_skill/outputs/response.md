# How Comparators Work

Comparators are one of the trickiest redstone components, so don't worry about finding them confusing -- most people do at first. Let me break it down.

## The Basics

A comparator is a small block that sits on the ground and has **three ports**:

- **Back** (the single torch end): This is the **main input**. The signal comes in here.
- **Front** (the two-torch end): This is the **output**.
- **Sides** (left and right): These are the **side inputs**.

The comparator has two modes, toggled by right-clicking it. You can tell the modes apart by looking at the front torch:

- **Front torch OFF** = Compare mode (the default)
- **Front torch ON** = Subtract mode

## Compare Mode (front torch OFF)

This is the simpler mode. The comparator asks:

> "Is my back input **greater than or equal to** both side inputs?"

- If **yes**: the output equals the back input signal strength.
- If **no** (either side input is stronger): the output is **0** (off).

**Example:**
- Back input = 10, Side input = 7 --> Output = 10 (back is stronger, so it passes through)
- Back input = 5, Side input = 8 --> Output = 0 (side is stronger, so it blocks)
- Back input = 6, Side input = 6 --> Output = 6 (equal counts as passing)

Think of compare mode as a **gate**: "Only let the signal through if it's at least as strong as the side signal."

## Subtract Mode (front torch ON)

This is the one that trips people up. Here's how it works:

> Output = Back input **minus** the strongest side input (but never goes below 0)

That's it. It literally does subtraction.

**Example:**
- Back = 12, Side = 4 --> Output = 12 - 4 = **8**
- Back = 10, Side = 7 --> Output = 10 - 7 = **3**
- Back = 5, Side = 9 --> Output = 5 - 9 = negative, so it clamps to **0**
- Back = 15, Side = 0 --> Output = 15 - 0 = **15** (full strength, nothing subtracted)

If both sides have signals, only the **stronger** side input matters.

**Example with two side inputs:**
- Back = 14, Left side = 3, Right side = 9 --> Output = 14 - 9 = **5** (uses the stronger side)

## Why Is Subtract Mode Useful?

Here are some practical uses that might help it click:

### 1. Dimming a Signal
If you have a signal strength of 15 coming out of a lever and you want to reduce it to exactly 8, feed a signal of 7 into the side. 15 - 7 = 8.

### 2. Pulse Shortening / Timing
You can create very precise short pulses by subtracting delayed versions of a signal from itself. This is the basis of many compact pulse circuits.

### 3. Item Counting
Comparators read the fullness of containers (chests, hoppers, barrels, etc.) as a signal strength from 0-15. By subtracting a threshold value from the side, you can make something activate only when a chest passes a certain fill level.

**Example:** A chest outputs signal 9 (partially full). You feed signal 6 into the side of a subtract-mode comparator. Output = 9 - 6 = 3. If the chest empties below signal 6, the output drops to 0 and shuts off. You've just built a "only activate when the chest is more than X full" detector.

### 4. Analog Logic / Math
Since redstone signals go from 0-15, subtract mode lets you do actual math with signals. Combined with other comparators, you can build calculators, combination locks, and other logic circuits.

## Quick Reference

| Mode | Condition | Output |
|------|-----------|--------|
| **Compare** (torch off) | Back >= Side | Back signal |
| **Compare** (torch off) | Back < Side | 0 |
| **Subtract** (torch on) | Always | Back - Side (min 0) |

## One More Thing: Container Reading

Comparators have a special ability that has nothing to do with modes: when you point the back of a comparator into a **container** (chest, hopper, furnace, barrel, brewing stand, etc.), it reads the fullness of that container and outputs a signal from 0-15. This works in both modes. The mode then determines what happens to that signal based on the side inputs.

This container-reading ability is what makes comparators essential for automatic storage systems, item sorters, and farms.

## Summary

- **Compare mode** = "Let the signal through only if it's strong enough" (acts as a gate)
- **Subtract mode** = "Reduce the signal by this much" (does arithmetic)
- Both modes use: back input as the main signal, side inputs as the reference/modifier
- The front torch being lit tells you which mode you're in

Start by placing a comparator, putting a chest behind it, and filling the chest gradually. Watch the output signal change. Then try adding a side signal and toggling between modes. Seeing it in action makes it click much faster than reading about it.
