import argparse
import requests
from bs4 import BeautifulSoup

USER_TAG = 'a'
TARGET_ATTR = 'target'
TARGET_VALUE = '_blank'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract users from HTML files and find who doesn't follow back.")
    parser.add_argument("--followers", "-f", help="Path to the HTML file containing followers", required=True)
    parser.add_argument("--following", "-F", help="Path to the HTML file containing following", required=True)
    parser.add_argument("--skip-validation", "-s", action="store_true",
                        help="Skip HTTP validation of usernames (faster, offline)")
    return parser.parse_args()

def parse_html(file_path: str) -> BeautifulSoup:
    with open(file_path, "r", encoding="utf-8") as f:
        return BeautifulSoup(f.read(), 'html.parser')

def extract_users(bs_obj: BeautifulSoup) -> list[str]:
    """
    Extracts and returns the list of usernames from the parsed HTML.
    """
    users = []

    for tag in bs_obj.find_all(USER_TAG):
        if tag.get(TARGET_ATTR) == TARGET_VALUE:
            # Safely extract the text within the tag
            username = tag.get_text(strip=True).split("/")[-1]
            if username:
                users.append(username)

    return users

def find_non_followers(followers: list[str], following: list[str]) -> list[str]:
    """Returns users in 'following' that are not in 'followers'."""
    # Using a set for followers drastically improves lookup performance from O(N) to O(1)
    followers_set = set(followers)
    return [user for user in following if user not in followers_set]

def check_username_existence(username: str) -> bool:
    url = "https://www.instagram.com/{username}/".format(username=username)
    
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    og_type_tag = soup.find('meta', property='og:type', content='profile')
    og_desc_tag = soup.find('meta', property='og:description')

    # If both key meta tags are present, it's very likely a real profile page.
    return bool(og_type_tag and og_desc_tag)

def _show_progress(current: int, total: int, bar_length: int = 40) -> None:
    """Simple terminal progress bar for checking profiles."""
    if total == 0:
        return
    fraction = current / total
    filled = int(bar_length * fraction)
    bar = '#' * filled + '-' * (bar_length - filled)
    print(f"\rChecking profiles: |{bar}| {current}/{total}", end='', flush=True)

def filter_existing_users(user_list: list[str]) -> tuple[list[str], list[str]]:
    """Check which users exist on Instagram and return the filtered list.

    Shows a simple progress bar while checking. Adds a delay between requests 
    to prevent aggressive rate limiting.
    """
    existing = []
    invalid = []
    total = len(user_list)
    for idx, user in enumerate(user_list, start=1):
        try:
            if check_username_existence(user):
                existing.append(user)
            else:
                invalid.append(user)
        except Exception:
            # If a request fails for any reason, treat as invalid/removed.
            invalid.append(user)
        _show_progress(idx, total)
    # finish the progress bar line
    print()
    return existing, invalid

def print_non_followers(non_followers: list[str], follower_count: int, following_count: int, invalid_count: int = 0):
    total_non = len(non_followers)
    header = f"The Shame List: followers={follower_count} following={following_count}"
    if invalid_count:
        header += f" (invalid removed={invalid_count})"
    header += f" non-followers={total_non}"
    print(header)
    print('-' * len(header))
    if not non_followers:
        print("(none)")
        return
    for user in non_followers:
        print(user)

def print_invalid_users(invalid_users: list[str]):
    if not invalid_users:
        return
    print()
    header = "Username/Deleted changed users:"
    print(header)
    print('-' * len(header))
    for user in invalid_users:
        print(user)

def main():
    args = parse_arguments()
    followers_soup = parse_html(args.followers)
    following_soup = parse_html(args.following)

    followers = extract_users(followers_soup)
    following = extract_users(following_soup)

    non_followers = find_non_followers(followers, following)
    # Check existence of non-followers before printing them (with progress bar)
    if args.skip_validation:
        # Skip HTTP validation: treat all non-followers as valid, none invalid
        valid_non_followers = non_followers
        invalid_non_followers = []
    else:
        valid_non_followers, invalid_non_followers = filter_existing_users(non_followers)
        
    invalid_count = len(invalid_non_followers)
    following_valid = len(following) - invalid_count
    
    print_non_followers(valid_non_followers, len(followers), following_valid, invalid_count)
    print_invalid_users(invalid_non_followers)

if __name__ == '__main__':
    main()
