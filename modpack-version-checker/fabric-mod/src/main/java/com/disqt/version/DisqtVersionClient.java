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
