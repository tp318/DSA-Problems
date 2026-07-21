#!/usr/bin/env python3
"""
Update problem statistics in README
"""

from pathlib import Path
import re

def count_problems():
    """Count problems by difficulty"""
    stats = {
        "easy": 0,
        "medium": 0,
        "hard": 0
    }
    
    for difficulty in stats.keys():
        folder = Path(difficulty)
        if folder.exists():
            # Count all solution files (excluding README)
            stats[difficulty] = len([f for f in folder.glob("*") if f.is_file() and f.name != "README.md"])
    
    return stats

def update_readme(stats):
    """Update README with latest stats"""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        print("README.md not found")
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    total = sum(stats.values())
    
    # Update statistics section
    content = re.sub(
        r'- \*\*Total Problems Solved\*\*: \d+',
        f'- **Total Problems Solved**: {total}',
        content
    )
    
    content = re.sub(
        r'- \*\*Easy\*\*: \d+',
        f'- **Easy**: {stats["easy"]}',
        content
    )
    
    content = re.sub(
        r'- \*\*Medium\*\*: \d+',
        f'- **Medium**: {stats["medium"]}',
        content
    )
    
    content = re.sub(
        r'- \*\*Hard\*\*: \d+',
        f'- **Hard**: {stats["hard"]}',
        content
    )
    
    # Update timestamp
    from datetime import datetime
    content = re.sub(
        r'\*\*Last Updated\*\*: .*',
        f'**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}',
        content
    )
    
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Statistics updated!")
    print(f"   Total: {total} | Easy: {stats['easy']} | Medium: {stats['medium']} | Hard: {stats['hard']}")

if __name__ == "__main__":
    stats = count_problems()
    update_readme(stats)
