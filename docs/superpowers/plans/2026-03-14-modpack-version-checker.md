# Modpack Version Checker Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Fabric client mod + Paper server plugin that notifies players when their modpack version is outdated, and update the prism-client skills to auto-generate changelogs.

**Architecture:** Fabric mod reads `modpack-version.txt` from the game directory and sends the version string over a `disqt:version` plugin messaging channel on server join. Paper plugin fetches `manifest.json` from disqt.com, listens for the version message, and sends Jamaica-colored MiniMessage chat notifications. Skill changes persist changelog summaries through the decision doc into the manifest.

**Tech Stack:** Java 21, Fabric API (networking), Paper API (plugin messaging, Adventure/MiniMessage), Gradle

**Spec:** `docs/superpowers/specs/2026-03-14-modpack-version-checker-design.md`

---

## File Structure

### New files

```
modpack-version-checker/
  paper-plugin/
    build.gradle.kts
    settings.gradle.kts
    gradle.properties
    src/main/java/com/disqt/version/
      DisqtVersionPlugin.java          # Plugin main: registers channel, starts fetcher
      ManifestFetcher.java             # Async HTTP manifest fetch + JSON parse + cache
      VersionListener.java             # PlayerJoinEvent + PluginMessageListener
    src/main/resources/
      paper-plugin.yml
      config.yml                       # Default config with MiniMessage templates
    src/test/java/com/disqt/version/
      ManifestFetcherTest.java         # Unit test for version extraction logic
  fabric-mod/
    build.gradle.kts
    settings.gradle.kts
    gradle.properties
    src/main/java/com/disqt/version/
      DisqtVersion.java                # Main entrypoint: registers payload type
      DisqtVersionClient.java          # Client entrypoint: reads file, sends on join
      VersionPayload.java              # CustomPayload record (raw UTF-8 bytes)
    src/main/resources/
      fabric.mod.json
```

### Modified files

```
plugins/minecraft-prism-client/skills/version-refresh/SKILL.md          # Add Step 5.5: write changelog summary
plugins/minecraft-prism-client/skills/version-refresh/executor-agent-spec.md  # Step 12d: include changelog in manifest
```

---

## Chunk 1: Paper Plugin

### Task 1: Paper plugin project scaffold

**Files:**
- Create: `modpack-version-checker/paper-plugin/build.gradle.kts`
- Create: `modpack-version-checker/paper-plugin/settings.gradle.kts`
- Create: `modpack-version-checker/paper-plugin/gradle.properties`
- Create: `modpack-version-checker/paper-plugin/src/main/resources/paper-plugin.yml`
- Create: `modpack-version-checker/paper-plugin/src/main/resources/config.yml`

- [ ] **Step 1: Create build.gradle.kts**

```kotlin
plugins {
    java
}

group = "com.disqt"
version = "1.0.0"

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(21))
}

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
}

dependencies {
    compileOnly("io.papermc.paper:paper-api:1.21.4-R0.1-SNAPSHOT")
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.jar {
    archiveBaseName.set("DisqtVersion")
}

tasks.test {
    useJUnitPlatform()
}
```

**Note:** The Paper API version `1.21.4-R0.1-SNAPSHOT` is a placeholder. Before building, verify the correct coordinate for MC 1.21.11 from `https://repo.papermc.io/repository/maven-public/io/papermc/paper/paper-api/`. Use the version that matches or is closest to MC 1.21.11.

- [ ] **Step 2: Create settings.gradle.kts**

```kotlin
rootProject.name = "DisqtVersion"
```

- [ ] **Step 3: Create gradle.properties**

```properties
group=com.disqt
version=1.0.0
```

- [ ] **Step 4: Create paper-plugin.yml**

```yaml
name: DisqtVersion
version: '1.0.0'
main: com.disqt.version.DisqtVersionPlugin
description: Notifies players when their modpack is outdated
author: disqt
api-version: '1.21'
```

- [ ] **Step 5: Create default config.yml**

```yaml
manifest-url: "https://disqt.com/minecraft/modpack/manifest.json"
refresh-minutes: 30
changelog-lines: 3
messages:
  outdated: "<black>[</black><green>D</green><gold>i</gold><black>s</black><green>q</green><gold>t</gold><black>]</black> <gray>Modpack update available:</gray> <aqua>v{latest}</aqua> <gray>-</gray> <green>disqt.com/minecraft</green>"
  changelog-line: "  <gray>- {line}</gray>"
  no-modpack: "<black>[</black><green>D</green><gold>i</gold><black>s</black><green>q</green><gold>t</gold><black>]</black> <gray>Get the modpack at</gray> <green>disqt.com/minecraft</green>"
```

- [ ] **Step 6: Generate Gradle wrapper**

```bash
cd modpack-version-checker/paper-plugin
gradle wrapper --gradle-version 8.12
```

If `gradle` is not installed, install it first (`sdk install gradle` via SDKMAN, `scoop install gradle`, or download from gradle.org).

- [ ] **Step 7: Verify scaffold compiles**

```bash
cd modpack-version-checker/paper-plugin
./gradlew build
```

Expected: BUILD SUCCESSFUL (no source yet, just verifies the build config resolves dependencies).

- [ ] **Step 8: Commit**

```bash
git add modpack-version-checker/paper-plugin/
git commit -m "feat: scaffold Paper plugin project for DisqtVersion"
```

---

### Task 2: ManifestFetcher with version extraction test

**Files:**
- Create: `modpack-version-checker/paper-plugin/src/main/java/com/disqt/version/ManifestFetcher.java`
- Create: `modpack-version-checker/paper-plugin/src/test/java/com/disqt/version/ManifestFetcherTest.java`

- [ ] **Step 1: Write failing test for extractVersion**

```java
package com.disqt.version;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class ManifestFetcherTest {

    @Test
    void extractVersion_fullFormat() {
        assertEquals("2.2", ManifestFetcher.extractVersion("1.21.11 v2.2"));
    }

    @Test
    void extractVersion_plainVersion() {
        assertEquals("2.2", ManifestFetcher.extractVersion("2.2"));
    }

    @Test
    void extractVersion_withWhitespace() {
        assertEquals("2.2", ManifestFetcher.extractVersion("1.21.11 v2.2 "));
    }

    @Test
    void extractVersion_majorMinorPatch() {
        assertEquals("2.2.1", ManifestFetcher.extractVersion("1.21.11 v2.2.1"));
    }

    @Test
    void parseChangelog_validArray() {
        String json = """
            {
              "latest": {
                "version": "1.21.11 v2.2",
                "changelog": ["Fixed shaders", "Added Ping Wheel"]
              }
            }
            """;
        List<String> changelog = ManifestFetcher.parseChangelog(json);
        assertEquals(List.of("Fixed shaders", "Added Ping Wheel"), changelog);
    }

    @Test
    void parseChangelog_missingField() {
        String json = """
            {
              "latest": {
                "version": "1.21.11 v2.2"
              }
            }
            """;
        List<String> changelog = ManifestFetcher.parseChangelog(json);
        assertTrue(changelog.isEmpty());
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd modpack-version-checker/paper-plugin
./gradlew test
```

Expected: FAIL — `ManifestFetcher` class does not exist yet.

- [ ] **Step 3: Implement ManifestFetcher**

```java
package com.disqt.version;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.bukkit.Bukkit;
import org.bukkit.plugin.Plugin;
import org.bukkit.scheduler.BukkitTask;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.logging.Level;

public class ManifestFetcher {
    private final Plugin plugin;
    private final String manifestUrl;
    private final int refreshMinutes;
    private final HttpClient httpClient;

    private volatile String latestVersion = null;
    private volatile List<String> changelog = Collections.emptyList();
    private BukkitTask refreshTask;

    public ManifestFetcher(Plugin plugin, String manifestUrl, int refreshMinutes) {
        this.plugin = plugin;
        this.manifestUrl = manifestUrl;
        this.refreshMinutes = refreshMinutes;
        this.httpClient = HttpClient.newHttpClient();
    }

    public void start() {
        Bukkit.getScheduler().runTaskAsynchronously(plugin, this::fetch);
        long ticks = refreshMinutes * 60L * 20L;
        refreshTask = Bukkit.getScheduler().runTaskTimerAsynchronously(
            plugin, this::fetch, ticks, ticks
        );
    }

    public void stop() {
        if (refreshTask != null) refreshTask.cancel();
    }

    private void fetch() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI(manifestUrl))
                .timeout(Duration.ofSeconds(10))
                .header("User-Agent", "DisqtVersion/1.0")
                .GET()
                .build();

            HttpResponse<String> response = httpClient.send(
                request, HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() != 200) {
                plugin.getLogger().warning("Manifest fetch failed: HTTP " + response.statusCode());
                return;
            }

            JsonObject json = JsonParser.parseString(response.body()).getAsJsonObject();
            JsonObject latest = json.getAsJsonObject("latest");

            latestVersion = extractVersion(latest.get("version").getAsString());
            changelog = parseChangelog(response.body());

            plugin.getLogger().info("Manifest loaded: latest version " + latestVersion);
        } catch (Exception e) {
            plugin.getLogger().log(Level.WARNING, "Failed to fetch manifest", e);
        }
    }

    static String extractVersion(String fullVersion) {
        int lastV = fullVersion.lastIndexOf('v');
        if (lastV >= 0 && lastV < fullVersion.length() - 1) {
            return fullVersion.substring(lastV + 1).trim();
        }
        return fullVersion.trim();
    }

    static List<String> parseChangelog(String jsonBody) {
        try {
            JsonObject json = JsonParser.parseString(jsonBody).getAsJsonObject();
            JsonObject latest = json.getAsJsonObject("latest");
            if (latest.has("changelog") && latest.get("changelog").isJsonArray()) {
                JsonArray arr = latest.getAsJsonArray("changelog");
                List<String> lines = new ArrayList<>();
                for (int i = 0; i < arr.size(); i++) {
                    lines.add(arr.get(i).getAsString());
                }
                return Collections.unmodifiableList(lines);
            }
        } catch (Exception ignored) {}
        return Collections.emptyList();
    }

    public String getLatestVersion() {
        return latestVersion;
    }

    public List<String> getChangelog() {
        return changelog;
    }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd modpack-version-checker/paper-plugin
./gradlew test
```

Expected: all 6 tests PASS.

**Note:** The Bukkit/scheduler imports won't resolve in the test classpath since paper-api is `compileOnly`. The test only calls static methods (`extractVersion`, `parseChangelog`) which don't touch Bukkit. If the compiler complains about unresolved Bukkit imports during test compilation, add `testCompileOnly("io.papermc.paper:paper-api:...")` to build.gradle.kts, or extract the static methods into a separate utility class with no Bukkit imports.

- [ ] **Step 5: Commit**

```bash
git add modpack-version-checker/paper-plugin/src/
git commit -m "feat: add ManifestFetcher with version extraction and changelog parsing"
```

---

### Task 3: VersionListener

**Files:**
- Create: `modpack-version-checker/paper-plugin/src/main/java/com/disqt/version/VersionListener.java`

- [ ] **Step 1: Implement VersionListener**

```java
package com.disqt.version;

import net.kyori.adventure.text.minimessage.MiniMessage;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.messaging.PluginMessageListener;
import org.bukkit.scheduler.BukkitTask;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class VersionListener implements Listener, PluginMessageListener {
    private final Plugin plugin;
    private final ManifestFetcher fetcher;
    private final MiniMessage miniMessage = MiniMessage.miniMessage();
    private final Map<UUID, BukkitTask> pendingChecks = new ConcurrentHashMap<>();

    private final String outdatedTemplate;
    private final String changelogLineTemplate;
    private final String noModpackTemplate;
    private final int changelogLines;

    public VersionListener(Plugin plugin, ManifestFetcher fetcher) {
        this.plugin = plugin;
        this.fetcher = fetcher;
        this.outdatedTemplate = plugin.getConfig().getString("messages.outdated");
        this.changelogLineTemplate = plugin.getConfig().getString("messages.changelog-line");
        this.noModpackTemplate = plugin.getConfig().getString("messages.no-modpack");
        this.changelogLines = plugin.getConfig().getInt("changelog-lines", 3);
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        BukkitTask task = Bukkit.getScheduler().runTaskLater(plugin, () -> {
            pendingChecks.remove(player.getUniqueId());
            if (player.isOnline()) {
                player.sendMessage(miniMessage.deserialize(noModpackTemplate));
            }
        }, 100L);
        pendingChecks.put(player.getUniqueId(), task);
    }

    @Override
    public void onPluginMessageReceived(String channel, Player player, byte[] message) {
        if (!channel.equals("disqt:version")) return;

        BukkitTask task = pendingChecks.remove(player.getUniqueId());
        if (task != null) task.cancel();

        String clientVersion = new String(message, StandardCharsets.UTF_8).trim();
        String latestVersion = fetcher.getLatestVersion();

        if (latestVersion == null) return;

        if (!clientVersion.equals(latestVersion)) {
            String msg = outdatedTemplate.replace("{latest}", latestVersion);
            player.sendMessage(miniMessage.deserialize(msg));

            List<String> changelog = fetcher.getChangelog();
            int linesToShow = Math.min(changelogLines, changelog.size());
            for (int i = 0; i < linesToShow; i++) {
                String line = changelogLineTemplate.replace("{line}", changelog.get(i));
                player.sendMessage(miniMessage.deserialize(line));
            }
        }
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add modpack-version-checker/paper-plugin/src/main/java/com/disqt/version/VersionListener.java
git commit -m "feat: add VersionListener for join events and plugin messages"
```

---

### Task 4: DisqtVersionPlugin main class + build

**Files:**
- Create: `modpack-version-checker/paper-plugin/src/main/java/com/disqt/version/DisqtVersionPlugin.java`

- [ ] **Step 1: Implement DisqtVersionPlugin**

```java
package com.disqt.version;

import org.bukkit.plugin.java.JavaPlugin;

public class DisqtVersionPlugin extends JavaPlugin {
    private ManifestFetcher manifestFetcher;

    @Override
    public void onEnable() {
        saveDefaultConfig();

        String manifestUrl = getConfig().getString("manifest-url");
        int refreshMinutes = getConfig().getInt("refresh-minutes", 30);

        manifestFetcher = new ManifestFetcher(this, manifestUrl, refreshMinutes);
        manifestFetcher.start();

        VersionListener listener = new VersionListener(this, manifestFetcher);
        getServer().getMessenger().registerIncomingPluginChannel(this, "disqt:version", listener);
        getServer().getPluginManager().registerEvents(listener, this);

        getLogger().info("DisqtVersion enabled — listening on disqt:version");
    }

    @Override
    public void onDisable() {
        if (manifestFetcher != null) manifestFetcher.stop();
        getServer().getMessenger().unregisterIncomingPluginChannel(this);
    }
}
```

- [ ] **Step 2: Build the plugin JAR**

```bash
cd modpack-version-checker/paper-plugin
./gradlew clean build
```

Expected: BUILD SUCCESSFUL. JAR at `build/libs/DisqtVersion-1.0.0.jar`.

- [ ] **Step 3: Commit**

```bash
git add modpack-version-checker/paper-plugin/src/main/java/com/disqt/version/DisqtVersionPlugin.java
git commit -m "feat: add DisqtVersionPlugin main class, complete Paper plugin"
```

---

## Chunk 2: Fabric Mod

### Task 5: Fabric mod project scaffold

**Files:**
- Create: `modpack-version-checker/fabric-mod/build.gradle.kts`
- Create: `modpack-version-checker/fabric-mod/settings.gradle.kts`
- Create: `modpack-version-checker/fabric-mod/gradle.properties`
- Create: `modpack-version-checker/fabric-mod/src/main/resources/fabric.mod.json`

- [ ] **Step 1: Create gradle.properties**

```properties
# Verify exact versions at https://fabricmc.net/develop/ for MC 1.21.11
minecraft_version=1.21.11
yarn_mappings=1.21.11+build.1
loader_version=0.16.14
fabric_version=0.115.0+1.21.11

mod_version=1.0.0
maven_group=com.disqt
archives_base_name=disqt-version
```

**Important:** These version numbers are estimates. Before building, verify the correct versions:
- Go to https://fabricmc.net/develop/ and select MC 1.21.11
- Copy the exact Yarn mappings, Loader, and Fabric API versions
- Update gradle.properties accordingly

- [ ] **Step 2: Create settings.gradle.kts**

```kotlin
pluginManagement {
    repositories {
        maven("https://maven.fabricmc.net/") { name = "Fabric" }
        mavenCentral()
        gradlePluginPortal()
    }
}

rootProject.name = "disqt-version"
```

- [ ] **Step 3: Create build.gradle.kts**

```kotlin
plugins {
    id("fabric-loom") version "1.9-SNAPSHOT"
    java
}

version = project.property("mod_version")!!
group = project.property("maven_group")!!

repositories {
    mavenCentral()
}

dependencies {
    minecraft("com.mojang:minecraft:${project.property("minecraft_version")}")
    mappings("net.fabricmc:yarn:${project.property("yarn_mappings")}:v2")
    modImplementation("net.fabricmc:fabric-loader:${project.property("loader_version")}")
    modImplementation("net.fabricmc.fabric-api:fabric-api:${project.property("fabric_version")}")
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(21))
}

tasks.jar {
    from("LICENSE") { rename { "${it}_${project.property("archives_base_name")}" } }
}
```

**Note:** Fabric Loom version `1.9-SNAPSHOT` is an estimate. Check https://maven.fabricmc.net/net/fabricmc/fabric-loom/ for the latest version.

- [ ] **Step 4: Create fabric.mod.json**

```json
{
  "schemaVersion": 1,
  "id": "disqt-version",
  "version": "${version}",
  "name": "Disqt Version",
  "description": "Sends modpack version to the server on join",
  "authors": [{ "name": "disqt" }],
  "license": "MIT",
  "environment": "client",
  "entrypoints": {
    "main": ["com.disqt.version.DisqtVersion"],
    "client": ["com.disqt.version.DisqtVersionClient"]
  },
  "depends": {
    "fabricloader": ">=0.16.0",
    "minecraft": ">=1.21",
    "java": ">=21",
    "fabric-api": "*"
  }
}
```

- [ ] **Step 5: Generate Gradle wrapper**

```bash
cd modpack-version-checker/fabric-mod
gradle wrapper --gradle-version 8.12
```

- [ ] **Step 6: Verify scaffold resolves dependencies**

```bash
cd modpack-version-checker/fabric-mod
./gradlew build
```

Expected: BUILD SUCCESSFUL (downloads MC + mappings, no source yet).

- [ ] **Step 7: Commit**

```bash
git add modpack-version-checker/fabric-mod/
git commit -m "feat: scaffold Fabric mod project for disqt-version"
```

---

### Task 6: Fabric mod implementation + build

**Files:**
- Create: `modpack-version-checker/fabric-mod/src/main/java/com/disqt/version/VersionPayload.java`
- Create: `modpack-version-checker/fabric-mod/src/main/java/com/disqt/version/DisqtVersion.java`
- Create: `modpack-version-checker/fabric-mod/src/main/java/com/disqt/version/DisqtVersionClient.java`

- [ ] **Step 1: Implement VersionPayload**

```java
package com.disqt.version;

import net.minecraft.network.RegistryByteBuf;
import net.minecraft.network.codec.PacketCodec;
import net.minecraft.network.packet.CustomPayload;
import net.minecraft.util.Identifier;

import java.nio.charset.StandardCharsets;

public record VersionPayload(String version) implements CustomPayload {
    public static final Id<VersionPayload> ID =
        new Id<>(Identifier.of("disqt", "version"));

    public static final PacketCodec<RegistryByteBuf, VersionPayload> CODEC =
        new PacketCodec<>() {
            @Override
            public VersionPayload decode(RegistryByteBuf buf) {
                byte[] bytes = new byte[buf.readableBytes()];
                buf.readBytes(bytes);
                return new VersionPayload(new String(bytes, StandardCharsets.UTF_8));
            }

            @Override
            public void encode(RegistryByteBuf buf, VersionPayload payload) {
                buf.writeBytes(payload.version().getBytes(StandardCharsets.UTF_8));
            }
        };

    @Override
    public Id<? extends CustomPayload> getId() {
        return ID;
    }
}
```

**Note:** The `PacketCodec` API varies across MC versions. If the anonymous class approach doesn't compile, try `PacketCodec.of(encoder, decoder)` or `PacketCodec.ofStatic(encoder, decoder)`. The Fabric docs for your exact MC version will have the correct factory method. The encoding (raw UTF-8 bytes, no length prefix) must stay the same — Paper receives these exact bytes in `onPluginMessageReceived`.

- [ ] **Step 2: Implement DisqtVersion (main entrypoint)**

```java
package com.disqt.version;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;

public class DisqtVersion implements ModInitializer {
    @Override
    public void onInitialize() {
        PayloadTypeRegistry.playC2S().register(VersionPayload.ID, VersionPayload.CODEC);
    }
}
```

- [ ] **Step 3: Implement DisqtVersionClient (client entrypoint)**

```java
package com.disqt.version;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.MinecraftClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class DisqtVersionClient implements ClientModInitializer {
    private static final Logger LOGGER = LoggerFactory.getLogger("disqt-version");

    @Override
    public void onInitializeClient() {
        ClientPlayConnectionEvents.JOIN.register((handler, sender, client) -> {
            Path versionFile = MinecraftClient.getInstance().runDirectory
                .toPath().resolve("modpack-version.txt");

            if (!Files.exists(versionFile)) {
                LOGGER.warn("modpack-version.txt not found, skipping version report");
                return;
            }

            try {
                String version = Files.readString(versionFile, StandardCharsets.UTF_8).trim();
                if (!version.isEmpty()) {
                    ClientPlayNetworking.send(new VersionPayload(version));
                    LOGGER.info("Sent modpack version: {}", version);
                }
            } catch (IOException e) {
                LOGGER.error("Failed to read modpack-version.txt", e);
            }
        });
    }
}
```

- [ ] **Step 4: Build the mod JAR**

```bash
cd modpack-version-checker/fabric-mod
./gradlew clean build
```

Expected: BUILD SUCCESSFUL. JAR at `build/libs/disqt-version-1.0.0.jar`.

- [ ] **Step 5: Commit**

```bash
git add modpack-version-checker/fabric-mod/src/
git commit -m "feat: implement Fabric mod — reads modpack-version.txt, sends over disqt:version channel"
```

---

## Chunk 3: Skill Changes + Deployment

### Task 7: Update prism-client skills

**Files:**
- Modify: `plugins/minecraft-prism-client/skills/version-refresh/SKILL.md`
- Modify: `plugins/minecraft-prism-client/skills/version-refresh/executor-agent-spec.md`
- Modify: `plugins/minecraft-prism-client/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add Step 5.5 to version-refresh SKILL.md**

After the existing Step 5 (Write version decisions) and before Step 6 (Dispatch executor), insert:

```markdown
### Step 5.5 — Write changelog summary to decision doc

From the upgrade plan's "Key changes" column (Step 3), compile a changelog summary. Order entries by user impact (most notable first). Include all approved changes — additions, replacements, updates, removals.

Append to the decision doc:

\```md
## Changelog summary
- Added Ping Wheel for in-game waypoint sharing
- Updated Complementary shaders and Euphoria Patches
- Replaced AdvancementInfo with BetterAdvancements
- Removed redundant MemoryLeakFix (fixed upstream in Fabric)
\```

Each line should be a concise, player-facing description (not mod names or version numbers). Write as if explaining to a friend what changed.
```

- [ ] **Step 2: Update executor Step 12d to include changelog**

In `executor-agent-spec.md`, modify Step 12d's Python script to read `## Changelog summary` from the decision doc and include it as a `"changelog"` array in the manifest entry:

Replace the existing Step 12d python script's `entry` dict construction with:

```python
# Read changelog from decision doc
changelog = []
try:
    with open('<decision-doc-path>') as f:
        in_changelog = False
        for line in f:
            if line.strip() == '## Changelog summary':
                in_changelog = True
                continue
            if in_changelog:
                if line.startswith('## '):
                    break
                stripped = line.strip()
                if stripped.startswith('- '):
                    changelog.append(stripped[2:])
except Exception:
    pass

entry = {
    'version': '<instance-name>',
    'file': '<instance-name>.zip',
    'date': '$(date +%Y-%m-%d)',
    'mc': '<mc-version>',
    'modloader': '<modloader>',
    'size': '<size in MB> MB',
    'changelog': changelog
}
```

**Note:** The decision doc path needs to be passed to the SSH command. The executor agent runs on the local machine and reads the decision doc locally, so extract the changelog lines locally and pass them as a JSON-encoded string to the remote python command.

- [ ] **Step 3: Also add `modpack-version.txt` update to executor Step 12 preamble**

Before Step 12a (Zip), add a note to the executor spec:

```markdown
**12-pre. Update modpack-version.txt:**

Write the new version string (e.g. `2.2`) to `{PRISM_INSTANCES}/<instance-name>/.minecraft/modpack-version.txt`. This file is read by the disqt-version Fabric mod to report the client's modpack version to the server.
```

- [ ] **Step 4: Bump plugin version to 1.0.3**

Update version in:
- `plugins/minecraft-prism-client/.claude-plugin/plugin.json`: `"version": "1.0.3"`
- `.claude-plugin/marketplace.json`: prism-client entry `"version": "1.0.3"`
- `CLAUDE.md`: tree comment `(v1.0.3)`

- [ ] **Step 5: Commit**

```bash
git add plugins/minecraft-prism-client/ .claude-plugin/marketplace.json CLAUDE.md
git commit -m "feat: add changelog summary to version-refresh pipeline and modpack-version.txt to executor"
```

---

### Task 8: Deploy and end-to-end test

- [ ] **Step 1: Deploy Paper plugin to server**

```bash
scp modpack-version-checker/paper-plugin/build/libs/DisqtVersion-1.0.0.jar \
  minecraft:/home/minecraft/serverfiles/plugins/
ssh minecraft "/home/minecraft/pmcserver restart"
```

- [ ] **Step 2: Verify plugin loaded**

```bash
ssh minecraft "grep -i 'DisqtVersion' /home/minecraft/serverfiles/logs/latest.log | tail -5"
```

Expected: `[DisqtVersion] DisqtVersion enabled — listening on disqt:version`

- [ ] **Step 3: Add Fabric mod and modpack-version.txt to instance**

```bash
# Copy mod JAR to mods folder
cp modpack-version-checker/fabric-mod/build/libs/disqt-version-1.0.0.jar \
  "C:/Users/leole/AppData/Roaming/PrismLauncher/instances/1.21.11 v2.0(1)/.minecraft/mods/"

# Create modpack-version.txt
echo "2.2" > "C:/Users/leole/AppData/Roaming/PrismLauncher/instances/1.21.11 v2.0(1)/.minecraft/modpack-version.txt"
```

- [ ] **Step 4: Add changelog to current manifest**

```bash
ssh dev "python3 -c \"
import json
path = '/home/dev/prism/manifest.json'
data = json.load(open(path))
data['latest']['changelog'] = ['Initial version-checker release']
data['versions'][0]['changelog'] = ['Initial version-checker release']
json.dump(data, open(path, 'w'), indent=2)
print('changelog added')
\""
```

- [ ] **Step 5: Test end-to-end**

1. Launch Minecraft from the Prism instance
2. Join the server
3. Verify: no message appears (version matches)
4. Edit `modpack-version.txt` to `2.1` (simulate outdated client)
5. Rejoin the server
6. Verify: Jamaica-colored outdated message appears with changelog line

- [ ] **Step 6: Commit everything and push**

```bash
git add .
git commit -m "feat: complete modpack version checker — Fabric mod + Paper plugin + skill changes"
```
