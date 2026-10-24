# The open-fleet live harness image (PR #668): every paid live arm runs in a fresh container of
# it, which scripts/live_container.py destroys after. Build it with `live_container.py build`,
# the only step that downloads anything (docs/guides/live-harness.md). It holds no credential:
# the subscription token reaches a container at run time as a read-only file, never this image.
#
# The base is pinned by digest: python:3.13.15-slim's OCI image index, one pin on every platform it carries.
FROM python:3.13.15-slim@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# git for the arms (each reads its own checkout's HEAD); curl and certificates for the installer.
# `runner` (10001) is the non-root user every arm runs as; /repo is a read-only mount it does not own.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates curl \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 10001 runner \
 && useradd --uid 10001 --gid 10001 --create-home --shell /bin/bash runner \
 && git config --system --add safe.directory /repo

USER runner
ENV HOME=/home/runner \
    PATH=/home/runner/.local/bin:/usr/local/bin:/usr/bin:/bin \
    DISABLE_AUTOUPDATER=1 \
    PYTHONDONTWRITEBYTECODE=1

# Claude Code, pinned, by its official installer, as `runner`. The build fails unless the pinned
# binary the in-container wrapper execs (scripts/live_container_bin/claude) is that version.
RUN curl -fsSL https://claude.ai/install.sh | bash -s 2.1.304 \
 && /home/runner/.local/share/claude/versions/2.1.304 --version | grep -q '^2\.1\.304 '

LABEL org.open-fleet.claude-code="2.1.304"
WORKDIR /results
