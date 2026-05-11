"""
个人笔记处理脚本：读取 _ManuNote/ 中的 Markdown 文件，调用 DeepSeek API 转化为知识库节点。

功能：
1. 扫描 _ManuNote/ 中的所有 .md 文件
2. 检查 manifest.json 避免重复处理
3. 调用 DeepSeek API 按 DEEPSEEK_SCHEMA 规范处理笔记
4. 生成 wiki/ 节点
5. 更新 manifest.json

使用方式：
    python process_manunote.py <note_filename.md>
    python process_manunote.py 我的深度学习笔记.md
    python process_manunote.py --list  # 列出所有待处理笔记
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


# ============ 配置 ============
DEFAULT_MANUNOTE_DIR = "_ManuNote"
DEFAULT_WIKI_DIR = "wiki"
MANIFEST_FILE = "manifest.json"
SCHEMA_FILE = "DEEPSEEK_SCHEMA.md"
# ================================


def load_manifest(project_root: Path) -> dict:
    """加载 manifest.json，如果不存在则创建空结构。"""
    manifest_path = project_root / MANIFEST_FILE
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_papers": [], "processed_manunotes": []}


def save_manifest(project_root: Path, manifest: dict):
    """保存 manifest.json。"""
    manifest_path = project_root / MANIFEST_FILE
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def is_note_processed(manifest: dict, note_id: str) -> bool:
    """检查笔记是否已经处理过。"""
    for entry in manifest.get("processed_manunotes", []):
        if entry.get("note_id") == note_id:
            return True
    return False


def list_pending_notes(project_root: Path, manifest: dict) -> list:
    """列出所有待处理的笔记文件。"""
    manunote_dir = project_root / DEFAULT_MANUNOTE_DIR
    if not manunote_dir.exists():
        return []
    
    all_md_files = list(manunote_dir.glob("*.md"))
    processed_ids = {e.get("note_id") for e in manifest.get("processed_manunotes", [])}
    
    pending = []
    for md_file in all_md_files:
        note_id = md_file.stem
        if note_id not in processed_ids:
            pending.append(md_file)
    
    return pending


def read_note_content(note_path: Path) -> str:
    """读取笔记文件内容。"""
    with open(note_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_schema(project_root: Path) -> str:
    """读取 DEEPSEEK_SCHEMA.md 内容。"""
    schema_path = project_root / SCHEMA_FILE
    if schema_path.exists():
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def build_prompt(note_content: str, schema: str, note_id: str) -> str:
    """
    构建发送给 DeepSeek 的 prompt。
    
    根据 DEEPSEEK_SCHEMA 规范，要求 DeepSeek：
    1. 读取笔记内容
    2. 提取核心概念
    3. 按规范创建 wiki 节点
    4. 返回创建的节点列表
    """
    prompt = f"""你是一个知识编译引擎。请严格按照以下规范处理个人笔记：

## 输入规范（DEEPSEEK_SCHEMA）

{schema}

## 当前任务

请处理以下个人笔记，提取核心概念并创建 wiki 节点。

**笔记来源**: `_ManuNote/{note_id}.md`
**笔记内容**:

```markdown
{note_content}
```

## 输出要求

1. 分析笔记内容，提取 1-5 个核心概念
2. 为每个概念创建符合规范的 wiki 节点（YAML frontmatter + 定义 + 数学推导 + 前提条件 + 关联拓扑）
3. 在 [关联拓扑] 中建立与其他 wiki 节点的双向链接
4. 返回本次创建的节点名称列表（用于更新 manifest）

请直接输出创建的 wiki 节点内容，格式如下：

---
**创建的节点**: ["节点名1", "节点名2", ...]

**节点1内容**:
```markdown
...
```

**节点2内容**:
```markdown
...
```
---
"""
    return prompt


def process_note(note_path: Path, project_root: Path, manifest: dict, dry_run: bool = False) -> list:
    """
    处理单个笔记文件。
    
    Args:
        note_path: 笔记文件路径
        project_root: 项目根目录
        manifest: manifest 数据
        dry_run: 是否为预览模式
    
    Returns:
        创建的 wiki 节点名称列表
    """
    note_id = note_path.stem
    
    print(f"\n📄 处理笔记: {note_path.name}")
    print(f"   note_id: {note_id}")
    
    # 检查是否已处理
    if is_note_processed(manifest, note_id):
        print(f"   ⏭️  已处理过，跳过")
        return []
    
    if dry_run:
        print(f"   [DRY RUN] 将处理此笔记")
        return ["节点预览"]
    
    # 读取笔记内容
    note_content = read_note_content(note_path)
    schema = read_schema(project_root)
    
    # 构建 prompt
    prompt = build_prompt(note_content, schema, note_id)
    
    print(f"   笔记长度: {len(note_content)} 字符")
    print(f"   已构建 DeepSeek prompt，请手动调用 API 处理")
    print(f"   Prompt 长度: {len(prompt)} 字符 (~{len(prompt)//3} tokens)")
    
    # 保存 prompt 到临时文件，方便用户手动调用
    temp_prompt_file = project_root / f"_temp_prompt_{note_id}.txt"
    with open(temp_prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"   Prompt 已保存到: {temp_prompt_file}")
    print(f"   请将此文件内容发送给 DeepSeek，然后将返回的 wiki 节点保存到 {DEFAULT_WIKI_DIR}/")
    
    # 注意：实际 API 调用需要用户手动完成或配置 API key
    # 这里仅提供 prompt 生成和文件管理功能
    
    return []  # 返回空列表，因为实际处理需要 DeepSeek 返回


def update_manifest_after_processing(project_root: Path, note_id: str, wiki_nodes: list):
    """处理完成后更新 manifest.json。"""
    manifest = load_manifest(project_root)
    
    # 检查是否已存在
    for entry in manifest.get("processed_manunotes", []):
        if entry.get("note_id") == note_id:
            return  # 已存在，不重复添加
    
    # 添加新记录
    if "processed_manunotes" not in manifest:
        manifest["processed_manunotes"] = []
    
    manifest["processed_manunotes"].append({
        "note_id": note_id,
        "source_path": f"{DEFAULT_MANUNOTE_DIR}/{note_id}.md",
        "processed_date": datetime.now().strftime("%Y-%m-%d"),
        "wiki_nodes_created": wiki_nodes
    })
    
    save_manifest(project_root, manifest)
    print(f"   ✅ manifest.json 已更新")


def main():
    parser = argparse.ArgumentParser(description="处理个人笔记并转化为知识库节点")
    parser.add_argument("note_file", nargs="?", help="要处理的笔记文件名（如：我的笔记.md）")
    parser.add_argument("--list", action="store_true", help="列出所有待处理的笔记")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要处理的文件，不实际执行")
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.resolve()
    manunote_dir = project_root / DEFAULT_MANUNOTE_DIR
    
    # 确保目录存在
    if not manunote_dir.exists():
        print(f"[信息] 创建 {manunote_dir} 目录")
        manunote_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载 manifest
    manifest = load_manifest(project_root)
    
    if args.list:
        # 列出待处理笔记
        pending = list_pending_notes(project_root, manifest)
        print(f"\n待处理笔记 ({len(pending)} 个):")
        for i, note in enumerate(pending, 1):
            print(f"  {i}. {note.name}")
        
        processed = manifest.get("processed_manunotes", [])
        print(f"\n已处理笔记 ({len(processed)} 个):")
        for entry in processed:
            print(f"  ✓ {entry['note_id']} ({entry['processed_date']})")
        return
    
    if not args.note_file:
        print("[错误] 请指定笔记文件名，或使用 --list 查看待处理列表")
        print(f"\n用法示例:")
        print(f"  python process_manunote.py 我的笔记.md")
        print(f"  python process_manunote.py --list")
        sys.exit(1)
    
    # 处理指定笔记
    note_path = manunote_dir / args.note_file
    if not note_path.exists():
        print(f"[错误] 笔记文件不存在: {note_path}")
        sys.exit(1)
    
    wiki_nodes = process_note(note_path, project_root, manifest, dry_run=args.dry_run)
    
    if not args.dry_run and wiki_nodes:
        # 更新 manifest（实际使用时，在 DeepSeek 返回结果后调用）
        update_manifest_after_processing(project_root, note_path.stem, wiki_nodes)
    
    print("\n" + "=" * 50)
    if args.dry_run:
        print("预览模式完成")
    else:
        print("提示生成完成，请手动调用 DeepSeek API 处理")
        print(f"处理完成后，运行以下命令更新 manifest:")
        print(f"  python -c \"from process_manunote import update_manifest_after_processing; ")
        print(f"from pathlib import Path; ")
        print(f"update_manifest_after_processing(Path('.'), '{note_path.stem}', ['节点名1', '节点名2'])\"")


if __name__ == "__main__":
    main()
