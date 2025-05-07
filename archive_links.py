import os
import yaml
import json
import requests
from pathlib import Path

ARCHIVE_API = "https://web.archive.org/save/"
YAML_DIR = "yamls"
CACHE_FILE = "archived_links.json"


def load_cached_archives():
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        return {}

def save_cached_archives(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def extract_links(obj):
    links = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'link':
                if isinstance(v, str):
                    links.append(v)
                elif isinstance(v, list):
                    links.extend(v)
            else:
                links.extend(extract_links(v))
    elif isinstance(obj, list):
        for item in obj:
            links.extend(extract_links(item))
    return links

def archive_link(url):
    try:
        response = requests.get(ARCHIVE_API + url, timeout=10)
        if response.status_code in (200, 302):
            print(f"Archived: {url}")
            return response.url  # Wayback snapshot link
        else:
            print(f"Failed to archive: {url} - Status: {response.status_code}")
    except Exception as e:
        print(f"Error archiving {url}: {e}")
    return None

def main():
    cache = load_cached_archives()
    for yaml_path in Path(YAML_DIR).rglob("*.yaml"):
        with open(yaml_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                links = extract_links(data)
                for link in set(links):
                    if link not in cache:
                        archived = archive_link(link)
                        if archived:
                            cache[link] = archived
            except yaml.YAMLError as e:
                print(f"Error parsing {yaml_path}: {e}")
    save_cached_archives(cache)

if __name__ == "__main__":
    main()
