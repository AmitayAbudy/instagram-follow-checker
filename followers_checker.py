import argparse
import os
from bs4 import BeautifulSoup

USER_TAG = 'a'
USER_FILTER_OPT = 'target'
TARGET = '_blank'

def file_exists(file_path):
    """
    Check if a file exists at the given path.
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract users from HTML files and find who doesn't follow you back.")
    parser.add_argument("--followers-file", "-f", help="Path to the HTML file containing followers", required=True)
    parser.add_argument("--following-file", "-F", help="Path to the HTML file containing following", required=True)

    return parser.parse_args()

def parse_html(file_path):
    """
    This function gets a path to a html file
    then reading and parsing it using BeautifulSoup
    and returns the parsed object
    """
    with open(file_path, "r") as f:
        return BeautifulSoup(f.read(), 'html.parser')

def extract_users(bs_obj):
    """
    This function gets a BeautifulSoup object
    the function returns the users from its file
    using the hard-coded class identifier USER_CLASS
    """
    users = []

    for span in bs_obj.find_all(USER_TAG):
        if span.get(USER_FILTER_OPT) == TARGET:
            users.append(span.contents[0])

    return users

def main():
    args = parse_arguments()

    if not file_exists(args.followers_file):
        print(f"Error: Followers file '{args.followers_file}' not found or is not a file.")
        return
    if not file_exists(args.following_file):
        print(f"Error: Following file '{args.following_file}' not found or is not a file.")
        return

    followers_soup = parse_html(args.followers_file)
    following_soup = parse_html(args.following_file)

    followers_usernames = extract_users(followers_soup)
    following_usernames = extract_users(following_soup)

    not_following_me = [user for user in following_usernames if user not in followers_usernames]
    print("The Shame List: (people I follow who don't follow me)")
    print("-----------------------------------------------------")
    for user in not_following_me:
        print(user)

if __name__ == '__main__':
    main()
