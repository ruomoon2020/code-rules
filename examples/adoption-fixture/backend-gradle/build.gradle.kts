// 接入验收占位；真实项目见 web-backend/rules/examples/gradle/build.gradle.kts.sample
plugins {
    java
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}
