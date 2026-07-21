#!/usr/bin/env python3
"""
LeetCode to GitHub sync script
Fetches recently solved problems from LeetCode and adds them to the repository
"""

import os
import requests
import json
from datetime import datetime
from pathlib import Path

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

def get_leetcode_submissions(username):
    """Fetch LeetCode submissions for a user"""
    query = """
    query getRecentSubmissions($username: String!, $limit: Int!) {
      recentSubmissionList(username: $username, limit: $limit) {
        title
        titleSlug
        timestamp
        statusDisplay
        difficulty
        lang
        url
      }
    }
    """
    
    variables = {
        "username": username,
        "limit": 50
    }
    
    try:
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("recentSubmissionList", [])
    except Exception as e:
        print(f"Error fetching LeetCode data: {e}")
        return []

def map_difficulty(difficulty):
    """Map LeetCode difficulty to folder"""
    difficulty_map = {
        "Easy": "easy",
        "Medium": "medium",
        "Hard": "hard"
    }
    return difficulty_map.get(difficulty, "easy")

def create_solution_file(title, slug, difficulty, url, lang):
    """Create a solution file template"""
    content = f"""# {title}

- **LeetCode Link**: [{title}]({url})
- **Difficulty**: {difficulty}
- **Language**: {lang}
- **Date Solved**: {datetime.now().strftime('%Y-%m-%d')}

## Problem Statement
[Add problem statement here]

## Solution Approach
[Describe your approach]

## Code
```{get_language_extension(lang)}
# Add your solution code here
```

## Complexity Analysis
- **Time Complexity**: O(?)
- **Space Complexity**: O(?)

## Notes
[Add any additional notes or edge cases]
"""
    return content

def get_language_extension(lang):
    """Get file extension for language"""
    extensions = {
        "python": "python",
        "python3": "python",
        "java": "java",
        "cpp": "cpp",
        "c++": "cpp",
        "javascript": "javascript",
        "typescript": "typescript",
        "go": "go",
        "rust": "rust",
        "csharp": "csharp",
    }
    return extensions.get(lang.lower(), "text")

def get_file_extension(lang):
    """Get file extension for language"""
    extensions = {
        "python": ".py",
        "python3": ".py",
        "java": ".java",
        "cpp": ".cpp",
        "c++": ".cpp",
        "javascript": ".js",
        "typescript": ".ts",
        "go": ".go",
        "rust": ".rs",
        "csharp": ".cs",
    }
    return extensions.get(lang.lower(), ".txt")

def main():
    username = os.getenv("LEETCODE_USERNAME")
    
    if not username:
        print("⚠️  LEETCODE_USERNAME not set. Skipping sync.")
        print("To enable automatic syncing:")
        print("1. Go to Settings → Secrets and variables → Actions")
        print("2. Create a new secret named 'LEETCODE_USERNAME'")
        print("3. Set it to your LeetCode username")
        return
    
    print(f"📡 Fetching LeetCode problems for user: {username}")
    submissions = get_leetcode_submissions(username)
    
    if not submissions:
        print("No submissions found or unable to fetch data")
        return
    
    print(f"✅ Found {len(submissions)} submissions")
    
    for submission in submissions:
        if submission.get("statusDisplay") == "Accepted":
            title = submission.get("title", "Unknown")
            slug = submission.get("titleSlug", "")
            difficulty = submission.get("difficulty", "Easy")
            lang = submission.get("lang", "python")
            url = submission.get("url", "")
            
            folder = map_difficulty(difficulty)
            filename = f"{slug}{get_file_extension(lang)}"
            filepath = Path(folder) / filename
            
            if not filepath.exists():
                print(f"📝 Creating: {filepath}")
                filepath.parent.mkdir(parents=True, exist_ok=True)
                
                content = create_solution_file(title, slug, difficulty, url, lang)
                with open(filepath, 'w') as f:
                    f.write(content)
            else:
                print(f"⏭️  Already exists: {filepath}")

if __name__ == "__main__":
    main()
