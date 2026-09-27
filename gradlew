#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ -x .gradle-bootstrap/gradle-9.5.1/bin/gradle ]; then
    exec .gradle-bootstrap/gradle-9.5.1/bin/gradle "$@"
fi
if ! command -v gradle >/dev/null 2>&1; then
    echo 'Install Gradle 9.5.1 and JDK 25 on Linux/macOS. Windows: use gradlew.bat.' >&2
    exit 1
fi
if ! gradle --version | grep -qx 'Gradle 9.5.1'; then
    echo 'This project requires Gradle 9.5.1.' >&2
    exit 1
fi
exec gradle "$@"
