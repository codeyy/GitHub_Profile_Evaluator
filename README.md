# GitHub Profile Evaluator

A Python tool that evaluates GitHub user profiles based on multiple criteria and provides a comprehensive score at different difficulty levels.

## Overview

This project analyzes GitHub profiles using the GitHub API to assess developers across five key categories:
- **Authenticity** - Account age and repository count
- **Execution** - Code quality and repository structure
- **Communication** - Documentation and README coverage
- **Consistency** - Commit activity patterns and frequency
- **Growth** - Repository creation timeline and activity trends

## Features

- 🔍 Fetch comprehensive GitHub profile data using the GitHub API
- 📊 Multi-level evaluation system (3 difficulty levels)
- ⚡ Efficient API usage with rate limiting and pagination
- 📈 Detailed scoring reports across 5 evaluation categories
- 🛡️ Error handling for network issues and invalid inputs
- 📋 Clear, formatted evaluation verdicts

## Installation

### Prerequisites
- Python 3.7+ (for advance setup)
- GitHub API Token

### User Setup

1. **Download the Executable**

   Download the latest release of gpe

2. **Set GitHub API Token**
   
   Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with public repository access and enter it in application when prompted:

## Usage

Run the evaluator with:
```bash
./gpe [options]
```
```bash
[options] : 
            [--help, -h] for help
            [--edit-token, -et] to edit your GitHub token
```
<br>

### Advance Setup (For Developers)

1. **Clone the repository**
   ```bash
   git clone https://github.com/codeyy/GitHub_Profile_Evaluator
   cd GitHub_Profile_Evaluator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set GitHub API Token**
   
   Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with public repository access, and enter when prompted.

## Usage

Run the evaluator with:
```bash
python main.py
```


<br>
You'll be prompted to enter:

1. **GitHub token** - For first setup only enter the GitHub Personal Access Token here 
2. **Username** - The GitHub username to evaluate
3. **Level** - Choose 1, 2, or 3 (increasing difficulty)




### Evaluation Levels

| Level | Account Age | Min Repos | Max Inactivity | README Coverage | Difficulty |
|-------|-------------|-----------|----------------|-----------------|-----------|
| 1 | 1 year | 2+ | 6 months | 25%+ | Beginner-friendly |
| 2 | 2 years | 5+ | 3 months | 50%+ | Intermediate |
| 3 | 5 years | 10+ | 1 month | 90%+ | Very Strict |

### Example Output

```
==================================================
Level-1 GitHub Profile Evaluation Report
==================================================

Category Scores:
  Authenticity   : 2 / 2
  Execution      : 1 / 2
  Communication  : 2 / 2
  Consistency    : 2 / 2
  Growth         : 1 / 2

--------------------------------------------------
Total Score      : 8 / 10
Verdict          : Excellent Developer
--------------------------------------------------
==================================================
```

## Project Structure

```
.
├── main.py              # Entry point and report generation
├── fetch_profile.py     # GitHub API interaction and data fetching
├── scorer.py            # Evaluation logic and scoring system
├── utils.py             # Utility functions for date/time handling
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

## How It Works

1. **Profile Fetching** (`fetch_profile.py`)
   - Authenticates with GitHub API using personal token
   - Retrieves user information and all repositories
   - Analyzes commit history and repository metadata
   - Handles pagination and rate limiting

2. **Scoring** (`scorer.py`)
   - Applies level-specific thresholds
   - Evaluates each category against criteria
   - Generates numerical scores (0-10 scale)
   - Provides verdict summary

3. **Report Generation** (`main.py`)
   - Validates user input
   - Orchestrates data fetching and scoring
   - Formats and displays results

## Requirements

- `requests>=2.28.0` - HTTP library for GitHub API calls

## Error Handling

The tool handles:
- ❌ Invalid or non-existent GitHub usernames
- ❌ Network timeouts and connection errors
- ❌ API rate limiting issues
- ❌ Missing or invalid input parameters
- ❌ Invalid evaluation levels

## Notes

- Requires a GitHub Personal Access Token for API authentication
- Rate limited by GitHub API (60+ requests available per hour)
- Only analyzes public profile information
- Commit history analysis limited to accessible repositories

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the evaluator.


🧑‍💻 Author
-`Agam Kumar`