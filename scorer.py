from utils import timedel, sort_date, list_t_delta
from fetch_profile import GitHubProfile



class Scorer:   
    # Scoring thresholds and constants to be set by _level()
    MIN_ACCOUNT_AGE_DAYS = 0
    MIN_REPO_COUNT = 0
    MAX_INACTIVITY_DAYS = 0
    LONG_GAP_THRESHOLD = 0
    HIGH_GAP_RATIO = 0
    LOW_GAP_RATIO = 0
    README_COVERAGE_THRESHOLD = 0

    def __init__(self, profile, level=1,):
        if not isinstance(profile, GitHubProfile):
            raise ValueError("Scorer requires a GitHubProfile instance")
        self.profile = profile
        self.scores = {}
        self.level = level

    def _score_all(self):
        self._level()
        self.score_authenticity()
        self.score_execution()
        self.score_communication()
        self.score_consistency()
        self.score_growth()

    def _level(self):
        # Level One (beginner friendly)
        if self.level == 1:
            self.MIN_ACCOUNT_AGE_DAYS = 365
            self.MIN_REPO_COUNT = 2
            self.MAX_INACTIVITY_DAYS = 182.5
            self.LONG_GAP_THRESHOLD = 6
            self.HIGH_GAP_RATIO = 0.75
            self.LOW_GAP_RATIO = 0.25
            self.README_COVERAGE_THRESHOLD = 0.25
        
        # Level two (bit harsh)
        elif self.level == 2:
            self.MIN_ACCOUNT_AGE_DAYS = 365 * 2
            self.MIN_REPO_COUNT = 5
            self.MAX_INACTIVITY_DAYS = 91.25
            self.LONG_GAP_THRESHOLD = 4
            self.HIGH_GAP_RATIO = 0.50
            self.LOW_GAP_RATIO = 0.20
            self.README_COVERAGE_THRESHOLD = 0.50
        
        # Level three (Very hard to satisfy)
        elif self.level == 3:
            self.MIN_ACCOUNT_AGE_DAYS = 365 * 5
            self.MIN_REPO_COUNT = 10
            self.MAX_INACTIVITY_DAYS = 30.41
            self.LONG_GAP_THRESHOLD = 2
            self.HIGH_GAP_RATIO = 0.25
            self.LOW_GAP_RATIO = 0.5
            self.README_COVERAGE_THRESHOLD = 0.90
        else:
            raise ValueError(f"Invalid level: {self.level}")

    def verdict(self):
        if not self.scores:
            self._score_all()
        total = sum(self.scores.values())
        return self._verdict(total)

    def score_authenticity(self):
        if not self.profile._user_data or "UserSince" not in self.profile._user_data:
            self.scores["authenticity"] = 0
            return 0
            
        age_days = timedel(sort_date(self.profile._user_data["UserSince"]))
        repo_count = len(self.profile._repo_data)
        score = 0
        
        if age_days > self.MIN_ACCOUNT_AGE_DAYS:
            score += 1
        if repo_count > self.MIN_REPO_COUNT:
            score += 1
        
        self.scores["authenticity"] = min(score, 2)
        return self.scores["authenticity"]

    def score_execution(self):
        repos = self.profile._repo_data
        if not repos:
            self.scores["execution"] = 0
            return 0

        non_empty = sum(1 for repo in repos.values() if repo.get("size", 0) > 0)
        original = sum(1 for repo in repos.values() if not repo.get("fork", False))

        score = (1 if non_empty >= 1 else 0) + (1 if original >= 1 else 0)
        self.scores["execution"] = min(score, 2)
        return self.scores["execution"]

    def score_communication(self):
        if self.profile._repo_count == 0:
            self.scores["communication"] = 0
            return 0
            
        readme_count = len(self.profile._readme_repos)
        if not readme_count:
            self.scores["communication"] = 0
            return 0
        
        score = 2 if readme_count > self.profile._repo_count * self.README_COVERAGE_THRESHOLD else 1
        self.scores["communication"] = score
        return score

    def score_consistency(self):
        commits = self.profile._commit_data
        if not commits:
            self.scores["consistency"] = 0
            return 0
        
        # Check last commit date
        last_commit_age = timedel(commits[-1])
        if last_commit_age > self.MAX_INACTIVITY_DAYS:
            self.scores["consistency"] = 0
            return 0
        
        gaps = list_t_delta(commits)
        if not gaps:
            self.scores["consistency"] = 1
            return 1
        
        long_gaps = sum(1 for g in gaps if g > self.LONG_GAP_THRESHOLD)
        ratio = long_gaps / len(gaps) if gaps else 0

        if ratio <= self.LOW_GAP_RATIO:
            score = 2
        elif ratio <= self.HIGH_GAP_RATIO:
            score = 1
        else:
            score = 0

        self.scores["consistency"] = score
        return score

    def score_growth(self):
        repos = self.profile._repo_data
        readme_repos = self.profile._readme_repos
        repo_names = list(repos.keys())

        if len(repo_names) < 3:
            self.scores["growth"] = 1
            return 1

        sorted_repos = sorted(repo_names, key=lambda r: repos[r]["created_at"])
        mid = len(sorted_repos) // 2
        older, newer = sorted_repos[:mid], sorted_repos[mid:]

        def quality_score(repo_list):
            if not repo_list:
                return 0
            score = sum(
                (1 if repos[r].get("size", 0) > 0 else 0) +
                (1 if r in readme_repos else 0)
                for r in repo_list
            )
            return score / len(repo_list)

        old_quality = quality_score(older)
        new_quality = quality_score(newer)

        if new_quality > old_quality:
            score = 2
        elif new_quality == old_quality:
            score = 1
        else:
            score = 0

        self.scores["growth"] = score
        return score

    def _verdict(self, total):
        if total >= 9:
            return "Strong candidate — interview immediately."
        elif total >= 7:
            return "Good junior profile — worth interviewing."
        elif total >= 5:
            return "Early-stage candidate — potential, but needs development."
        return "Not ready yet — lacks key hiring signals."
