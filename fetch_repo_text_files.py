#!/usr/bin/env python3
"""
fetch_repo_text_files.py
Usage:
    python fetch_repo_text_files.py https://github.com/owner/repo [output_dir]

What it does:
 - Downloads the repo zip (default branch or specified branch if URL includes it)
 - Extracts
 - Copies only non-binary, non-image, non-node_modules files to output_dir
"""

import sys
import os
import re
import tempfile
import zipfile
import shutil
import pathlib

try:
    import requests
except Exception:
    requests = None

# --- Configuration ---
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif'}
SKIP_EXTENSIONS = {'.exe', '.dll', '.so', '.class', '.jar', '.pyc', '.pyo', '.db', '.sqlite', '.bin'}
SKIP_DIR_NAMES = {'node_modules', '.git', '__pycache__'}
TEXT_SAMPLE_SIZE = 4096
NON_TEXT_THRESHOLD = 0.30  # fraction of non-text bytes to consider as binary

# --- Helpers ---
def parse_github_url(url: str):
    # Accepts forms like:
    # https://github.com/owner/repo
    # https://github.com/owner/repo/
    # https://github.com/owner/repo/tree/branch or .../tree/branch/path
    m = re.match(r'https?://github\.com/([^/]+)/([^/]+)(?:/(.*))?', url.strip())
    if not m:
        raise ValueError("Not a recognized GitHub repo URL.")
    owner = m.group(1)
    repo = m.group(2).removesuffix('.git')
    tail = m.group(3) or ''
    branch = None
    # If tail starts with tree/<branch>
    parts = tail.split('/')
    if len(parts) >= 2 and parts[0] == 'tree':
        branch = parts[1]
    return owner, repo, branch

def get_zip_url(owner, repo, branch=None):
    if branch:
        return f'https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip'
    else:
        # use default branch zip (github redirects to default branch)
        return f'https://github.com/{owner}/{repo}/archive/refs/heads/master.zip', f'https://github.com/{owner}/{repo}/archive/refs/heads/main.zip'

def download_zip(zip_url, dest_path):
    if requests is None:
        # fallback to urllib
        import urllib.request
        with urllib.request.urlopen(zip_url) as resp, open(dest_path, 'wb') as f:
            f.write(resp.read())
        return
    r = requests.get(zip_url, stream=True)
    r.raise_for_status()
    with open(dest_path, 'wb') as f:
        for chunk in r.iter_content(1024 * 64):
            if chunk:
                f.write(chunk)

def is_binary_file(path):
    try:
        with open(path, 'rb') as f:
            sample = f.read(TEXT_SAMPLE_SIZE)
            if not sample:
                return False  # empty file -> treat as text
            if b'\x00' in sample:
                return True
            # count non-text bytes
            # consider printable ASCII range and common UTF-8 byte ranges as text
            non_text = 0
            for b in sample:
                # allow tab/newline/carriage return
                if b in (9,10,13):
                    continue
                # ASCII printable range
                if 32 <= b <= 126:
                    continue
                # bytes >= 128 are likely part of UTF-8 multibyte sequences; consider them text for simplicity
                if b >= 128:
                    continue
                non_text += 1
            frac = non_text / max(1, len(sample))
            return frac > NON_TEXT_THRESHOLD
    except Exception:
        # if we can't read the file, assume binary (safer)
        return True

def should_skip_file(rel_path: pathlib.Path):
    # skip by extension
    ext = rel_path.suffix.lower()
    if ext in IMAGE_EXTS or ext in SKIP_EXTENSIONS:
        return True
    # skip by folder name in path
    for part in rel_path.parts:
        if part in SKIP_DIR_NAMES:
            return True
    return False

# --- Main flow ---
def fetch_repo(github_url, output_dir):
    owner, repo, branch = parse_github_url(github_url)
    out_dir = pathlib.Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='repofetch_')
    try:
        # pick zip url(s)
        if branch:
            zip_urls = [get_zip_url(owner, repo, branch)]
        else:
            # try both master and main; one will 404 but we'll try
            zip_urls = list(get_zip_url(owner, repo, None))
        zip_path = os.path.join(tmp, 'repo.zip')
        success = False
        last_err = None
        for z in zip_urls:
            try:
                print(f"Downloading {z} ...")
                download_zip(z, zip_path)
                success = True
                break
            except Exception as e:
                last_err = e
                print(f"Failed to download {z}: {e}")
        if not success:
            raise RuntimeError(f"Failed to download repo zip. Last error: {last_err}")

        # extract
        extract_dir = os.path.join(tmp, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)

        # top-level folder often is repo-branchname; find it
        extracted_root = None
        for entry in os.listdir(extract_dir):
            p = os.path.join(extract_dir, entry)
            if os.path.isdir(p):
                extracted_root = p
                break
        if not extracted_root:
            extracted_root = extract_dir

        # Walk and copy files that are not skipped or binary
        copied = 0
        skipped = 0
        for root, dirs, files in os.walk(extracted_root):
            # remove skipped dirs in-place so os.walk doesn't descend
            dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
            for fname in files:
                src_path = pathlib.Path(root) / fname
                # get relative path inside repo
                rel = pathlib.Path(os.path.relpath(src_path, start=extracted_root))
                if should_skip_file(rel):
                    skipped += 1
                    continue
                # check binary
                if is_binary_file(src_path):
                    skipped += 1
                    continue
                # copy to output, preserve relative structure
                dest = out_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest)
                copied += 1

        print(f"Done. Copied {copied} files. Skipped {skipped} files.")
        return out_dir
    finally:
        # cleanup temp
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_repo_text_files.py <github_repo_url> [output_dir]")
        sys.exit(1)
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) >= 3 else 'data/fetched_repo'

    print("Fetching repo from:", url)
    print("Saving text files to:", out)

    try:
        dest = fetch_repo(url, out)
        print("Files saved to:", dest)
    except Exception as e:
        print("Error:", e)
        sys.exit(2)
