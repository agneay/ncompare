# Scripts

## make_atl06_structural_fixtures.py

Regenerates the structure-only ATL06 fixtures in `tests/data/atl06_structure/`.

`ncompare` compares metadata only, so the ATL06 comparison test does not need the
granules' science data — only their structure. These fixtures declare the same
groups, dimensions, variables, dtypes, chunking, and attributes while writing no
data values, which makes the test hermetic (no network, no Earthdata credentials)
and its difference count stable across ATL06 reprocessing. Roughly 32 MB of
granules becomes ~128 KB of committed fixtures.

**Usage:**
```bash
uv run python scripts/make_atl06_structural_fixtures.py <granule_1.h5> <granule_2.h5>
```

Only needed when the fixtures should track a different ATL06 version. It reads
real granules, so obtaining those requires Earthdata credentials; the nightly
integration workflow downloads them at `~/.cache/icesat2_test_data/`.

After regenerating, run `pytest -k icesat_structure` and update
`EXPECTED_ATL06_DIFFERENCES` in `tests/test_core.py` if the count legitimately
changed.

## bump_develop_after_release.sh

Automatically bumps the develop branch to the next minor version when a release branch is created.

**Usage:**
```bash
./scripts/bump_develop_after_release.sh <release_version>
```

**Example:**
```bash
./scripts/bump_develop_after_release.sh 1.11.0
```

This script is called automatically by CI when a release branch is first pushed. It:
1. Checks out develop
2. Verifies develop is still on the version being released
3. Bumps develop to the next minor alpha (e.g., `1.11.0a6 → 1.12.0a1`)
4. Commits and pushes the change

This prevents version collisions between hotfixes and develop.

**Manual Usage:**

If CI fails to auto-bump develop, you can run it manually:

```bash
git checkout release/1.11.0
bash scripts/bump_develop_after_release.sh 1.11.0
```

The script is idempotent - safe to run multiple times.