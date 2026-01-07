import hashlib
import os
import pickle

CACHE_DIR = ".ci_cache"

def hash_dependencies(requirements_file):
    with open(requirements_file, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_cache(cache_key):
    path = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def save_cache(cache_key, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, cache_key), "wb") as f:
        pickle.dump(data, f)
