import time
import hashlib
from pathlib import Path
from ci_engine.change_detector import get_changed_files, get_changed_files_by_language, filter_changes_by_language
from ci_engine.ibst import select_tests
from ci_engine.cache_manager import (
    load_cache, save_cache,
    load_language_aware_cache, save_language_aware_cache, save_language_map,
    get_file_language
)

def run_pipeline(test_map, dependency_graph, baseline=False, language_aware=True):
    start = time.time()

    # ---------- BASELINE MODE ----------
    if baseline:
        selected_tests = list(test_map.keys())
        time.sleep(0.5 * len(selected_tests))
        end = time.time()

        return {
            "tests": selected_tests,
            "time": end - start,
            "cache_hit": False,
            "mode": "baseline"
        }

    # ---------- HYBRIDCI MODE ----------
    changed_files = get_changed_files()

    # 🔥 SAFETY NET
    if not changed_files:
        changed_files = []
        for files in test_map.values():
            changed_files.extend(files)

    # Language-aware caching
    if language_aware:
        return _run_pipeline_language_aware(changed_files, test_map, dependency_graph, start)
    else:
        return _run_pipeline_standard(changed_files, test_map, dependency_graph, start)

def _run_pipeline_standard(changed_files, test_map, dependency_graph, start):
    """Standard caching mode (non-language-aware)."""
    cache_key = generate_cache_key(changed_files)

    cached = load_cache(cache_key)
    if cached:
        return {
            "tests": cached["tests"],
            "time": cached["time"],
            "cache_hit": True,
            "mode": "hybrid"
        }

    selected_tests = select_tests(changed_files, dependency_graph, test_map)

    time.sleep(0.5 * len(selected_tests))
    end = time.time()

    result = {
        "tests": selected_tests,
        "time": end - start,
        "cache_hit": False,
        "mode": "hybrid"
    }

    save_cache(cache_key, result)
    return result

def _run_pipeline_language_aware(changed_files, test_map, dependency_graph, start):
    """Language-aware caching mode."""
    base_cache_key = generate_cache_key(changed_files)
    language_map, _ = get_changed_files_by_language()
    
    # Try to load all language-specific caches
    cached_results = {}
    all_cached = True
    
    for language in language_map.keys():
        lang_cache = load_language_aware_cache(base_cache_key, language)
        if lang_cache:
            cached_results[language] = lang_cache
        else:
            all_cached = False
    
    # If all language caches exist, merge and return
    if all_cached and cached_results:
        merged_tests = set()
        for lang_result in cached_results.values():
            merged_tests.update(lang_result["tests"])
        
        end = time.time()
        return {
            "tests": list(merged_tests),
            "time": end - start,
            "cache_hit": True,
            "mode": "language_aware",
            "languages_cached": list(cached_results.keys())
        }
    
    # Compute tests per language
    selected_tests_by_language = {}
    all_selected_tests = set()
    
    for language in language_map.keys():
        lang_files = language_map[language]
        lang_tests = select_tests(lang_files, dependency_graph, test_map)
        selected_tests_by_language[language] = lang_tests
        all_selected_tests.update(lang_tests)
        
        time.sleep(0.5 * len(lang_tests))
    
    end = time.time()
    
    # Save per-language caches
    for language, lang_tests in selected_tests_by_language.items():
        lang_result = {
            "tests": lang_tests,
            "time": (end - start) / len(selected_tests_by_language),
            "language": language
        }
        save_language_aware_cache(base_cache_key, lang_result, language)
    
    # Save language map
    save_language_map(base_cache_key, language_map)
    
    return {
        "tests": list(all_selected_tests),
        "time": end - start,
        "cache_hit": False,
        "mode": "language_aware",
        "languages": list(language_map.keys()),
        "language_breakdown": {lang: len(tests) for lang, tests in selected_tests_by_language.items()}
    }

def generate_cache_key(files):
    normalized = sorted([f.replace("\\", "/") for f in files])
    joined = "|".join(normalized)
    return hashlib.md5(joined.encode()).hexdigest()
