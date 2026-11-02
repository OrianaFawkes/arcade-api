FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Remove the broken, unused Yarn APT repository.
RUN set -eux; \
    for source in /etc/apt/sources.list /etc/apt/sources.list.d/*; do \
        if [ -f "$source" ] && grep -q "dl.yarnpkg.com/debian" "$source"; then \
            rm -f "$source"; \
        fi; \
    done
