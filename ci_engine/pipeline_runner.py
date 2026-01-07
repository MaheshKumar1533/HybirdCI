import time
from ci_engine.change_detector import get_changed_files
from ci_engine.ibst import select_tests
from ci_engine.cache_manager import load_cache, save_cache

def run_pipeline(test_map, dependency_graph, baseline=False):
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

import hashlib

def generate_cache_key(files):
    normalized = sorted([f.replace("\\", "/") for f in files])
    joined = "|".join(normalized)
    return hashlib.md5(joined.encode()).hexdigest()
