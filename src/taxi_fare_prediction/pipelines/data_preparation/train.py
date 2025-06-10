#!/usr/bin/env python3
import os

def folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def find_large_dirs(base_dir="data", min_size_mb=100):
    threshold = min_size_mb * 1024 * 1024
    heavy = []
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            p = os.path.join(root, d)
            size = folder_size(p)
            if size >= threshold:
                heavy.append((p, size / 1024**2))
    return sorted(heavy, key=lambda x: -x[1])

if __name__ == "__main__":
    heavy_dirs = find_large_dirs("data", min_size_mb=100)
    if not heavy_dirs:
        print("Nie znaleziono katalogów >100 MB w folderze 'data/'.")
    else:
        print("Znalezione ciężkie katalogi (>100 MB):\n")
        for path, mb in heavy_dirs:
            print(f"  {mb:7.1f} MB\t{path}")
