import sys
import base64

from scorer import Scorer
from fetch_profile import GitHubProfile
from requests.exceptions import RequestException, Timeout

def main():
    try:
        with open("GITHUB_TOKEN.bin", "r+b") as TOKEN_file:
            TOKEN = TOKEN_file.read().strip()
            if not TOKEN:
                print("No GitHub token Saved. \nPlease enter your GitHub token or type 'skip' to continue without a token.(limited access)")
                while True:
                    TOKEN = input("Github Token: ").strip()
                    if TOKEN.strip().lower() not in ["/exit", "skip"] and TOKEN:
                        TOKEN_file.write(base64.b64encode(TOKEN.encode('utf-8')))
                        break
                    if TOKEN.strip().lower() == "/exit":
                        sys.exit(0)
                    if TOKEN.strip().lower() == "skip":
                        TOKEN = None
                        break
    except FileNotFoundError:
        print("No GitHub token Saved. \nPlease enter your GitHub token or type 'skip' to continue without a token.(limited access)")
        with open("GITHUB_TOKEN.bin", "w+b") as TOKEN_file:
            while True:
                TOKEN = input("Github Token: ").strip()
                if TOKEN.strip().lower() not in ["/exit", "skip"] and TOKEN:
                    TOKEN_file.write(base64.b64encode(TOKEN.encode('utf-8')))
                    break
                if TOKEN.strip().lower() == "/exit":
                    sys.exit(0)
                if TOKEN.strip().lower() == "skip":
                    break       

    while True:
        USERNAME = input("Username: ").strip()
        if USERNAME:
            break
        if USERNAME == "/exit":
            break
        
    while True:
        level_input = input("Choose Level (1, 2, or 3): ").strip()
        if level_input in ['1', '2', '3']:
            break
        if level_input == "/exit":
            break

    
    # Validate and convert level
    try:
        level = int(level_input)
        if level not in [1, 2, 3]:
            print("Error: Level must be 1, 2, or 3")
            exit(1)
    except ValueError:
        print("Error: Level must be a valid integer (1, 2, or 3)")
        exit(1)

    try:
        profile = GitHubProfile(USERNAME)
        profile.fetch()

        score = Scorer(profile, level)
        score._score_all()

        print_report(score, level)

    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except (RequestException, Timeout) as e:
        print(f"Network error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

def print_report(scorer, level):
    scores = scorer.scores
    total = sum(scores.values())
    verdict = scorer.verdict()

    print("\n" + "=" * 50)
    print(f"Level-{level} GitHub Profile Evaluation Report")
    print("=" * 50)
    print("\nCategory Scores:")
    print(f"  Authenticity   : {scores.get('authenticity', 0)} / 2")
    print(f"  Execution      : {scores.get('execution', 0)} / 2")
    print(f"  Communication  : {scores.get('communication', 0)} / 2")
    print(f"  Consistency    : {scores.get('consistency', 0)} / 2")
    print(f"  Growth         : {scores.get('growth', 0)} / 2")
    print("\n" + "-" * 50)
    print(f"Total Score      : {total} / 10")
    print(f"Verdict          : {verdict}")
    print("-" * 50)
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()