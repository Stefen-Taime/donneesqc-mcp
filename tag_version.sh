#!/usr/bin/env bash
#
# Usage: ./tag_version.sh <version> [--dry-run]
# Example: ./tag_version.sh 1.0.0
#
# Creates a git tag, updates CHANGELOG.md, and creates a GitHub release.
# Requires: GitHub CLI (gh) installed and authenticated.

set -euo pipefail

VERSION="${1:-}"
DRY_RUN="${2:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: ./tag_version.sh <version> [--dry-run]"
    echo "Example: ./tag_version.sh 1.0.0"
    exit 1
fi

TAG="v${VERSION}"

# Check we're on main with clean working directory
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" ]]; then
    echo "Error: Must be on main branch (currently on $BRANCH)"
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: Working directory is not clean"
    exit 1
fi

# Get commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [[ -n "$LAST_TAG" ]]; then
    COMMITS=$(git log "${LAST_TAG}..HEAD" --pretty=format:"- %s (%h)" --no-merges)
else
    COMMITS=$(git log --pretty=format:"- %s (%h)" --no-merges)
fi

# Check for breaking changes
BREAKING=""
if echo "$COMMITS" | grep -q '!:'; then
    BREAKING="⚠️ **Breaking Changes** detected — review commits marked with \`!:\`"
fi

# Build changelog entry
DATE=$(date +%Y-%m-%d)
CHANGELOG_ENTRY="## ${TAG} (${DATE})

${BREAKING}

${COMMITS}
"

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "=== DRY RUN ==="
    echo "Would create tag: $TAG"
    echo ""
    echo "Changelog entry:"
    echo "$CHANGELOG_ENTRY"
    exit 0
fi

# Update CHANGELOG.md
if [[ -f CHANGELOG.md ]]; then
    # Insert after first line (title)
    TEMP=$(mktemp)
    head -1 CHANGELOG.md > "$TEMP"
    echo "" >> "$TEMP"
    echo "$CHANGELOG_ENTRY" >> "$TEMP"
    tail -n +2 CHANGELOG.md >> "$TEMP"
    mv "$TEMP" CHANGELOG.md
else
    echo "# Changelog" > CHANGELOG.md
    echo "" >> CHANGELOG.md
    echo "$CHANGELOG_ENTRY" >> CHANGELOG.md
fi

git add CHANGELOG.md
git commit -m "chore: release ${TAG}"
git tag -a "$TAG" -m "Release ${TAG}"
git push origin main --tags

# Create GitHub release
gh release create "$TAG" \
    --title "Release ${TAG}" \
    --notes "$CHANGELOG_ENTRY"

echo "✅ Released ${TAG}"
