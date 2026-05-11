import os
import re

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

def check_frontmatter(content):
    """Check if file has YAML frontmatter."""
    lines = content.strip().split('\n')
    if len(lines) < 3:
        return False
    # Check for --- at beginning and end
    if lines[0].strip() == '---' and '---' in lines[1:]:
        # Find the second ---
        for i in range(1, min(20, len(lines))):  # Check first 20 lines
            if lines[i].strip() == '---':
                return True
    return False

def check_math_delimiters(content):
    """Check for potential missing math delimiters."""
    # Patterns that might indicate math formulas without proper delimiters
    patterns = [
        r'[a-zA-Z]_{[^}]+}',  # Subscript without $
        r'[a-zA-Z]\^{[^}]+}',  # Superscript without $
        r'\\frac{[^}]+}{[^}]+}',  # \frac without $
        r'\\sum_{[^}]+}',  # \sum without $
        r'\\int_{[^}]+}',  # \int without $
        r'[a-zA-Z]_{[^}]+}\^{[^}]+}',  # Both subscript and superscript
    ]
    
    issues = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Check if it's already inside $ or $$
            before = content[:content.find(match)]
            after = content[content.find(match)+len(match):]
            
            # Count $ before the match
            dollars_before = before.count('$') - before.count(r'\$')
            dollars_after = after.count('$') - after.count(r'\$')
            
            # If odd number of $ before, it might be inside math
            if dollars_before % 2 == 0:  # Not inside math
                # Check if it's near a $ (within 10 chars)
                if not re.search(r'\$[^$]{0,10}' + re.escape(match), before) and \
                   not re.search(re.escape(match) + r'[^$]{0,10}\$', after):
                    issues.append(match)
    
    return issues

def main():
    wiki_dir = 'wiki'
    print("=== 格式合规分析 ===")
    
    frontmatter_issues = []
    math_issues = []
    
    for filename in os.listdir(wiki_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(wiki_dir, filename)
            content = read_file_content(filepath)
            
            # Check frontmatter
            if not check_frontmatter(content):
                frontmatter_issues.append(filename)
            
            # Check math delimiters
            issues = check_math_delimiters(content)
            if issues:
                math_issues.append((filename, issues))
    
    print("\n1. YAML Frontmatter 检查:")
    if frontmatter_issues:
        print(f"   发现 {len(frontmatter_issues)} 个文件缺少 YAML Frontmatter:")
        for f in frontmatter_issues:
            print(f"     - {f}")
    else:
        print("   所有文件都有 YAML Frontmatter ✓")
    
    print("\n2. 数学公式定界符检查:")
    if math_issues:
        print(f"   发现 {len(math_issues)} 个文件可能有数学公式定界符问题:")
        for filename, issues in math_issues:
            print(f"     - {filename}:")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"       可能遗漏 $: {issue}")
            if len(issues) > 3:
                print(f"       还有 {len(issues)-3} 个其他问题...")
    else:
        print("   未发现明显的数学公式定界符问题 ✓")
    
    # Also check for common LaTeX patterns without delimiters
    print("\n3. 常见LaTeX模式检查:")
    common_latex_patterns = [
        (r'\\alpha|\\beta|\\gamma|\\delta|\\epsilon', "希腊字母"),
        (r'\\times|\\cdot|\\div|\\pm', "数学运算符"),
        (r'\\leq|\\geq|\\neq|\\approx|\\equiv', "关系运算符"),
        (r'\\in|\\subset|\\subseteq|\\cup|\\cap', "集合符号"),
    ]
    
    for pattern, description in common_latex_patterns:
        files_with_pattern = []
        for filename in os.listdir(wiki_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(wiki_dir, filename)
                content = read_file_content(filepath)
                matches = re.findall(pattern, content)
                if matches:
                    # Check if they're inside math mode
                    for match in matches:
                        pos = content.find(match)
                        before = content[:pos]
                        dollars_before = before.count('$') - before.count(r'\$')
                        if dollars_before % 2 == 0:  # Not inside math
                            files_with_pattern.append(filename)
                            break
        
        if files_with_pattern:
            print(f"   {description} 可能不在数学模式中: {', '.join(set(files_with_pattern))}")

if __name__ == '__main__':
    main()
