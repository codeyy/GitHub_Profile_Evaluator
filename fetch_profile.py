import base64
import os
import time
import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from utils import sort_date



class GitHubProfile:
    # Constants for GitHub API and scoring thresholds
    BASE_URL = "https://api.github.com"
    API_TIMEOUT = 10
    REPOS_PER_PAGE = 100
    MIN_RATE_LIMIT = 0  # Stop if rate limit drops below this
    
    def __init__(self, username):
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        
        self.USERNAME = username
        self.scoring_level = 1
        self._user_data = {}
        self._repo_data = {}
        self._commit_data = []   
        self._readme_repos = set()
        self._empty_repos = []
        self._repo_count = 0
        self._rate_limit_remaining = 0
        
        self._header = {}

        try: 
            with open("GITHUB_TOKEN.bin", "r") as token_file:
                self._GITHUB_TOKEN = base64.b64decode(token_file.read().strip()).decode('utf-8')
        except FileNotFoundError:
            self._GITHUB_TOKEN = None

        if self._GITHUB_TOKEN == None:
            print("Warning: No GitHub token found. You may encounter rate limits. Set GITHUB_TOKEN environment variable for better performance.\n\n\n")
        if self._GITHUB_TOKEN:
            self._header = {
                "Authorization": f"Bearer {self._GITHUB_TOKEN}", 
                "User-Agent": self.USERNAME, 
                "Accept": "application/vnd.github+json", 
                "X-GitHub-Api-Version": "2022-11-28" 
            }
    
    def fetch(self):
        self._fetch_user()
        self._fetch_repos()

    def _fetch_user(self):
        try:
            response = requests.get(
                f"{self.BASE_URL}/users/{self.USERNAME}", 
                headers=self._header, 
                timeout=self.API_TIMEOUT
            )
            self._update_rate_limit(response)
            response.raise_for_status()
            
            data = response.json()
            self._user_data = {
                "Name": data.get("name") or "Not Specified",
                "UserName": data["login"],
                "Email": data.get('email') or "Not Specified",
                "Bio": data.get('bio') or "Not Specified",
                "UserSince": data["created_at"],
                "LastActive": data["updated_at"],
            }
        except HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"User '{self.USERNAME}' not found")
            raise ValueError(f"HTTP Error {e.response.status_code}: {e}")
        except Timeout:
            raise ValueError(f"Request timeout while fetching user data for '{self.USERNAME}'")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to parse user data: {e}")
    
    def _fetch_repos(self):
        try:
            all_repos = []
            page = 1
            
            # Fetch all repos with pagination
            while True:
                if self._rate_limit_remaining < self.MIN_RATE_LIMIT:
                    raise ValueError(f"GitHub API rate limit approaching (remaining: {self._rate_limit_remaining})")
                
                response = requests.get(
                    f"{self.BASE_URL}/users/{self.USERNAME}/repos",
                    params={"page": page, "per_page": self.REPOS_PER_PAGE},
                    headers=self._header,
                    timeout=self.API_TIMEOUT
                )
                self._update_rate_limit(response)
                response.raise_for_status()
                repos_json = response.json()
                
                if not isinstance(repos_json, list):
                    raise ValueError("Invalid repos response format")
                
                if not repos_json:
                    break
                
                all_repos.extend(repos_json)
                page += 1
                time.sleep(0.1)
            
            # Build repo data with proper handling
            self._repo_data = {}
            for repo in all_repos:
                try:
                    self._repo_data[repo["name"]] = {
                        "name": repo["name"],
                        "created_at": sort_date(repo["created_at"]),
                        "updated_at": sort_date(repo["updated_at"]),
                        "pushed_at": sort_date(repo["pushed_at"]),
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "issues": repo["open_issues_count"],
                        "size": repo["size"],
                        "fork": repo.get("fork", False),  # Added missing fork field
                        "language": self._safe_fetch_languages(repo["name"])
                    }
                except KeyError as e:
                    print(f"Warning: Skipping repo '{repo.get('name', 'unknown')}' due to missing field: {e}")
                    continue
            
            # Fetch details for each repo
            for repo in all_repos:
                self._fetch_repo_details(repo)

            if self._commit_data:
                self._commit_data = sort_date(self._commit_data)
            
            self._repo_count = len(self._repo_data)
        except Timeout:
            raise ValueError("Request timeout while fetching repositories")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch repos: {e}")

    def _update_rate_limit(self, response):
        """Extract and store rate limit information from response headers"""
        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining:
            try:
                self._rate_limit_remaining = int(remaining)
            except ValueError:
                pass  # If it's not an integer, just skip
            print(f"Rate Limit Remaining: {self._rate_limit_remaining}")

    def _safe_fetch_languages(self, repo_name):
        try:
            response = requests.get(
                f"{self.BASE_URL}/repos/{self.USERNAME}/{repo_name}/languages",
                headers=self._header,
                timeout=self.API_TIMEOUT
            )
            self._update_rate_limit(response)
            response.raise_for_status()
            return response.json()
        except (HTTPError, Timeout, RequestException):
            return {}

    def _fetch_repo_details(self, repo):
        try:
            # Fetch commits
            commits_response = requests.get(
                f"{self.BASE_URL}/repos/{self.USERNAME}/{repo['name']}/commits",
                headers=self._header,
                timeout=self.API_TIMEOUT
            )
            self._update_rate_limit(commits_response)
            
            if commits_response.status_code == 409:
                self._empty_repos.append(repo["name"])
                return

            commits_response.raise_for_status()
            commits = commits_response.json()
            if commits and isinstance(commits, list):
                self._commit_data.extend([commit["commit"]["author"]["date"] for commit in commits if "commit" in commit])

            # Fetch tree structure
            if not repo.get("default_branch"):
                return
                
            tree_response = requests.get(
                f"{self.BASE_URL}/repos/{self.USERNAME}/{repo['name']}/git/trees/{repo['default_branch']}?recursive=1",
                headers=self._header,
                timeout=self.API_TIMEOUT
            )
            self._update_rate_limit(tree_response)
            tree_response.raise_for_status()
            
            # Track README presence
            for item in tree_response.json().get("tree", []):
                if item.get("path") in ["README.md", "readme.md"]:
                    self._readme_repos.add(repo["name"])
                    break
        except HTTPError as e:
            if e.response.status_code != 404:
                print(f"Warning: HTTP {e.response.status_code} when fetching details for '{repo.get('name', 'unknown')}'")
        except (Timeout, RequestException) as e:
            print(f"Warning: Network error fetching details for '{repo.get('name', 'unknown')}': {type(e).__name__}")

