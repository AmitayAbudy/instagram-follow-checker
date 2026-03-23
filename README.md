# Instagram Follower Checker

This Python script analyzes your Instagram followers and following lists (JSON exports) and prints which users you follow who don't follow you back.

## Requirements

- Python 3
- `requests` (`pip install requests`)
- BeautifulSoup (`pip install beautifulsoup4`)

## Usage

1. Clone the repository or download the script (`followers_checker.py`).
2. Download your Instagram data in **JSON** format (see below).
3. Place the `connections` folder in the same directory as the script.
4. Run the script:

```bash
python followers_checker.py
```

By default, the script looks for:
- Followers: `connections/followers_and_following/followers_1.json`
- Following: `connections/followers_and_following/following.json`

You can also specify paths manually:

```bash
python followers_checker.py --followers custom_followers.json --following custom_following.json
```

You can skip network validation (faster, offline) with:

```bash
python followers_checker.py --skip-validation
```

## What the script does (notes)

- The script extracts usernames from the provided JSON files and computes users you follow who don't follow you back.
- Before printing, the script validates each non-follower by requesting the profile page on Instagram. A small terminal progress bar shows validation progress.
- Output sections:
  - The Shame List: validated users you follow who don't follow you back. The header shows `followers=... following=...` and how many invalid profiles were removed.
  - Deleted/Blocked users: user names that appear removed/blocked (invalid profiles) and were excluded from the main list.

## CLI flags

- `--skip-validation`, `-s`: skip the HTTP profile validation step and treat all detected non-followers as valid. Use this if you want a fast, offline run or to avoid making requests to Instagram.

## Network & rate-limiting

- The script performs HTTP requests to Instagram for validation. Ensure you have network access when running it.
- To reduce the chance of rate-limiting, avoid running the script repeatedly in quick succession.

## Obtaining the JSON files

Before running the script, follow this [tutorial](https://help.instagram.com/181231772500920) to access and download your Instagram information. **Make sure to select JSON format** instead of HTML when requesting the download. Select only the option to download your followers and following data. Also remember to request data from "All time", not just the past year.
