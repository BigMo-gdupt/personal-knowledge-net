import os
import re
from collections import Counter

def extract_links_from_file(filepath):
    """Extract all [[...]] links from a markdown file."""
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'gbk', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            # Find all [[...]] patterns
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            return links
        except UnicodeDecodeError:
            continue
    # If all encodings fail, return empty list
    print(f"Warning: Could not read {filepath} with any encoding")
    return []

def main():
    wiki_dir = 'wiki'
    all_links = []
    
    # Get all markdown files
    for filename in os.listdir(wiki_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(wiki_dir, filename)
            links = extract_links_from_file(filepath)
            all_links.extend(links)
    
    # Count link frequencies
    link_counter = Counter(all_links)
    
    # Get existing files (without .md extension)
    existing_files = [f[:-3] for f in os.listdir(wiki_dir) if f.endswith('.md')]
    
    print("=== 拓扑死链分析 ===")
    print("\n所有被引用节点及其频次:")
    for link, count in sorted(link_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"  {link}: {count}次")
    
    print("\n=== 死链节点（物理不存在）===")
    dead_links = []
    for link, count in link_counter.items():
        if link not in existing_files:
            dead_links.append((link, count))
    
    if dead_links:
        for link, count in sorted(dead_links, key=lambda x: x[1], reverse=True):
            print(f"  {link}: 被引用{count}次")
    else:
        print("  未发现死链节点")
    
    print(f"\n总计: {len(dead_links)}个死链节点")

if __name__ == '__main__':
    main()
