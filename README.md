# Instagram Follower Checker

This Python script analyzes your Instagram followers and following lists (JSON exports) and prints which users you follow who don't follow you back.

## Requirements

- Python 3
- `requests` (`pip install requests`)
- BeautifulSoup (`pip install beautifulsoup4`)
- `rich` (`pip install rich`) — optional but recommended for enhanced terminal UI

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

## Features & Terminal UI

- **Rich Terminal Dashboard**: Displays summary stats, categorized multi-column tables, and badges for easy scanning.
- **Interactive Flagging**: Post-run terminal menu allows you to flag celebrities, public figures, or brand accounts you don't expect to follow you back. Flagged accounts are saved to `ignored_users.json` and automatically separated from **The Shame List** on future runs.
- **Full Profile Caching**: Caches validation results (both valid active profiles and invalid/deleted profiles) in `profile_cache.json`. Subsequent runs skip HTTP checks for all cached profiles, executing instantly!
- **Incremental Cache Persistence**: Saves progress every 10 network checks so progress is never lost even if interrupted.
- **Search & Export**: Interactively search for usernames, export structured reports, or trigger on-demand profile re-validation.

## CLI flags

- `--skip-validation`, `-s`: skip the HTTP profile validation step and treat all detected non-followers as valid.
- `--cache-file`, `-c`: path to the JSON file storing cached profile validation statuses (default: `profile_cache.json`).
- `--ignored-file`, `-i`: path to the JSON file storing expected non-followers / celebrities (default: `ignored_users.json`).
- `--revalidate`, `-r`: force re-validation of all profile statuses over the network, updating the cache.
- `--non-interactive`, `-n`: disable the interactive menu loop post-run (useful for automated scripts).




## Network & rate-limiting

- The script performs HTTP requests to Instagram for validation. Ensure you have network access when running it.
- To reduce the chance of rate-limiting, avoid running the script repeatedly in quick succession.

## Obtaining the JSON files

Before running the script, follow this [tutorial](https://help.instagram.com/181231772500920) to access and download your Instagram information. **Make sure to select JSON format** instead of HTML when requesting the download. Select only the option to download your followers and following data. Also remember to request data from "All time", not just the past year.
