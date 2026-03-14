plugins {
    id("fabric-loom") version "1.13.6"
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
