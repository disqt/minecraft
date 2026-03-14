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
