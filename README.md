# Instagram Follower Checker

This Python script analyzes your Instagram followers and following lists to find users who you follow but don't follow you back.

## Requirements

- Python 3
- BeautifulSoup (`pip install beautifulsoup4`)

## Usage

1. Clone the repository or download the script (`follower_analyzer.py`).
2. Run the script with Python, providing paths to the HTML files containing your followers and following lists as arguments.

```python follower_analyzer.py --followers followers.html --following following.html```

The script will then print a list of users who you follow but who don't follow you back.

## How it works

The script parses HTML files containing your followers and following lists using BeautifulSoup. It then compares the two lists to find users who you follow but who don't follow you back.