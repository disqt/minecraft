// Dust connection logic tests — run with: node test-dust-connections.js
//
// Based on Minecraft's RedStoneWireBlock.shouldConnectTo() and getRenderConnectionType():
//
// shouldConnectTo(state, direction):
//   - redstone_wire → always true
//   - repeater → only if facing == direction or facing.opposite == direction
//   - comparator → same as repeater
//   - observer → only if facing == direction (output face only)
//   - any isSignalSource block → true (redstone_block, torch, button, lever,
//     pressure_plate, tripwire_hook, daylight_detector, trapped_chest, target)
//   - everything else (stone, piston, dispenser, dropper) → false
//
// getRenderConnectionType(direction):
//   1. Same-level adjacent: shouldConnectTo() → "side"
//   2. If no same-level AND no opaque block above wire: check one step up → if wire → "up"
//   3. If no above: check one step down → if wire AND no opaque above lower → "side"
//   4. Otherwise → "none"
//
// UV mapping (proven from face corner analysis):
//   uvRot=0 → line0 runs E-W in world space
//   uvRot=1 → line0 runs N-S in world space

// === Block classification ===

// Blocks that are signal sources (isSignalSource() == true)
const SIGNAL_SOURCES = new Set([
  'redstone_block', 'redstone_torch', 'redstone_torch_wall',
  'lever', 'stone_button', 'oak_button', 'spruce_button',
  'birch_button', 'jungle_button', 'acacia_button', 'dark_oak_button',
  'mangrove_button', 'cherry_button', 'bamboo_button', 'crimson_button',
  'warped_button', 'polished_blackstone_button',
  'stone_pressure_plate', 'oak_pressure_plate', 'spruce_pressure_plate',
  'birch_pressure_plate', 'jungle_pressure_plate', 'acacia_pressure_plate',
  'dark_oak_pressure_plate', 'mangrove_pressure_plate', 'cherry_pressure_plate',
  'bamboo_pressure_plate', 'crimson_pressure_plate', 'warped_pressure_plate',
  'light_weighted_pressure_plate', 'heavy_weighted_pressure_plate',
  'tripwire_hook', 'daylight_detector', 'trapped_chest', 'target',
  'sculk_sensor', 'calibrated_sculk_sensor', 'lightning_rod',
]);

// Blocks with directional connections (front/back only)
const DIRECTIONAL_CONNECTORS = new Set(['repeater', 'comparator']);

const DUST_BLOCKS = new Set(['redstone_dust', 'redstone_dust_on']);

// Blocks that are opaque/solid (block cross-level connections)
// For simplicity: anything that's not dust, not air (null), and not a flat/transparent block
const TRANSPARENT_BLOCKS = new Set([
  ...DUST_BLOCKS,
  ...DIRECTIONAL_CONNECTORS,
  'redstone_torch', 'redstone_torch_wall',
  'lever', 'tripwire_hook',
  'rail', 'powered_rail', 'detector_rail', 'activator_rail',
]);

function isOpaque(block) {
  if (!block) return false;
  return !TRANSPARENT_BLOCKS.has(block) && !block.endsWith('_button') && !block.endsWith('_pressure_plate');
}

// Minecraft's shouldConnectTo logic
function shouldConnectTo(block, dir, facing) {
  if (!block) return false;
  if (DUST_BLOCKS.has(block)) return true;
  if (DIRECTIONAL_CONNECTORS.has(block)) {
    // Connects from front or back only
    if (!facing || !dir) return false;
    const opp = { north: 'south', south: 'north', east: 'west', west: 'east' };
    return facing === dir || opp[facing] === dir;
  }
  if (block === 'observer') {
    // Connects only from its output face (opposite of facing)
    const opp = { north: 'south', south: 'north', east: 'west', west: 'east', up: 'down', down: 'up' };
    return dir === opp[facing];
  }
  if (SIGNAL_SOURCES.has(block)) return dir != null;
  return false;
}

// The direction from (x,y,z) toward (x+dx,y,z+dz)
function deltaToDir(dx, dz) {
  if (dz < 0) return 'north';
  if (dz > 0) return 'south';
  if (dx > 0) return 'east';
  if (dx < 0) return 'west';
  return null;
}

// Full connection resolver per Minecraft's getRenderConnectionType
// Returns array of { tex, uvRot } faces for a dust block's UP face.
function resolveDustTextures(x, y, z, voxels) {
  function getBlock(bx, by, bz) {
    const v = voxels.get(`${bx},${by},${bz}`);
    return v ? v.block : null;
  }
  function getFacing(bx, by, bz) {
    const v = voxels.get(`${bx},${by},${bz}`);
    return v ? v.dir : null;
  }

  function connectsInDirection(dx, dz) {
    const dir = deltaToDir(dx, dz);
    const oppDir = deltaToDir(-dx, -dz);

    // 1. Same-level: shouldConnectTo(adjacent, oppositeDirection)
    const adjBlock = getBlock(x + dx, y, z + dz);
    const adjFacing = getFacing(x + dx, y, z + dz);
    if (shouldConnectTo(adjBlock, oppDir, adjFacing)) return true;

    // 2. Up one step: only if no opaque block directly above this wire
    const aboveBlock = getBlock(x, y + 1, z);
    if (!isOpaque(aboveBlock)) {
      const upBlock = getBlock(x + dx, y + 1, z + dz);
      if (DUST_BLOCKS.has(upBlock)) return true;
    }

    // 3. Down one step: only if no opaque block above the lower wire
    //    (the block at our level in that direction)
    const sameLevelBlock = getBlock(x + dx, y, z + dz);
    if (!isOpaque(sameLevelBlock)) {
      const downBlock = getBlock(x + dx, y - 1, z + dz);
      if (DUST_BLOCKS.has(downBlock)) return true;
    }

    return false;
  }

  const n = connectsInDirection(0, -1);
  const s = connectsInDirection(0, 1);
  const e = connectsInDirection(1, 0);
  const w = connectsInDirection(-1, 0);

  const faces = [];
  if (n || s) faces.push({ tex: 'redstone_dust_line0', uvRot: 1 });
  if (e || w) faces.push({ tex: 'redstone_dust_line0', uvRot: 0 });
  if (faces.length === 0) faces.push({ tex: 'redstone_dust_dot', uvRot: 0 });
  return faces;
}

// ─── Test runner ───

let pass = 0, fail = 0, total = 0;

function test(name, fn) {
  total++;
  try {
    fn();
    console.log(`  PASS: ${name}`);
    pass++;
  } catch (e) {
    console.log(`  FAIL: ${name}`);
    console.log(`        ${e.message}`);
    fail++;
  }
}

function eq(actual, expected, msg) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`${msg || ''} got ${a}, expected ${b}`);
}

function makeVoxels(entries) {
  const m = new Map();
  for (const e of entries) {
    const [x, y, z] = e;
    const block = e[3] || 'redstone_dust';
    const dir = e[4] || null;
    m.set(`${x},${y},${z}`, { block, dir });
  }
  return m;
}

const EW = [{ tex: 'redstone_dust_line0', uvRot: 0 }];
const NS = [{ tex: 'redstone_dust_line0', uvRot: 1 }];
const CROSS = [{ tex: 'redstone_dust_line0', uvRot: 1 }, { tex: 'redstone_dust_line0', uvRot: 0 }];
const DOT = [{ tex: 'redstone_dust_dot', uvRot: 0 }];

// ─── Straight lines ───
console.log("\n=== Straight lines ===");

test("EW line — middle", () => {
  const v = makeVoxels([[0,0,0], [1,0,0], [2,0,0]]);
  eq(resolveDustTextures(1, 0, 0, v), EW);
});

test("NS line — middle", () => {
  const v = makeVoxels([[0,0,0], [0,0,1], [0,0,2]]);
  eq(resolveDustTextures(0, 0, 1, v), NS);
});

// ─── Single connections ───
console.log("\n=== Single connections ===");

test("Single E", () => {
  eq(resolveDustTextures(0, 0, 0, makeVoxels([[0,0,0], [1,0,0]])), EW);
});
test("Single N", () => {
  eq(resolveDustTextures(0, 0, 1, makeVoxels([[0,0,0], [0,0,1]])), NS);
});

// ─── L-bends (overlapping faces) ───
console.log("\n=== L-bends ===");

test("L-bend N+E → two faces", () => {
  const v = makeVoxels([[1,0,0], [1,0,1], [2,0,1]]);
  eq(resolveDustTextures(1, 0, 1, v), CROSS);
});
test("L-bend S+W → two faces", () => {
  const v = makeVoxels([[1,0,1], [1,0,2], [0,0,1]]);
  eq(resolveDustTextures(1, 0, 1, v), CROSS);
});

// ─── T-junctions and crosses ───
console.log("\n=== T-junctions and crosses ===");

test("T-junction N+S+E", () => {
  const v = makeVoxels([[1,0,0], [1,0,1], [1,0,2], [2,0,1]]);
  eq(resolveDustTextures(1, 0, 1, v), CROSS);
});
test("Full cross", () => {
  const v = makeVoxels([[1,0,0], [0,0,1], [1,0,1], [2,0,1], [1,0,2]]);
  eq(resolveDustTextures(1, 0, 1, v), CROSS);
});

// ─── Isolated ───
console.log("\n=== Isolated ===");

test("Isolated → dot", () => {
  eq(resolveDustTextures(5, 0, 5, makeVoxels([[5,0,5]])), DOT);
});

// ─── Signal source connections ───
console.log("\n=== Signal source connections (same level) ===");

test("Connects to redstone_block", () => {
  const v = makeVoxels([[0,0,0], [1,0,0,'redstone_block']]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});
test("Connects to lever", () => {
  const v = makeVoxels([[0,0,0], [0,0,1,'lever']]);
  eq(resolveDustTextures(0, 0, 0, v), NS);
});
test("Connects to redstone_torch", () => {
  const v = makeVoxels([[0,0,0], [1,0,0,'redstone_torch']]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});

// ─── Non-signal-source blocks: NO connection ───
console.log("\n=== Non-signal sources (should NOT connect) ===");

test("Does NOT connect to stone", () => {
  eq(resolveDustTextures(0, 0, 0, makeVoxels([[0,0,0], [1,0,0,'stone']])), DOT);
});
test("Does NOT connect to piston", () => {
  eq(resolveDustTextures(0, 0, 0, makeVoxels([[0,0,0], [1,0,0,'piston']])), DOT);
});
test("Does NOT connect to dispenser", () => {
  eq(resolveDustTextures(0, 0, 0, makeVoxels([[0,0,0], [1,0,0,'dispenser']])), DOT);
});
test("Does NOT connect to dropper", () => {
  eq(resolveDustTextures(0, 0, 0, makeVoxels([[0,0,0], [1,0,0,'dropper']])), DOT);
});
test("Does NOT connect to sticky_piston", () => {
  eq(resolveDustTextures(0, 0, 0, makeVoxels([[0,0,0], [1,0,0,'sticky_piston']])), DOT);
});

// ─── Directional connectors (repeater/comparator) ───
console.log("\n=== Directional connectors ===");

test("Repeater facing toward wire → connects", () => {
  // Repeater at (1,0,0) facing west (toward wire at 0,0,0)
  // Wire is west of repeater, repeater faces west → connects
  const v = makeVoxels([[0,0,0], [1,0,0,'repeater','west']]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});
test("Repeater facing away from wire → connects (back)", () => {
  // Repeater at (1,0,0) facing east (away from wire at 0,0,0)
  // Wire is west, repeater faces east → opposite matches → connects
  const v = makeVoxels([[0,0,0], [1,0,0,'repeater','east']]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});
test("Repeater facing perpendicular → does NOT connect", () => {
  // Repeater at (1,0,0) facing north, wire is to its west
  const v = makeVoxels([[0,0,0], [1,0,0,'repeater','north']]);
  eq(resolveDustTextures(0, 0, 0, v), DOT);
});

test("Observer output face → connects", () => {
  // Observer at (1,0,0) facing east → output is west → wire at (0,0,0) is west → connects
  const v = makeVoxels([[0,0,0], [1,0,0,'observer','east']]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});
test("Observer input face → does NOT connect", () => {
  // Observer at (1,0,0) facing west → output is east → wire at (0,0,0) is west (input) → no
  const v = makeVoxels([[0,0,0], [1,0,0,'observer','west']]);
  eq(resolveDustTextures(0, 0, 0, v), DOT);
});

// ─── Cross-level connections ───
console.log("\n=== Cross-level: up one step ===");

test("Up-east: connects when no opaque above wire", () => {
  const v = makeVoxels([[0,0,0], [1,1,0]]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});
test("Up-east: BLOCKED by opaque block above wire", () => {
  const v = makeVoxels([[0,0,0], [1,1,0], [0,1,0,'stone']]);
  eq(resolveDustTextures(0, 0, 0, v), DOT);
});
test("Up-north: connects when clear", () => {
  const v = makeVoxels([[0,0,1], [0,1,0]]);
  eq(resolveDustTextures(0, 0, 1, v), NS);
});
test("Up: dust above wire is NOT opaque → still connects", () => {
  const v = makeVoxels([[0,0,0], [0,1,0], [1,1,0]]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});
test("Up: repeater above wire is NOT opaque → still connects", () => {
  const v = makeVoxels([[0,0,0], [0,1,0,'repeater','north'], [1,1,0]]);
  eq(resolveDustTextures(0, 0, 0, v), EW);
});

console.log("\n=== Cross-level: down one step ===");

test("Down-east: connects when no opaque at same level", () => {
  // Wire at (0,1,0), lower wire at (1,0,0), nothing at (1,1,0)
  const v = makeVoxels([[0,1,0], [1,0,0]]);
  eq(resolveDustTextures(0, 1, 0, v), EW);
});
test("Down-east: BLOCKED by opaque block at same level in direction", () => {
  // Wire at (0,1,0), lower wire at (1,0,0), stone at (1,1,0) blocks
  const v = makeVoxels([[0,1,0], [1,0,0], [1,1,0,'stone']]);
  eq(resolveDustTextures(0, 1, 0, v), DOT);
});
test("Down: transparent block at same level does NOT block", () => {
  const v = makeVoxels([[0,1,0], [1,0,0], [1,1,0,'redstone_torch']]);
  eq(resolveDustTextures(0, 1, 0, v), EW);
});

console.log("\n=== Cross-level: only dust climbs ===");

test("Non-dust block one step up → no cross-level", () => {
  const v = makeVoxels([[0,0,0], [1,1,0,'redstone_block']]);
  eq(resolveDustTextures(0, 0, 0, v), DOT);
});
test("Non-dust block one step down → no cross-level", () => {
  const v = makeVoxels([[0,1,0], [1,0,0,'redstone_block']]);
  eq(resolveDustTextures(0, 1, 0, v), DOT);
});

// ─── Same-level takes priority over cross-level ───
console.log("\n=== Priority: same-level before cross-level ===");

test("Same-level connection found → skip cross-level check", () => {
  // Same-level stone at (1,0,0) is not connectable, but there IS wire at same level further
  // Actually test: same-level wire exists, also wire one up — both should count
  const v = makeVoxels([[0,0,0], [1,0,0], [0,1,0]]);
  // East connects (same-level wire), should show EW
  // No north/south connections
  eq(resolveDustTextures(0, 0, 0, v), EW);
});

// ─── Summary ───
console.log(`\n${pass}/${total} passed` + (fail > 0 ? ` (${fail} FAILED)` : ''));
if (fail > 0) process.exit(1);
