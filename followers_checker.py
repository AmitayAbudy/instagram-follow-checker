#!python3
from bs4 import BeautifulSoup

USER_TAG = 'a'
USER_FILTER_OPT = 'target'
TARGET = '_blank'

FOLLOWING_HTML_FILE_PATH = "/Users/amitay/Downloads/instagram-amitay-2/connections/followers_and_following/following.html"
FOLLOWERS_HTML_FILE_PATH = "/Users/amitay/Downloads/instagram-amitay-2/connections/followers_and_following/followers_1.html"


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
   followers_soup = parse_html(FOLLOWERS_HTML_FILE_PATH)
   following_soup = parse_html(FOLLOWING_HTML_FILE_PATH)

   followers_usernames = extract_users(followers_soup)
   following_usernames = extract_users(following_soup)

   not_following_me = [user for user in following_usernames if user not in followers_usernames]
   print("The Shame List: (people I follow who don't follow me)")
   print("-----------------------------------------------------")
   for user in not_following_me:
      print(user)

if __name__ == '__main__':
   main()