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
