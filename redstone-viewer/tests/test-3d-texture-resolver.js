#!/usr/bin/env node
// Tests for the 3D viewer's texture resolver and UV rotation tables.
// Run: node redstone-viewer/tests/test-3d-texture-resolver.js
//
// These tests validate that:
// 1. resolve3DTexture picks the correct texture for every (block, dir, face) combo
// 2. TOP_UV_ROT / BOTTOM_UV_ROT / SIDE_UV_ROT values match algorithmic computation
// 3. The algorithmic computation itself is correct (arrow/grain points toward blockDir)

// ============================================================
// Copy of production constants (keep in sync with 3d-new-code.js / 3d-new-facemap.js)
// ============================================================

const OPPOSITES = { north: 'south', south: 'north', east: 'west', west: 'east', up: 'down', down: 'up' };

const SIDE_ROTATE_BLOCKS = new Set(['piston', 'sticky_piston', 'piston_head']);

const TOP_UV_ROT = { north: 1, south: 3, east: 2, west: 0 };
const BOTTOM_UV_ROT = { north: 1, south: 3, east: 0, west: 2 };

const SIDE_UV_ROT = {
  up:    { north: 1, south: 1, east: 0, west: 0 },
  down:  { north: 3, south: 3, east: 2, west: 2 },
  north: { east: 1, west: 3, up: 1, down: 1 },
  south: { east: 3, west: 1, up: 3, down: 3 },
  east:  { north: 0, south: 2, up: 2, down: 0 },
  west:  { north: 2, south: 0, up: 0, down: 2 },
};

const FACE_MAP_3D = {
  piston:         { front: 'piston_top',        back: 'piston_bottom', side: 'piston_side' },
  sticky_piston:  { front: 'piston_top_sticky', back: 'piston_bottom', side: 'piston_side' },
  piston_head:    { front: 'piston_top',        back: 'piston_inner',  side: 'piston_side' },
  observer:       { front: 'observer_front', back: 'observer_back', top: 'observer_top', bottom: 'observer_top', side: 'observer_side' },
  dispenser:      { front: 'dispenser_front_vertical', back: 'furnace_top', top: 'furnace_top', bottom: 'furnace_top', side: 'furnace_side' },
  dropper:        { front: 'dropper_front_vertical',   back: 'furnace_top', top: 'furnace_top', bottom: 'furnace_top', side: 'furnace_side' },
  furnace:        { front: 'furnace_front', back: 'furnace_side', top: 'furnace_top', bottom: 'furnace_top', side: 'furnace_side' },
  hopper:         { top: 'hopper_top', side: 'hopper_outside', bottom: 'hopper_outside' },
};

// Simulated BLOCKS — only directional flag matters for the resolver
const BLOCKS = {
  piston:         { directional: true },
  sticky_piston:  { directional: true },
  piston_head:    { directional: true },
  observer:       { directional: true },
  dispenser:      { directional: true },
  dropper:        { directional: true },
  furnace:        { directional: true },
  hopper:         { directional: true },
  repeater:       { directional: true },
  comparator:     { directional: true },
  // Non-directional examples
  stone:          {},
  oak_log:        {},
};

// ============================================================
// Production function under test (exact copy from 3d-new-code.js)
// ============================================================

function resolve3DTexture(block, blockDir, worldFace) {
  const faces = FACE_MAP_3D[block];
  if (!faces) return { tex: block, uvRot: 0 };

  const fb = faces.all || block;
  const isDirectional = BLOCKS[block]?.directional && blockDir;

  if (isDirectional) {
    if (worldFace === blockDir) {
      return { tex: faces.front || faces.top || fb, uvRot: 0 };
    }
    if (worldFace === OPPOSITES[blockDir]) {
      return { tex: faces.back || faces.bottom || faces.top || fb, uvRot: 0 };
    }
    if (worldFace === 'up' && faces.top) {
      return { tex: faces.top, uvRot: TOP_UV_ROT[blockDir] || 0 };
    }
    if (worldFace === 'down' && faces.bottom) {
      return { tex: faces.bottom, uvRot: BOTTOM_UV_ROT[blockDir] || 0 };
    }
    const tex = faces.side || fb;
    const uvRot = SIDE_ROTATE_BLOCKS.has(block)
      ? (SIDE_UV_ROT[blockDir]?.[worldFace] || 0)
      : 0;
    return { tex, uvRot };
  }

  if (worldFace === 'up') return { tex: faces.top || fb, uvRot: 0 };
  if (worldFace === 'down') return { tex: faces.bottom || faces.top || fb, uvRot: 0 };
  return { tex: faces.side || faces.top || fb, uvRot: 0 };
}

// ============================================================
// Face geometry (same as production code)
// ============================================================

const faceData = {
  west:  { corners: [[0,1,0],[0,0,0],[0,1,1],[0,0,1]] },
  east:  { corners: [[1,1,1],[1,0,1],[1,1,0],[1,0,0]] },
  down:  { corners: [[1,0,1],[0,0,1],[1,0,0],[0,0,0]] },
  up:    { corners: [[0,1,1],[1,1,1],[0,1,0],[1,1,0]] },
  north: { corners: [[1,0,0],[0,0,0],[1,1,0],[0,1,0]] },
  south: { corners: [[0,0,1],[1,0,1],[0,1,1],[1,1,1]] },
};

const uvSets = [
  [[0,1],[0,0],[1,1],[1,0]],  // 0°
  [[0,0],[1,0],[0,1],[1,1]],  // 90° CW
  [[1,0],[1,1],[0,0],[0,1]],  // 180°
  [[1,1],[0,1],[1,0],[0,0]],  // 270°
];

const DIR_VEC = {
  up: [0,1,0], down: [0,-1,0],
  east: [1,0,0], west: [-1,0,0],
  north: [0,0,-1], south: [0,0,1],
};

const ALL_FACES = ['north', 'south', 'east', 'west', 'up', 'down'];
const ALL_DIRS = ['north', 'south', 'east', 'west', 'up', 'down'];
const NSEW_DIRS = ['north', 'south', 'east', 'west'];

// ============================================================
// Algorithmic UV rotation computation (ground truth)
// ============================================================

/**
 * For a given world face and target direction, compute which uvRot
 * places the texture V=1 edge (arrow/grain) closest to targetDir.
 */
function computeUVRot(worldFace, targetDir) {
  const corners = faceData[worldFace].corners;
  const targetVec = DIR_VEC[targetDir];
  let bestRot = 0, bestScore = -Infinity;

  for (let rot = 0; rot < 4; rot++) {
    const uvs = uvSets[rot];
    let score = 0;
    for (let i = 0; i < 4; i++) {
      if (uvs[i][1] >= 0.5) { // V=1 corners
        const pos = corners[i];
        score += pos[0] * targetVec[0] + pos[1] * targetVec[1] + pos[2] * targetVec[2];
      }
    }
    if (score > bestScore) { bestScore = score; bestRot = rot; }
  }
  return bestRot;
}

// ============================================================
// Test runner
// ============================================================

let passed = 0, failed = 0, total = 0;

function assert(condition, msg) {
  total++;
  if (condition) {
    passed++;
  } else {
    failed++;
    console.error(`  FAIL: ${msg}`);
  }
}

function assertEqual(actual, expected, msg) {
  total++;
  if (actual === expected) {
    passed++;
  } else {
    failed++;
    console.error(`  FAIL: ${msg} — expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

// ============================================================
// Test 1: TOP_UV_ROT matches algorithmic computation
// ============================================================
console.log('\n--- Test 1: TOP_UV_ROT correctness ---');
for (const blockDir of NSEW_DIRS) {
  const expected = computeUVRot('up', blockDir);
  assertEqual(TOP_UV_ROT[blockDir], expected,
    `TOP_UV_ROT[${blockDir}] should be ${expected}`);
}

// ============================================================
// Test 2: BOTTOM_UV_ROT matches algorithmic computation
// ============================================================
console.log('\n--- Test 2: BOTTOM_UV_ROT correctness ---');
for (const blockDir of NSEW_DIRS) {
  const expected = computeUVRot('down', blockDir);
  assertEqual(BOTTOM_UV_ROT[blockDir], expected,
    `BOTTOM_UV_ROT[${blockDir}] should be ${expected}`);
}

// ============================================================
// Test 3: SIDE_UV_ROT matches algorithmic computation
// ============================================================
console.log('\n--- Test 3: SIDE_UV_ROT correctness ---');
for (const blockDir of ALL_DIRS) {
  for (const worldFace of ALL_FACES) {
    if (worldFace === blockDir || worldFace === OPPOSITES[blockDir]) continue;
    const expected = computeUVRot(worldFace, blockDir);
    const actual = SIDE_UV_ROT[blockDir]?.[worldFace];
    assertEqual(actual, expected,
      `SIDE_UV_ROT[${blockDir}][${worldFace}] should be ${expected}`);
  }
}

// ============================================================
// Test 4: Piston texture selection (all 6 directions × 6 faces)
// ============================================================
console.log('\n--- Test 4: Piston texture selection ---');
for (const block of ['piston', 'sticky_piston', 'piston_head']) {
  const faces = FACE_MAP_3D[block];
  for (const dir of ALL_DIRS) {
    for (const face of ALL_FACES) {
      const { tex } = resolve3DTexture(block, dir, face);
      if (face === dir) {
        // Front face → push face texture
        assertEqual(tex, faces.front, `${block}:${dir} front face (${face})`);
      } else if (face === OPPOSITES[dir]) {
        // Back face → back texture
        assertEqual(tex, faces.back, `${block}:${dir} back face (${face})`);
      } else {
        // Side face → side texture
        assertEqual(tex, faces.side, `${block}:${dir} side face (${face})`);
      }
    }
  }
}

// ============================================================
// Test 5: Piston SIDE_UV_ROT applied on side faces, not front/back
// ============================================================
console.log('\n--- Test 5: Piston side UV rotation applied correctly ---');
for (const block of ['piston', 'sticky_piston']) {
  for (const dir of ALL_DIRS) {
    for (const face of ALL_FACES) {
      const { uvRot } = resolve3DTexture(block, dir, face);
      if (face === dir || face === OPPOSITES[dir]) {
        // Front/back → no rotation
        assertEqual(uvRot, 0, `${block}:${dir} ${face} (front/back) should have uvRot=0`);
      } else {
        // Side → should use SIDE_UV_ROT
        const expected = SIDE_UV_ROT[dir]?.[face] || 0;
        assertEqual(uvRot, expected, `${block}:${dir} ${face} (side) uvRot`);
      }
    }
  }
}

// ============================================================
// Test 6: Observer texture selection
// ============================================================
console.log('\n--- Test 6: Observer texture selection ---');
for (const dir of ALL_DIRS) {
  for (const face of ALL_FACES) {
    const { tex } = resolve3DTexture('observer', dir, face);
    if (face === dir) {
      assertEqual(tex, 'observer_front', `observer:${dir} front face (${face})`);
    } else if (face === OPPOSITES[dir]) {
      assertEqual(tex, 'observer_back', `observer:${dir} back face (${face})`);
    } else if (face === 'up') {
      assertEqual(tex, 'observer_top', `observer:${dir} top face`);
    } else if (face === 'down') {
      assertEqual(tex, 'observer_top', `observer:${dir} bottom face`);
    } else {
      assertEqual(tex, 'observer_side', `observer:${dir} side face (${face})`);
    }
  }
}

// ============================================================
// Test 7: Observer TOP_UV_ROT applied correctly on top face
// ============================================================
console.log('\n--- Test 7: Observer top/bottom UV rotation ---');
for (const dir of NSEW_DIRS) {
  // Top face
  const topResult = resolve3DTexture('observer', dir, 'up');
  assertEqual(topResult.uvRot, TOP_UV_ROT[dir],
    `observer:${dir} top uvRot should be TOP_UV_ROT[${dir}]=${TOP_UV_ROT[dir]}`);

  // Bottom face
  const bottomResult = resolve3DTexture('observer', dir, 'down');
  assertEqual(bottomResult.uvRot, BOTTOM_UV_ROT[dir],
    `observer:${dir} bottom uvRot should be BOTTOM_UV_ROT[${dir}]=${BOTTOM_UV_ROT[dir]}`);
}

// For up/down facing observers, top/bottom are front/back (no TOP_UV_ROT)
for (const dir of ['up', 'down']) {
  const topResult = resolve3DTexture('observer', dir, 'up');
  const bottomResult = resolve3DTexture('observer', dir, 'down');
  if (dir === 'up') {
    // up face IS front face → should get observer_front, uvRot=0
    assertEqual(topResult.tex, 'observer_front', `observer:up top face is front`);
    assertEqual(topResult.uvRot, 0, `observer:up top face uvRot=0`);
    assertEqual(bottomResult.tex, 'observer_back', `observer:up bottom face is back`);
  } else {
    assertEqual(bottomResult.tex, 'observer_front', `observer:down bottom face is front`);
    assertEqual(bottomResult.uvRot, 0, `observer:down bottom face uvRot=0`);
    assertEqual(topResult.tex, 'observer_back', `observer:up top face is back`);
  }
}

// ============================================================
// Test 8: Observer side faces have no UV rotation (observer_side is symmetric)
// ============================================================
console.log('\n--- Test 8: Observer side UV rotation (should be 0) ---');
for (const dir of ALL_DIRS) {
  for (const face of ALL_FACES) {
    if (face === dir || face === OPPOSITES[dir]) continue;
    if (face === 'up' || face === 'down') continue;
    const { uvRot } = resolve3DTexture('observer', dir, face);
    assertEqual(uvRot, 0, `observer:${dir} side ${face} uvRot should be 0 (not in SIDE_ROTATE_BLOCKS)`);
  }
}

// ============================================================
// Test 9: Dispenser/dropper texture selection
// ============================================================
console.log('\n--- Test 9: Dispenser/dropper textures ---');
for (const block of ['dispenser', 'dropper']) {
  const faces = FACE_MAP_3D[block];
  for (const dir of ALL_DIRS) {
    const front = resolve3DTexture(block, dir, dir);
    assertEqual(front.tex, faces.front, `${block}:${dir} front`);

    const back = resolve3DTexture(block, dir, OPPOSITES[dir]);
    assertEqual(back.tex, faces.back, `${block}:${dir} back`);
  }
}

// ============================================================
// Test 10: Non-directional blocks get no UV rotation
// ============================================================
console.log('\n--- Test 10: Non-directional blocks ---');
for (const face of ALL_FACES) {
  const { uvRot } = resolve3DTexture('stone', null, face);
  assertEqual(uvRot, 0, `stone ${face} uvRot=0 (no FACE_MAP_3D)`);
}

// ============================================================
// Test 11: Blocks without FACE_MAP_3D return block name as texture
// ============================================================
console.log('\n--- Test 11: Fallback texture ---');
{
  const { tex } = resolve3DTexture('stone', null, 'up');
  assertEqual(tex, 'stone', `stone returns own name as texture`);
}

// ============================================================
// Test 12: Arrow direction correctness (integration test)
// For each directional block with asymmetric top texture, verify
// that the computed uvRot actually makes the arrow point toward blockDir.
// ============================================================
console.log('\n--- Test 12: Arrow points toward blockDir (integration) ---');

function arrowDirection(worldFace, uvRot) {
  // Given a world face and uvRot, compute which world direction the
  // texture V=1 edge (arrow) points toward.
  const corners = faceData[worldFace].corners;
  const uvs = uvSets[uvRot % 4];

  let highV = [0, 0, 0], lowV = [0, 0, 0];
  let hc = 0, lc = 0;
  for (let i = 0; i < 4; i++) {
    if (uvs[i][1] >= 0.5) {
      highV[0] += corners[i][0]; highV[1] += corners[i][1]; highV[2] += corners[i][2]; hc++;
    } else {
      lowV[0] += corners[i][0]; lowV[1] += corners[i][1]; lowV[2] += corners[i][2]; lc++;
    }
  }
  const dir = [highV[0]/hc - lowV[0]/lc, highV[1]/hc - lowV[1]/lc, highV[2]/hc - lowV[2]/lc];

  // Find best matching cardinal direction
  let best = null, bestDot = -Infinity;
  for (const [name, vec] of Object.entries(DIR_VEC)) {
    const dot = dir[0]*vec[0] + dir[1]*vec[1] + dir[2]*vec[2];
    if (dot > bestDot) { bestDot = dot; best = name; }
  }
  return best;
}

// Observer top arrow should point toward blockDir
for (const dir of NSEW_DIRS) {
  const { uvRot } = resolve3DTexture('observer', dir, 'up');
  const actual = arrowDirection('up', uvRot);
  assertEqual(actual, dir, `observer:${dir} top arrow should point ${dir}, got ${actual}`);
}

// Observer bottom arrow should point toward blockDir
for (const dir of NSEW_DIRS) {
  const { uvRot } = resolve3DTexture('observer', dir, 'down');
  const actual = arrowDirection('down', uvRot);
  assertEqual(actual, dir, `observer:${dir} bottom arrow should point ${dir}, got ${actual}`);
}

// Piston side grain should point toward blockDir
for (const block of ['piston', 'sticky_piston']) {
  for (const dir of ALL_DIRS) {
    for (const face of ALL_FACES) {
      if (face === dir || face === OPPOSITES[dir]) continue;
      const { uvRot } = resolve3DTexture(block, dir, face);
      const actual = arrowDirection(face, uvRot);
      assertEqual(actual, dir, `${block}:${dir} ${face} grain should point ${dir}, got ${actual}`);
    }
  }
}

// ============================================================
// Test 13: OPPOSITES table is symmetric and complete
// ============================================================
console.log('\n--- Test 13: OPPOSITES table ---');
for (const dir of ALL_DIRS) {
  assert(OPPOSITES[dir] !== undefined, `OPPOSITES[${dir}] defined`);
  assertEqual(OPPOSITES[OPPOSITES[dir]], dir, `OPPOSITES is symmetric for ${dir}`);
  assert(OPPOSITES[dir] !== dir, `OPPOSITES[${dir}] !== ${dir}`);
}

// ============================================================
// Test 14: SIDE_UV_ROT has entries for all valid (blockDir, worldFace) pairs
// ============================================================
console.log('\n--- Test 14: SIDE_UV_ROT completeness ---');
for (const blockDir of ALL_DIRS) {
  assert(SIDE_UV_ROT[blockDir] !== undefined, `SIDE_UV_ROT[${blockDir}] exists`);
  for (const face of ALL_FACES) {
    if (face === blockDir || face === OPPOSITES[blockDir]) continue;
    assert(SIDE_UV_ROT[blockDir][face] !== undefined,
      `SIDE_UV_ROT[${blockDir}][${face}] exists`);
  }
}

// ============================================================
// Summary
// ============================================================
console.log(`\n${'='.repeat(50)}`);
if (failed === 0) {
  console.log(`ALL ${total} TESTS PASSED`);
} else {
  console.log(`${failed} FAILED, ${passed} passed, ${total} total`);
  process.exit(1);
}
