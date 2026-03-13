# How Comparators Work (and What Subtract Mode Actually Does)

Great question -- comparators are one of the trickiest redstone components, but once it clicks, you will use them everywhere. Let me break it down.

## The Basics: What Is a Comparator?

A comparator is a small redstone component that takes up to **three inputs** and produces **one output**. Think of it like a little calculator that sits on the ground.

Here is how it is oriented:

- **Back (rear):** This is the main input. Signal comes in from behind.
- **Left and right sides:** These are the side inputs. They modify what happens to the main signal.
- **Front:** This is the output. The result comes out here.

You can tell which end is which by the two torches: the **back** has two small torches, and the **front** has one single torch (which is either dark or lit depending on the mode).

## The Two Modes

Right-click a comparator to switch between modes. You can see which mode you are in by looking at the front torch:

### Compare Mode (front torch is OFF / dark)

This is the default. The comparator asks: **"Is my rear signal at least as strong as the strongest side signal?"**

- If YES: it passes the rear signal through unchanged.
- If NO: it outputs nothing (signal 0).

Example: Rear = 10, Side = 5. Since 10 is bigger than 5, output = 10.
Example: Rear = 10, Side = 12. Since 12 is bigger than 10, output = 0 (blocked).

Compare mode is like a gate -- the side signal decides whether to let the rear signal through or not.

### Subtract Mode (front torch is ON / lit)

This is the one you are asking about. The comparator does simple **subtraction**:

**output = rear signal - strongest side signal**

If the answer would be negative, it just outputs 0 (it never goes below zero).

That is literally it. It is subtraction.

## Subtract Mode Examples

Let me walk through some concrete numbers:

| Rear Signal | Side Signal | Math | Output |
|------------|-------------|------|--------|
| 15 | 0 | 15 - 0 | **15** |
| 15 | 5 | 15 - 5 | **10** |
| 15 | 10 | 15 - 10 | **5** |
| 15 | 15 | 15 - 15 | **0** |
| 10 | 3 | 10 - 3 | **7** |
| 10 | 12 | 10 - 12 would be -2, but... | **0** |

See? The side input "eats away" at the rear signal. The stronger the side input, the weaker the output.

## Where Does Signal Strength Come From?

You might be wondering: "OK, but how do I get a signal of 10 vs 15?" Here are the key facts:

- **Levers, buttons, torches** all output signal strength **15** (the maximum).
- **Redstone dust loses 1 strength per block** it travels. So if you run dust 5 blocks from a lever, the signal at the end is 15 - 5 = **10**.
- **Repeaters** reset signal strength back to **15**, regardless of what came in.
- **Comparators do NOT boost the signal.** They can only output what came in (or less). This is a key difference from repeaters.

So to get different signal strengths for testing, just run different lengths of redstone dust from your lever to the comparator inputs.

## A Quick Demo Build

I have generated an interactive HTML viewer (`comparator-demo.html`) with a tiny test circuit you can build in creative mode. Here is what it contains:

**Face east when building this.** The build is 2 layers:

- **Layer 1 (Y=0):** A row of 6 stone blocks as foundation, plus one stone block extending south from the middle.
- **Layer 2 (Y=1):** On top of the foundation:
  - Far left: a **lever** (this is the rear input)
  - Next: **redstone dust** carrying the signal east
  - Center: the **comparator** facing east (right-click once to set it to subtract mode -- the front torch should light up)
  - Next: two blocks of **redstone dust** carrying the output east
  - Far right: a **redstone lamp** (shows the output)
  - Extending south from the comparator: a **repeater** facing north (into the comparator's side), then a **lever** at the south end (this is the side input)

**How to test it:**

1. Turn ON the rear (left) lever. The lamp lights up -- full strength signal (15) passes through with nothing subtracted.
2. Now turn ON the side (bottom) lever. The repeater sends a strength-15 signal into the comparator's side. The comparator calculates 15 - 15 = 0. The lamp goes dark.
3. Turn OFF the side lever again. Lamp comes back on.

**To see partial subtraction:** Remove the repeater from the side path and replace it with several blocks of redstone dust. The longer the dust path, the weaker the side signal (it loses 1 per block), so less gets subtracted, and the lamp stays brighter.

## Why Subtract Mode Is Useful

Here are some real things people build with subtract mode:

- **Detecting how full a container is.** A comparator can read the contents of a chest, barrel, or hopper behind it and output a signal proportional to how full it is (0 = empty, 15 = full). By subtracting a threshold with the side input, you can trigger something only when a container reaches a specific fill level.
- **Item sorters.** The standard hopper-based item sorter uses a comparator reading a hopper's fill level. When the right items accumulate, the comparator signal passes a threshold and unlocks the output hopper.
- **Combination locks.** By feeding specific signal strengths into comparators and checking if the subtraction yields exactly the right value, you can build password-protected doors.
- **Analog circuits.** Unlike most redstone that is just "on or off," comparators let you work with the full 0-15 range of signal strength. This opens up dimmer switches, volume controls, and other graduated outputs.

## Common Mistakes

1. **Forgetting which end is which.** The two-torch side is the BACK (input). The single-torch side is the FRONT (output). Place the comparator while facing the direction you want the signal to flow.
2. **Not switching to subtract mode.** It defaults to compare mode. Right-click once to toggle. Check for the lit front torch.
3. **Expecting it to boost signals.** Unlike a repeater, a comparator never outputs more than what came in from the rear. It can only reduce or pass through.
4. **Side inputs from both sides.** If you have signals coming into BOTH the left and right sides, the comparator uses whichever is stronger. It does not add them together.

## Quick Reference

| Mode | Front Torch | Formula | In Plain English |
|------|-------------|---------|-----------------|
| Compare | OFF | If rear >= max(sides): output = rear. Else: output = 0 | "Let the signal through only if it is stronger than the side" |
| Subtract | ON | output = rear - max(sides), minimum 0 | "Reduce the signal by the side amount" |

The comparator also adds a fixed delay of 1 redstone tick (0.1 seconds) to any signal passing through it. This is not configurable (unlike repeaters where you can right-click to change the delay).

Hope that clears things up! Try building the demo -- playing with different dust lengths on the side input makes the subtraction really intuitive once you see the lamp dimming in real time.
