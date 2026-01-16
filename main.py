from fetch_profile import GitHubProfile
from scorer import Scorer
from requests.exceptions import RequestException, Timeout


def main():
    USERNAME = input("Username: ").strip()
    if not USERNAME:
        print("Error: Username cannot be empty")
        exit(1)
    
    level_input = input("Choose Level (1, 2, or 3): ").strip()
    
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