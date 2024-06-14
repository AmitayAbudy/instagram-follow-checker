import argparse
from bs4 import BeautifulSoup

USER_TAG = 'a'
TARGET_ATTR = 'target'
TARGET_VALUE = '_blank'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract users from HTML files and find who doesn't follow back.")
    parser.add_argument("--followers", "-f", help="Path to the HTML file containing followers", required=True)
    parser.add_argument("--following", "-F", help="Path to the HTML file containing following", required=True)
    return parser.parse_args()

def parse_html(file_path):
    with open(file_path, "r") as f:
        return BeautifulSoup(f.read(), 'html.parser')

def extract_users(bs_obj):
    """
    This function gets a BeautifulSoup object
    the function returns the users from its file
    """
    users = []

    for span in bs_obj.find_all(USER_TAG):
        if span.get(TARGET_ATTR) == TARGET_VALUE:
            users.append(span.contents[0])

    return users

def find_non_followers(followers, following):
    return [user for user in following if user not in followers]

def print_non_followers(non_followers):
    print("The Shame List: (people I follow who don't follow me)")
    print("-----------------------------------------------------")
    for user in non_followers:
        print(user)

def main():
    args = parse_arguments()
    followers_soup = parse_html(args.followers)
    following_soup = parse_html(args.following)

    followers = extract_users(followers_soup)
    following = extract_users(following_soup)

    non_followers = find_non_followers(followers, following)
    print_non_followers(non_followers)

if __name__ == '__main__':
    main()
