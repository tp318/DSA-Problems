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
    
    # Updated GraphQL query with proper formatting
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
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://leetcode.com/",
    }
    
    try:
        payload = {
            "query": query,
            "variables": variables
        }
        
        print(f"Sending request to LeetCode GraphQL API...")
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return []
        
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            return []
        
        submissions = data.get("data", {}).get("recentSubmissionList", [])
        return submissions
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching LeetCode data: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")
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
        print("ℹ️  No submissions found or unable to fetch data")
        print("This could mean:")
        print("- The username is incorrect")
        print("- LeetCode's API is temporarily unavailable")
        print("- Your profile is not publicly visible")
        return
    
    print(f"✅ Found {len(submissions)} submissions")
    
    created_count = 0
    skipped_count = 0
    
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
                created_count += 1
            else:
                print(f"⏭️  Already exists: {filepath}")
                skipped_count += 1
    
    print(f"\n📊 Summary: {created_count} created, {skipped_count} skipped")

if __name__ == "__main__":
    main()
