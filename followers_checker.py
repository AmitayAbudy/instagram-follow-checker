import argparse
import requests
import json
import os
import sys
import re
from bs4 import BeautifulSoup

# HTML parsing tag definitions
USER_TAG = "a"
TARGET_ATTR = "target"
TARGET_VALUE = "_blank"

# Try importing rich for UI enhancements
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich import print as rprint
    from rich.text import Text
    from rich.columns import Columns
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract users from Instagram JSON or HTML files and find who doesn't follow back.")
    parser.add_argument("--followers", "-f", help="Path to the file containing followers (JSON or HTML)", default="connections/followers_and_following/followers_1.json")
    parser.add_argument("--following", "-F", help="Path to the file containing following (JSON or HTML)", default="connections/followers_and_following/following.json")
    parser.add_argument("--skip-validation", "-s", action="store_true", help="Skip HTTP validation of usernames (faster, offline)")
    parser.add_argument("--cache-file", "-c", help="Path to the profile JSON cache file", default="profile_cache.json")
    parser.add_argument("--ignored-file", "-i", help="Path to the ignored/expected non-followers JSON file", default="ignored_users.json")
    parser.add_argument("--revalidate", "-r", action="store_true", help="Force re-validation of profile existence over network, bypassing valid profile cache")
    parser.add_argument("--non-interactive", "-n", action="store_true", help="Disable interactive terminal menu post-run")
    return parser.parse_args()

def extract_followers(file_path: str) -> list[str]:
    """Extracts usernames from a followers JSON or HTML export file."""
    if file_path.lower().endswith(('.html', '.htm')):
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        users = []
        for tag in soup.find_all(USER_TAG):
            if tag.get(TARGET_ATTR) == TARGET_VALUE:
                username = tag.get_text(strip=True).split("/")[-1]
                if username:
                    users.append(username)
        return users
    
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
    """Extracts usernames from a following JSON or HTML export file."""
    if file_path.lower().endswith(('.html', '.htm')):
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        users = []
        for tag in soup.find_all(USER_TAG):
            if tag.get(TARGET_ATTR) == TARGET_VALUE:
                username = tag.get_text(strip=True).split("/")[-1]
                if username:
                    users.append(username)
        return users

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
    if total == 0:
        return
    fraction = current / total
    filled = int(bar_length * fraction)
    bar = '#' * filled + '-' * (bar_length - filled)
    print(f"\rChecking profiles: |{bar}| {current}/{total}", end='', flush=True)

def load_profile_cache(cache_file: str) -> tuple[set[str], set[str]]:
    """Loads valid and invalid profile validation cache. Returns (valid_set, invalid_set)."""
    valid_set = set()
    invalid_set = set()

    if os.path.exists("invalid_users_cache.json"):
        try:
            with open("invalid_users_cache.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    invalid_set.update(data)
        except Exception:
            pass

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    valid_set.update(data.get("valid", []))
                    invalid_set.update(data.get("invalid", []))
                elif isinstance(data, list):
                    invalid_set.update(data)
        except Exception as e:
            print(f"Warning: Failed to load profile cache file '{cache_file}': {e}")

    return valid_set, invalid_set

def save_profile_cache(cache_file: str, valid_set: set[str], invalid_set: set[str]) -> None:
    """Saves valid and invalid profile validation cache."""
    try:
        data = {
            "valid": sorted(list(valid_set)),
            "invalid": sorted(list(invalid_set))
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        with open("invalid_users_cache.json", "w", encoding="utf-8") as f:
            json.dump(sorted(list(invalid_set)), f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save profile cache file '{cache_file}': {e}")

def load_ignored_users(ignored_file: str) -> set[str]:
    if not os.path.exists(ignored_file):
        return set()
    try:
        with open(ignored_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
    except Exception as e:
        print(f"Warning: Failed to load ignored file '{ignored_file}': {e}")
    return set()

def save_ignored_users(ignored_file: str, ignored_users: set[str]) -> None:
    try:
        with open(ignored_file, "w", encoding="utf-8") as f:
            json.dump(sorted(list(ignored_users)), f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save ignored file '{ignored_file}': {e}")

def filter_existing_users(user_list: list[str], cache_file: str = "profile_cache.json", force_revalidate: bool = False) -> tuple[list[str], list[str]]:
    valid_cache, invalid_cache = load_profile_cache(cache_file)
    
    existing = []
    invalid = []
    total = len(user_list)
    cached_valid_hits = 0
    cached_invalid_hits = 0
    http_checks = 0

    for idx, user in enumerate(user_list, start=1):
        if not force_revalidate and user in valid_cache:
            existing.append(user)
            cached_valid_hits += 1
        elif not force_revalidate and user in invalid_cache:
            invalid.append(user)
            cached_invalid_hits += 1
        else:
            http_checks += 1
            if check_username_existence(user):
                existing.append(user)
                valid_cache.add(user)
                invalid_cache.discard(user)
            else:
                invalid.append(user)
                invalid_cache.add(user)
                valid_cache.discard(user)
            
            if http_checks % 10 == 0:
                save_profile_cache(cache_file, valid_cache, invalid_cache)

        _show_progress(idx, total)
    print()

    total_cached = cached_valid_hits + cached_invalid_hits
    if total_cached > 0:
        print(f"Used cache: skipped HTTP validation for {total_cached} user(s) ({cached_valid_hits} valid, {cached_invalid_hits} invalid/deleted).")
    if http_checks > 0:
        print(f"Performed HTTP validation for {http_checks} new/revalidated profile(s).")

    save_profile_cache(cache_file, valid_cache, invalid_cache)

    return existing, invalid

def parse_user_selections(input_str: str, usernames: list[str]) -> set[str]:
    selected = set()
    username_lookup = {u.lower(): u for u in usernames}
    tokens = re.split(r'[, \t]+', input_str.strip())
    
    for token in tokens:
        if not token:
            continue
        if '-' in token and not token.startswith('-'):
            parts = token.split('-', 1)
            if parts[0].isdigit() and parts[1].isdigit():
                start, end = int(parts[0]), int(parts[1])
                for idx in range(start, end + 1):
                    if 1 <= idx <= len(usernames):
                        selected.add(usernames[idx - 1])
                continue
        if token.isdigit():
            idx = int(token)
            if 1 <= idx <= len(usernames):
                selected.add(usernames[idx - 1])
            continue
        token_lower = token.lower()
        if token_lower in username_lookup:
            selected.add(username_lookup[token_lower])
        else:
            matches = [u for u in usernames if token_lower in u.lower()]
            if len(matches) == 1:
                selected.add(matches[0])
    return selected

def display_dashboard(followers_count: int, following_count: int,
                      shame_list: list[str], expected_list: list[str],
                      invalid_list: list[str]):
    if HAS_RICH:
        console.clear()
        banner = Panel(
            "[bold cyan]📸 INSTAGRAM FOLLOWER CHECKER[/bold cyan]\n"
            "[dim]Analyze followers, flag celebrities/expected non-followers, and filter deleted profiles[/dim]",
            border_style="cyan",
            expand=False
        )
        console.print(banner)

        stats_table = Table(show_header=True, header_style="bold magenta", box=None)
        stats_table.add_column("Metric", style="bold white")
        stats_table.add_column("Count", justify="right", style="bold yellow")
        
        stats_table.add_row("Total Followers", f"[green]{followers_count}[/green]")
        stats_table.add_row("Total Following", f"[cyan]{following_count}[/cyan]")
        stats_table.add_row("⚠️ The Shame List (Unexpected Non-Followers)", f"[bold red]{len(shame_list)}[/bold red]")
        stats_table.add_row("⭐ Expected / Ignored Accounts", f"[bold blue]{len(expected_list)}[/bold blue]")
        stats_table.add_row("🚫 Deleted / Changed Profiles", f"[dim]{len(invalid_list)}[/dim]")
        
        console.print(Panel(stats_table, title="[bold]Summary Dashboard[/bold]", border_style="magenta"))

        if shame_list:
            table = Table(title=f"⚠️ The Shame List ({len(shame_list)} non-followers)", show_lines=False, border_style="red")
            table.add_column("#", style="dim", width=5)
            table.add_column("Username", style="bold white", width=25)
            table.add_column("#", style="dim", width=5)
            table.add_column("Username", style="bold white", width=25)
            table.add_column("#", style="dim", width=5)
            table.add_column("Username", style="bold white", width=25)

            for i in range(0, len(shame_list), 3):
                row = []
                for j in range(3):
                    if i + j < len(shame_list):
                        row.extend([str(i + j + 1), shame_list[i + j]])
                    else:
                        row.extend(["", ""])
                table.add_row(*row)
            console.print(table)
        else:
            console.print("[bold green]🎉 Great news! Nobody in your non-followers list is unexpected.[/bold green]")

        if expected_list:
            exp_text = ", ".join(expected_list)
            console.print(Panel(exp_text, title=f"⭐ Expected Non-Followers / Celebrities ({len(expected_list)})", border_style="blue"))

        if invalid_list:
            inv_text = ", ".join(invalid_list)
            console.print(Panel(inv_text, title=f"🚫 Deleted / Changed Profiles ({len(invalid_list)})", border_style="dim"))
    else:
        print("\n" + "=" * 60)
        print(" 📸 INSTAGRAM FOLLOWER CHECKER")
        print("=" * 60)
        print(f" Followers: {followers_count} | Following: {following_count}")
        print(f" ⚠️ Shame List: {len(shame_list)} | ⭐ Expected: {len(expected_list)} | 🚫 Invalid: {len(invalid_list)}")
        print("-" * 60)
        
        print(f"\n⚠️ The Shame List ({len(shame_list)} users):")
        for idx, user in enumerate(shame_list, start=1):
            print(f" [{idx:3d}] {user}")
            
        if expected_list:
            print(f"\n⭐ Expected Non-Followers ({len(expected_list)} users):")
            print(" " + ", ".join(expected_list))
            
        if invalid_list:
            print(f"\n🚫 Deleted / Changed Profiles ({len(invalid_list)} users):")
            print(" " + ", ".join(invalid_list))
        print("=" * 60)

def export_report(filename: str, followers_count: int, following_count: int,
                  shame_list: list[str], expected_list: list[str], invalid_list: list[str]):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("====================================================\n")
            f.write(" INSTAGRAM FOLLOWER CHECKER - REPORT\n")
            f.write("====================================================\n\n")
            f.write(f"Followers: {followers_count}\n")
            f.write(f"Following: {following_count}\n")
            f.write(f"Unexpected Non-Followers (Shame List): {len(shame_list)}\n")
            f.write(f"Expected Non-Followers (Flagged): {len(expected_list)}\n")
            f.write(f"Deleted / Invalid Accounts: {len(invalid_list)}\n\n")
            
            f.write("----------------------------------------------------\n")
            f.write(" ⚠️ THE SHAME LIST (Unexpected Non-Followers)\n")
            f.write("----------------------------------------------------\n")
            if shame_list:
                for idx, u in enumerate(shame_list, start=1):
                    f.write(f"{idx:3d}. {u} (https://www.instagram.com/{u}/)\n")
            else:
                f.write("(None)\n")
            f.write("\n")

            f.write("----------------------------------------------------\n")
            f.write(" ⭐ EXPECTED NON-FOLLOWERS (Celebrities / Public Figures)\n")
            f.write("----------------------------------------------------\n")
            if expected_list:
                for idx, u in enumerate(expected_list, start=1):
                    f.write(f"{idx:3d}. {u}\n")
            else:
                f.write("(None)\n")
            f.write("\n")

            f.write("----------------------------------------------------\n")
            f.write(" 🚫 DELETED / CHANGED ACCOUNTS\n")
            f.write("----------------------------------------------------\n")
            if invalid_list:
                for idx, u in enumerate(invalid_list, start=1):
                    f.write(f"{idx:3d}. {u}\n")
            else:
                f.write("(None)\n")
            f.write("\n")

        msg = f"✔ Report successfully saved to '{filename}'."
        if HAS_RICH:
            console.print(f"[bold green]{msg}[/bold green]")
        else:
            print(msg)
    except Exception as e:
        msg = f"Error saving report to '{filename}': {e}"
        if HAS_RICH:
            console.print(f"[bold red]{msg}[/bold red]")
        else:
            print(msg)

def interactive_loop(followers_count: int, following_count: int,
                     valid_non_followers: list[str], invalid_non_followers: list[str],
                     non_followers_all: list[str],
                     cache_file: str, ignored_file: str):
    ignored_users = load_ignored_users(ignored_file)

    while True:
        shame_list = [u for u in valid_non_followers if u not in ignored_users]
        expected_list = [u for u in valid_non_followers if u in ignored_users]

        display_dashboard(followers_count, following_count, shame_list, expected_list, invalid_non_followers)

        if HAS_RICH:
            console.print("\n[bold yellow]Interactive Menu:[/bold yellow]")
            console.print(" [1] 🚩 Flag account(s) as Expected / Ignored (e.g. celebrities)")
            console.print(" [2] ❌ Unflag account(s) from Expected list")
            console.print(" [3] 🔍 Search for a username")
            console.print(" [4] 💾 Export report to text file")
            console.print(" [5] 🔄 Re-validate all profiles over network")
            console.print(" [6] 🚪 Exit")
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6"], default="6")
        else:
            print("\nInteractive Menu:")
            print(" [1] Flag account(s) as Expected / Ignored")
            print(" [2] Unflag account(s) from Expected list")
            print(" [3] Search username")
            print(" [4] Export report to file")
            print(" [5] Re-validate profiles over network")
            print(" [6] Exit")
            choice = input("\nSelect an option [1-6] (default 6): ").strip() or "6"

        if choice == "1":
            if not shame_list:
                msg = "No users currently in the Shame List to flag."
                if HAS_RICH: console.print(f"[yellow]{msg}[/yellow]")
                else: print(msg)
                input("\nPress Enter to continue...")
                continue
            
            prompt_msg = "\nEnter numbers (e.g. 1, 4, 7-10) or username(s) to flag as Expected (or press Enter to cancel): "
            user_input = input(prompt_msg).strip()
            if user_input:
                to_flag = parse_user_selections(user_input, shame_list)
                if to_flag:
                    ignored_users.update(to_flag)
                    save_ignored_users(ignored_file, ignored_users)
                    success_msg = f"✔ Flagged {len(to_flag)} user(s) as Expected Non-Followers: {', '.join(sorted(list(to_flag)))}"
                    if HAS_RICH: console.print(f"[bold green]{success_msg}[/bold green]")
                    else: print(success_msg)
                    input("\nPress Enter to refresh...")
                else:
                    msg = "No matching users found for your selection."
                    if HAS_RICH: console.print(f"[yellow]{msg}[/yellow]")
                    else: print(msg)
                    input("\nPress Enter to continue...")

        elif choice == "2":
            if not expected_list:
                msg = "No expected/ignored users to unflag."
                if HAS_RICH: console.print(f"[yellow]{msg}[/yellow]")
                else: print(msg)
                input("\nPress Enter to continue...")
                continue
            
            prompt_msg = "\nEnter numbers (e.g. 1, 3) or username(s) to unflag (or press Enter to cancel): "
            user_input = input(prompt_msg).strip()
            if user_input:
                to_unflag = parse_user_selections(user_input, expected_list)
                if to_unflag:
                    ignored_users.difference_update(to_unflag)
                    save_ignored_users(ignored_file, ignored_users)
                    success_msg = f"✔ Unflagged {len(to_unflag)} user(s): {', '.join(sorted(list(to_unflag)))}"
                    if HAS_RICH: console.print(f"[bold green]{success_msg}[/bold green]")
                    else: print(success_msg)
                    input("\nPress Enter to refresh...")
                else:
                    msg = "No matching users found for your selection."
                    if HAS_RICH: console.print(f"[yellow]{msg}[/yellow]")
                    else: print(msg)
                    input("\nPress Enter to continue...")

        elif choice == "3":
            query = input("\nEnter search term: ").strip().lower()
            if query:
                matches_shame = [u for u in shame_list if query in u.lower()]
                matches_exp = [u for u in expected_list if query in u.lower()]
                matches_inv = [u for u in invalid_non_followers if query in u.lower()]

                print(f"\n--- Search results for '{query}' ---")
                if matches_shame:
                    print(f"⚠️ Shame List ({len(matches_shame)}): {', '.join(matches_shame)}")
                if matches_exp:
                    print(f"⭐ Expected List ({len(matches_exp)}): {', '.join(matches_exp)}")
                if matches_inv:
                    print(f"🚫 Invalid Profiles ({len(matches_inv)}): {', '.join(matches_inv)}")
                if not (matches_shame or matches_exp or matches_inv):
                    print("No matching usernames found.")
                input("\nPress Enter to return to menu...")

        elif choice == "4":
            filename = input("\nEnter filename to export [default: instagram_report.txt]: ").strip() or "instagram_report.txt"
            export_report(filename, followers_count, following_count, shame_list, expected_list, invalid_non_followers)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            msg = "Re-validating all profiles over network..."
            if HAS_RICH: console.print(f"[yellow]{msg}[/yellow]")
            else: print(msg)
            valid_non_followers, invalid_non_followers = filter_existing_users(non_followers_all, cache_file=cache_file, force_revalidate=True)
            input("\nRe-validation complete. Press Enter to refresh dashboard...")

        elif choice == "6":
            msg = "👋 Goodbye!"
            if HAS_RICH: console.print(f"[bold cyan]{msg}[/bold cyan]")
            else: print(msg)
            break

def main():
    args = parse_arguments()
    
    try:
        followers = extract_followers(args.followers)
        following = extract_following(args.following)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please check the path to your JSON/HTML files.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON files. Are you sure they are valid Instagram exports? (Use .html extension for HTML files).")
        return

    non_followers = find_non_followers(followers, following)
    
    if args.skip_validation:
        valid_non_followers = non_followers
        invalid_non_followers = []
    else:
        valid_non_followers, invalid_non_followers = filter_existing_users(
            non_followers,
            cache_file=args.cache_file,
            force_revalidate=args.revalidate
        )
        
    invalid_count = len(invalid_non_followers)
    following_valid = len(following) - invalid_count
    
    if args.non_interactive:
        ignored_users = load_ignored_users(args.ignored_file)
        shame_list = [u for u in valid_non_followers if u not in ignored_users]
        expected_list = [u for u in valid_non_followers if u in ignored_users]
        display_dashboard(len(followers), following_valid, shame_list, expected_list, invalid_non_followers)
    else:
        interactive_loop(
            len(followers), following_valid,
            valid_non_followers, invalid_non_followers,
            non_followers,
            args.cache_file, args.ignored_file
        )

if __name__ == '__main__':
    main()
