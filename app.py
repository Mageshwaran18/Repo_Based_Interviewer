import streamlit as st
import requests
import tempfile
import zipfile
import shutil
import os
import pathlib
from io import BytesIO

# ------------------------
# Config
# ------------------------
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tif', '.tiff'}
SKIP_EXTENSIONS = {'.exe', '.dll', '.so', '.class', '.jar', '.pyc', '.pyo', '.bin', '.db', '.sqlite'}
SKIP_DIR_NAMES = {'node_modules', '.git', '__pycache__'}
TEXT_SAMPLE_SIZE = 4096
NON_TEXT_THRESHOLD = 0.30


# ------------------------
# Helper functions
# ------------------------
def parse_github_url(url):
    # Example: https://github.com/user/repo or with /tree/branch
    parts = url.replace("https://github.com/", "").split("/")
    owner = parts[0]
    repo = parts[1].replace(".git", "")
    branch = "main"

    if len(parts) > 3 and parts[2] == "tree":
        branch = parts[3]

    return owner, repo, branch


def is_binary_file(path):
    try:
        with open(path, "rb") as f:
            sample = f.read(TEXT_SAMPLE_SIZE)
            if not sample:
                return False
            if b"\x00" in sample:
                return True

            non_text = 0
            for b in sample:
                if b in (9, 10, 13):  # tab/newline
                    continue
                if 32 <= b <= 126:    # ASCII printable
                    continue
                if b >= 128:          # UTF-8 multi-byte
                    continue
                non_text += 1

            return (non_text / len(sample)) > NON_TEXT_THRESHOLD
    except:
        return True


def should_skip_file(rel_path: pathlib.Path):
    ext = rel_path.suffix.lower()
    if ext in IMAGE_EXTS or ext in SKIP_EXTENSIONS:
        return True

    for part in rel_path.parts:
        if part in SKIP_DIR_NAMES:
            return True

    return False


def download_repo(owner, repo, branch):
    url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    r = requests.get(url)
    r.raise_for_status()
    return r.content


def filter_repo(zip_bytes):
    tmp = tempfile.mkdtemp()
    extract_dir = os.path.join(tmp, "extract")
    os.makedirs(extract_dir, exist_ok=True)

    # Extract zip
    with zipfile.ZipFile(BytesIO(zip_bytes)) as z:
        z.extractall(extract_dir)

    # Find root folder
    root_folder = next(
        os.path.join(extract_dir, d)
        for d in os.listdir(extract_dir)
        if os.path.isdir(os.path.join(extract_dir, d))
    )

    # Filter files
    output_io = BytesIO()
    with zipfile.ZipFile(output_io, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for root, dirs, files in os.walk(root_folder):

            # Skip whole directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]

            for fname in files:
                src = pathlib.Path(root) / fname
                rel = pathlib.Path(os.path.relpath(src, root_folder))

                if should_skip_file(rel):
                    continue
                if is_binary_file(src):
                    continue

                out_zip.write(src, arcname=str(rel))

    return output_io.getvalue()


# ------------------------
# Streamlit UI
# ------------------------
st.title("📥 GitHub Repo Cleaner (Text-only Extractor)")

repo_url = st.text_input("Enter a public GitHub repository URL:")
run_btn = st.button("Process Repository")

if run_btn:
    try:
        st.info("⏳ Downloading repository...")

        owner, repo, branch = parse_github_url(repo_url)
        zip_bytes = download_repo(owner, repo, branch)

        st.info("⚙️ Filtering files (removing binaries, images, libraries)...")
        output_zip = filter_repo(zip_bytes)

        st.success("✅ Processing complete!")

        st.download_button(
            label="⬇️ Download Filtered ZIP",
            data=output_zip,
            file_name=f"{repo}_filtered.zip",
            mime="application/zip"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
