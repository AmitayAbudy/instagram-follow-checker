import argparse
import requests
import json
from bs4 import BeautifulSoup

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract users from Instagram JSON files and find who doesn't follow back.")
    parser.add_argument("--followers", "-f", help="Path to the JSON file containing followers", default="connections/followers_and_following/followers_1.json")
    parser.add_argument("--following", "-F", help="Path to the JSON file containing following", default="connections/followers_and_following/following.json")
    parser.add_argument("--skip-validation", "-s", action="store_true",
                        help="Skip HTTP validation of usernames (faster, offline)")
    return parser.parse_args()

def extract_followers(file_path: str) -> list[str]:
    """Extracts and returns the list of usernames from the followers JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    users = []
    for item in data:
        if "string_list_data" in item and item["string_list_data"]:
            username = item["string_list_data"][0].get("value")
            if username:
                users.append(username)
    return users

def extract_following(file_path: str) -> list[str]:
    """Extracts and returns the list of usernames from the following JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    users = []
    following_list = data.get("relationships_following", [])
    for item in following_list:
        if "title" in item:
            username = item["title"]
            if username:
                users.append(username)
        elif "string_list_data" in item and item["string_list_data"]:
            # Fallback if title is missing
            username = item["string_list_data"][0].get("value")
            if username:
                users.append(username)
    return users

def find_non_followers(followers: list[str], following: list[str]) -> list[str]:
    """Returns users in 'following' that are not in 'followers'."""
    followers_set = set(followers)
    return [user for user in following if user not in followers_set]

def check_username_existence(username: str) -> bool:
    url = f"https://www.instagram.com/{username}/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        og_type_tag = soup.find('meta', property='og:type', content='profile')
        og_desc_tag = soup.find('meta', property='og:description')
        return bool(og_type_tag and og_desc_tag)
    except Exception:
        return False

def _show_progress(current: int, total: int, bar_length: int = 40) -> None:
    """Simple terminal progress bar for checking profiles."""
    if total == 0:
        return
    fraction = current / total
    filled = int(bar_length * fraction)
    bar = '#' * filled + '-' * (bar_length - filled)
    print(f"\rChecking profiles: |{bar}| {current}/{total}", end='', flush=True)

def filter_existing_users(user_list: list[str]) -> tuple[list[str], list[str]]:
    """Check which users exist on Instagram and return the filtered list."""
    existing = []
    invalid = []
    total = len(user_list)
    for idx, user in enumerate(user_list, start=1):
        if check_username_existence(user):
            existing.append(user)
        else:
            invalid.append(user)
        _show_progress(idx, total)
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
    
    try:
        followers = extract_followers(args.followers)
        following = extract_following(args.following)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please check the path to your JSON files.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON files. Are you sure they are valid Instagram exports?")
        return

    non_followers = find_non_followers(followers, following)
    
    if args.skip_validation:
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
