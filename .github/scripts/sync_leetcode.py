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
import time

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
        lang
        url
      }
    }
    """
    
    variables = {
        "username": username,
        "limit": 50
    }
    
    # Headers mimicking a real browser
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": f"https://leetcode.com/u/{username}/",
    }
    
    try:
        print(f"📤 Attempting to fetch data from LeetCode GraphQL API...")
        print(f"📝 Query variables: username={username}, limit=50")
        
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=20
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return []
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON response")
            print(f"Response: {response.text[:500]}")
            return []
        
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
            return []
        
        submissions = data.get("data", {}).get("recentSubmissionList", [])
        print(f"✅ Successfully fetched {len(submissions)} submissions")
        
        # Fetch difficulty for each submission
        submissions_with_difficulty = []
        for submission in submissions:
            slug = submission.get("titleSlug", "")
            difficulty = get_problem_difficulty(slug, headers)
            submission["difficulty"] = difficulty
            submissions_with_difficulty.append(submission)
        
        return submissions_with_difficulty
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - LeetCode API is slow or unreachable")
        return []
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - Unable to reach LeetCode API")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return []

def get_problem_difficulty(slug, headers):
    """Fetch problem difficulty by slug"""
    query = """
    query getProblem($slug: String!) {
      problem(titleSlug: $slug) {
        difficulty
      }
    }
    """
    
    variables = {"slug": slug}
    
    try:
        response = requests.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" not in data:
                difficulty = data.get("data", {}).get("problem", {}).get("difficulty", "Easy")
                return difficulty
    except Exception as e:
        pass
    
    return "Easy"  # Default to Easy if we can't fetch

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
    """Get code block language identifier"""
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
    
    print(f"🔄 Starting LeetCode sync for user: {username}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("-" * 60)
    
    submissions = get_leetcode_submissions(username)
    
    print("-" * 60)
    
    if not submissions:
        print("\n⚠️  No submissions found or unable to fetch data")
        print("Possible reasons:")
        print("  • Username is incorrect or profile doesn't exist")
        print("  • LeetCode's API is temporarily down or rate-limited")
        print("  • Your profile is set to private")
        print("  • Network issue or firewall blocking the request")
        return
    
    print(f"\n✅ Processing {len(submissions)} submissions...")
    
    created_count = 0
    skipped_count = 0
    
    for submission in submissions:
        status = submission.get("statusDisplay", "")
        
        # Only process accepted submissions
        if status == "Accepted":
            title = submission.get("title", "Unknown")
            slug = submission.get("titleSlug", "")
            difficulty = submission.get("difficulty", "Easy")
            lang = submission.get("lang", "python")
            url = submission.get("url", "")
            
            folder = map_difficulty(difficulty)
            filename = f"{slug}{get_file_extension(lang)}"
            filepath = Path(folder) / filename
            
            if not filepath.exists():
                try:
                    print(f"  📝 Creating: {filepath}")
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    content = create_solution_file(title, slug, difficulty, url, lang)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created_count += 1
                except Exception as e:
                    print(f"  ❌ Error creating {filepath}: {e}")
            else:
                print(f"  ⏭️  Already exists: {filepath}")
                skipped_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Sync Summary:")
    print(f"  ✅ Created: {created_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  📦 Total: {created_count + skipped_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
