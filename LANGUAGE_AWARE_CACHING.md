# Language-Aware Caching for HybridCI

## Overview

The language-aware caching system enhances HybridCI's test selection optimization by grouping changed files by programming language and maintaining separate cache entries per language. This enables more granular cache management, faster cache hits, and better insights into language-specific test impacts.

## Features

### 1. **Automatic Language Detection**

- Detects over 15+ programming languages from file extensions
- Supported languages:
  - **Python** (.py)
  - **JavaScript** (.js)
  - **TypeScript** (.ts, .tsx)
  - **Java** (.java, .class)
  - **C#** (.cs)
  - **C/C++** (.c, .cpp, .h)
  - **Go** (.go)
  - **Rust** (.rs)
  - **Ruby** (.rb)
  - **PHP** (.php)
  - **Swift** (.swift)
  - **Kotlin** (.kt)
  - **Scala** (.scala)
  - And more...

### 2. **Language-Aware Caching**

- **Per-Language Caches**: Maintains separate cache entries for each language
- **Granular Hit Detection**: Cache hits are determined at the language level
- **Efficient Storage**: Language-specific results are stored in `.ci_cache/language_aware/`
- **Language Maps**: Tracks which languages were affected by code changes

### 3. **Enhanced Analytics**

- View project language distribution
- Track recently changed languages
- Language-specific cache statistics
- Cache hit rate by language
- Test execution breakdown by language

### 4. **Dashboard Integration**

- **Cache Statistics Page**: New `/cache-stats` dashboard showing:
  - Total caches and language-aware caches
  - Language distribution chart
  - Recently changed languages
  - Language-specific cache breakdown
- **Run History Enhancement**: Track execution mode and languages per run
- **Real-time Status**: Display language information during pipeline execution

## Architecture

### Cache Structure

```
.ci_cache/
├── <hash>                          # Standard cache (legacy)
└── language_aware/
    ├── <hash>_python.pkl           # Python-specific cache
    ├── <hash>_javascript.pkl       # JavaScript-specific cache
    ├── <hash>_<language>.pkl       # Per-language caches
    └── <hash>_map.json             # Language distribution map
```

### Core Components

#### `cache_manager.py`

Enhanced with language-aware functions:

- `get_file_language(filepath)` - Detect language from file extension
- `load_language_aware_cache(cache_key, language)` - Load language-specific cache
- `save_language_aware_cache(cache_key, data, language)` - Save language-specific cache
- `save_language_map(cache_key, language_map)` - Store language distribution
- `get_cache_stats()` - Get cache statistics including language breakdown

#### `change_detector.py`

Extended with language-aware change detection:

- `get_changed_files_by_language()` - Group changed files by language
- `filter_changes_by_language(files, language)` - Filter changes for specific language

#### `pipeline_runner.py`

Updated with two execution modes:

- **Standard Mode** (`language_aware=False`): Original single-cache approach
- **Language-Aware Mode** (`language_aware=True`): Per-language cache management

#### `language_utils.py` (NEW)

Utility module for language analysis:

- `get_language_stats()` - Analyze project language distribution
- `get_changed_languages()` - Identify languages affected by recent changes
- `analyze_file_impact(filepath)` - Analyze impact potential of file changes
- `get_language_test_runners(language)` - Get recommended test runners
- `format_language_report(breakdown)` - Generate human-readable reports

#### `test_language_aware.py` (NEW)

Comprehensive test suite with 40+ test cases covering:

- Language detection for all supported languages
- Cache operations (save/load)
- File impact analysis
- Test runner recommendations
- Report formatting

### Database Enhancement

The `runs` table now tracks:

```sql
CREATE TABLE runs (
    id INTEGER PRIMARY KEY,
    tests_run INTEGER,
    time_taken REAL,
    cache_hit INTEGER,
    mode TEXT,                    -- 'hybrid', 'baseline', 'language_aware'
    languages TEXT,               -- JSON array of detected languages
    language_breakdown TEXT       -- JSON object with test counts per language
)
```

## Usage

### Basic Usage (Language-Aware by Default)

```python
from ci_engine.pipeline_runner import run_pipeline

# Uses language-aware caching automatically
result = run_pipeline(TEST_MAP, DEP_GRAPH)
print(result)
# Output:
# {
#     'tests': [...],
#     'time': 2.45,
#     'cache_hit': True,
#     'mode': 'language_aware',
#     'languages': ['python', 'javascript'],
#     'languages_cached': ['python', 'javascript']
# }
```

### Standard Mode (Legacy)

```python
# Use original single-cache approach
result = run_pipeline(TEST_MAP, DEP_GRAPH, language_aware=False)
```

### Language Detection

```python
from ci_engine.cache_manager import get_file_language

lang = get_file_language("src/main.py")        # Returns: "python"
lang = get_file_language("src/app.js")         # Returns: "javascript"
lang = get_file_language("Main.java")          # Returns: "java"
```

### Analyze Language Changes

```python
from ci_engine.change_detector import get_changed_files_by_language

language_map, all_files = get_changed_files_by_language()
print(language_map)
# Output:
# {
#     'python': ['src/main.py', 'src/utils.py'],
#     'javascript': ['src/app.js']
# }
```

### Get Language Statistics

```python
from ci_engine.language_utils import get_language_stats, get_changed_languages

# Project-wide language distribution
stats = get_language_stats()
print(stats['by_language'])  # { 'python': [...], 'javascript': [...] }

# Recently changed languages
langs = get_changed_languages()
print(langs)  # ['python', 'javascript']
```

### Generate Language Report

```python
from ci_engine.language_utils import format_language_report

breakdown = {'python': 15, 'javascript': 10, 'typescript': 5}
report = format_language_report(breakdown)
print(report)
# Output:
# Language-Aware Test Execution Report
# ========================================
# python         15 tests ( 50.0%)
# javascript     10 tests ( 33.3%)
# typescript      5 tests ( 16.7%)
# ========================================
# Total          30 tests
```

## Dashboard Endpoints

### New Routes

- **`GET /cache-stats`** - Display cache statistics dashboard
- **`GET /cache-stats-api`** - JSON API for cache statistics
- **`GET /run`** - Run CI pipeline with language-aware caching (enhanced)
- **`GET /`** - Main dashboard (enhanced with cache statistics)
- **`GET /runs`** - Run history (enhanced with language tracking)

### Dashboard Features

#### Main Dashboard (`/`)

- **Cache Hit Rate Card** - Shows percentage of cache hits
- **Total Runs Card** - Tracks pipeline executions
- **Run CI Pipeline Button** - Enhanced with language information display
- **Runtime Trend Chart** - Visual representation of execution times

#### Cache Statistics (`/cache-stats`)

- **Total Caches** - Count of all cache entries
- **Language-Aware Caches** - Count of language-specific caches
- **Languages Tracked** - Number of distinct languages in cache
- **Language Distribution Chart** - Doughnut chart showing project language composition
- **Recently Changed Languages** - Languages affected by recent changes
- **Language-Specific Caches Breakdown** - Table of caches per language

#### Run History (`/runs`)

- **Enhanced Table Columns**:
  - Run ID
  - Tests Executed
  - Time Taken (seconds)
  - Cache Hit (Yes/No badge)
  - Mode (hybrid, baseline, language_aware)
  - Languages (affected by the run)

## Testing

Run the comprehensive test suite:

```bash
pytest ci_engine/test_language_aware.py -v
```

Test coverage includes:

- ✓ Language detection for 13+ languages
- ✓ Language-aware cache save/load operations
- ✓ Language map operations
- ✓ File impact analysis
- ✓ Test runner recommendations
- ✓ Report formatting

## Performance Benefits

### Cache Hit Rates

- **Single-Language Changes**: 100% cache hit rate (isolated to one language)
- **Multi-Language Changes**: Partial cache hits (only unchanged languages cached)
- **Repeated Changes**: Instant hits from language-specific cache

### Example Scenario

```
Change 1: Modify Python files (test_auth.py)
├─ Python tests cached
├─ JavaScript cache not affected
└─ Next Python change: cache hit ✓

Change 2: Modify JavaScript files (app.js)
├─ JavaScript tests executed
├─ Python tests skipped (cache hit)
└─ Next JavaScript change: cache hit ✓
```

## Configuration

### Environment Variables

- `CI_LANGUAGE_AWARE` (optional) - Set to `false` to disable language-aware mode
- `CI_CACHE_DIR` (optional) - Override cache directory path

### Dashboard Configuration

The dashboard automatically detects and displays language information. No additional configuration needed.

## Migration Guide

### From Standard Cache to Language-Aware

**Existing code** continues to work without changes:

```python
# Still works - automatically uses language-aware caching
result = run_pipeline(TEST_MAP, DEP_GRAPH)
```

**To use standard mode**:

```python
# Explicitly disable language-aware caching
result = run_pipeline(TEST_MAP, DEP_GRAPH, language_aware=False)
```

### Database Migration

The `runs` table is backward-compatible. Existing rows will have:

- `mode = None` (handled as 'hybrid')
- `languages = None`
- `language_breakdown = None`

## Troubleshooting

### Cache Not Hitting

1. Verify language detection: `get_file_language(filepath)`
2. Check `.ci_cache/language_aware/` directory exists
3. Ensure file extensions are standard
4. Review git diff output: `git diff --name-only HEAD~1`

### Unknown Language Files

Files with unknown extensions are grouped under `"unknown"` language. Add extensions to `LANGUAGE_EXTENSIONS` in `cache_manager.py`:

```python
LANGUAGE_EXTENSIONS[".custom"] = "custom_lang"
```

### Performance Issues

- Monitor cache size: `du -sh .ci_cache/`
- Clear old caches: `rm -rf .ci_cache/language_aware/*`
- Reduce git history depth if detecting changes is slow

## Future Enhancements

- [ ] Language-specific test runner selection
- [ ] Configuration file per language (e.g., `pytest.ini`, `jest.config.js`)
- [ ] Cross-language dependency analysis
- [ ] Language-specific performance benchmarks
- [ ] Cache compression for language-specific data
- [ ] Webhook notifications for multi-language changes

## Contributing

When adding new language support:

1. Add extension mapping to `LANGUAGE_EXTENSIONS`
2. Update test suite in `test_language_aware.py`
3. Document in README
4. Test cache operations work correctly

Example:

```python
LANGUAGE_EXTENSIONS[".lua"] = "lua"
```

## License

Same as HybridCI project
