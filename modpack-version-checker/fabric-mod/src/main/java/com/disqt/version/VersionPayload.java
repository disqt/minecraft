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
