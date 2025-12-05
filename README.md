# Instagram Follower Checker

This Python script analyzes your Instagram followers and following lists (HTML exports) and prints which users you follow who don't follow you back.

## Requirements

- Python 3
- `requests` (`pip install requests`)
- BeautifulSoup (`pip install beautifulsoup4`)

## Usage

1. Clone the repository or download the script (`followers_checker.py`).
2. Run the script with Python, providing paths to the HTML files containing your followers and following lists as arguments:

```bash
python followers_checker.py --followers followers.html --following following.html
```

You can skip network validation (faster, offline) with:

```bash
python followers_checker.py --followers followers.html --following following.html --skip-validation
```

## What the script does (notes)

- The script extracts usernames from the provided HTML files and computes users you follow who don't follow you back.
- Before printing, the script validates each non-follower by requesting the profile page on Instagram. A small terminal progress bar shows validation progress.
- Output sections:
  - The Shame List: validated users you follow who don't follow you back. The header shows `followers=... following=...` and how many invalid profiles were removed.
  - Deleted/Blocked users: user names that appear removed/blocked (invalid profiles) and were excluded from the main list.

## CLI flags

- `--skip-validation`, `-s`: skip the HTTP profile validation step and treat all detected non-followers as valid. Use this if you want a fast, offline run or to avoid making requests to Instagram.

## Network & rate-limiting

- The script performs HTTP requests to Instagram for validation. Ensure you have network access when running it.
- To reduce the chance of rate-limiting, avoid running the script repeatedly in quick succession. The script already includes a small delay between checks.

## Obtaining the HTML files

Before running the script, follow this [tutorial](https://help.instagram.com/181231772500920) to access and download your Instagram information. You can also download it from the Instagram account data tools. Select only the option to download your followers and following data. Also remember to request data from any timeframe, not just the past year.
