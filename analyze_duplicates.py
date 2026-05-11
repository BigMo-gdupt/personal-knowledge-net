import os
import re
from collections import defaultdict

def read_file_content(filepath):
    """Read file content with multiple encoding attempts."""
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'gbk', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""

def extract_title_and_summary(content):
    """Extract title and first paragraph from markdown content."""
    lines = content.split('\n')
    title = ""
    summary = ""
    
    # Try to find title from first non-empty line or YAML frontmatter
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('---'):
            continue
        if line and not title:
            # Remove markdown headers
            if line.startswith('# '):
                title = line[2:].strip()
            else:
                title = line
        if line and len(summary) < 200:  # Get first 200 chars for summary
            summary += line + " "
    
    return title[:100], summary[:300]

def main():
    wiki_dir = 'wiki'
    files_info = {}
    
    # Collect information about all files
    for filename in os.listdir(wiki_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(wiki_dir, filename)
            content = read_file_content(filepath)
            title, summary = extract_title_and_summary(content)
            files_info[filename] = {
                'title': title,
                'summary': summary,
                'content': content[:1000]  # First 1000 chars for comparison
            }
    
    print("=== 语义重叠分析 ===")
    print("\n所有文件标题:")
    for filename, info in files_info.items():
        print(f"  {filename}: {info['title']}")
    
    # Check for potential duplicates by comparing titles and summaries
    print("\n=== 潜在语义重叠检查 ===")
    
    # Group by similar titles (remove special characters and compare)
    title_groups = defaultdict(list)
    for filename, info in files_info.items():
        # Normalize title: remove parentheses, brackets, spaces, convert to lowercase
        normalized = re.sub(r'[\(\)\[\]\（\）\【\】\s]', '', info['title'].lower())
        title_groups[normalized].append(filename)
    
    potential_duplicates = {k: v for k, v in title_groups.items() if len(v) > 1}
    
    if potential_duplicates:
        print("发现可能重复的标题:")
        for normalized, filenames in potential_duplicates.items():
            print(f"  组 '{normalized}':")
            for f in filenames:
                print(f"    - {f}: {files_info[f]['title']}")
    else:
        print("未发现明显重复的标题")
    
    # Check content similarity for files with similar topics
    print("\n=== 内容相似性分析 ===")
    
    # Based on manual inspection, check for known potential duplicates
    # From the file list, check if there are English-Chinese pairs
    file_pairs_to_check = []
    
    # Look for files that might be English/Chinese versions of the same concept
    all_files = list(files_info.keys())
    for i in range(len(all_files)):
        for j in range(i+1, len(all_files)):
            file1 = all_files[i]
            file2 = all_files[j]
            
            # Check if they might be translations
            # Simple heuristic: if one contains English words and the other Chinese
            # This is a simplified check
            content1 = files_info[file1]['content'].lower()
            content2 = files_info[file2]['content'].lower()
            
            # Count common words (simple approach)
            words1 = set(re.findall(r'\b\w+\b', content1))
            words2 = set(re.findall(r'\b\w+\b', content2))
            common_words = words1.intersection(words2)
            
            if len(common_words) > 20:  # Arbitrary threshold
                similarity = len(common_words) / max(len(words1), len(words2))
                if similarity > 0.3:
                    file_pairs_to_check.append((file1, file2, similarity))
    
    if file_pairs_to_check:
        print("发现内容相似的文件对:")
        for file1, file2, similarity in sorted(file_pairs_to_check, key=lambda x: x[2], reverse=True):
            print(f"  {file1} 和 {file2}: 相似度 {similarity:.2%}")
            print(f"    {file1}: {files_info[file1]['title']}")
            print(f"    {file2}: {files_info[file2]['title']}")
    else:
        print("未发现高度相似的内容")

if __name__ == '__main__':
    main()
