# Instagram Follower Checker

This Python script analyzes your Instagram followers and following lists to find users who you follow but don't follow you back.

## Requirements

- Python 3
- BeautifulSoup (`pip install beautifulsoup4`)

## Usage

1. Clone the repository or download the script (`follower_checker.py`).
2. Run the script with Python, providing paths to the HTML files containing your followers and following lists as arguments.

```python follower_checker.py --followers followers.html --following following.html```

The script will then print a list of users who you follow but who don't follow you back.

## Obtaining the HTML files

Before running the script, follow this [tutorial](https://help.instagram.com/181231772500920) to access and download your Instagram information. You can also download it straight from [here](https://accountscenter.instagram.com/info_and_permissions/dyi/).  
Ensure you select the option to only download your followers and following data to only get the necessary data. Remember to request data from any timeframe, not just the past year.
