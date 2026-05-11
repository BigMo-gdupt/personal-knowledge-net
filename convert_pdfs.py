"""
PDF 批量转换脚本：将 _staging_pdf/ 中的 PDF 通过 marker 转为 Markdown，输出到 raw/ 目录。

功能：
1. 扫描 _staging_pdf/ 中的所有 PDF 文件
2. 检查 manifest.json 避免重复转换
3. 自动处理文件名过长问题（截断 + 保留映射关系）
4. 调用 marker_single 进行转换
5. 更新 manifest.json 记录

使用方式：
    python convert_pdfs.py
    python convert_pdfs.py --staging _staging_pdf --output raw --max-name-length 80
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# ============ 配置 ============
DEFAULT_STAGING_DIR = "_staging_pdf"
DEFAULT_RAW_DIR = "raw"
DEFAULT_MAX_NAME_LENGTH = 80  # 文件名（不含扩展名）最大长度
MANIFEST_FILE = "manifest.json"
# ================================


def sanitize_paper_id(stem_name: str, max_length: int = DEFAULT_MAX_NAME_LENGTH) -> str:
    """
    将 PDF 文件名（不含扩展名）清理为合法的 paper_id。
    
    注意：输入应该是已经去掉 .pdf 扩展名的文件名 stem。
    
    规则：
    - 保留字母、数字、点号、下划线、连字符、中文
    - 其他特殊字符替换为下划线
    - 如果长度超过 max_length，截断并添加短哈希后缀避免冲突
    """
    import re
    import hashlib
    
    name = stem_name
    
    # 替换空格和特殊字符为下划线（保留点号、字母、数字、下划线、连字符、中文）
    safe_name = re.sub(r'[^\w\u4e00-\u9fff.\-]', '_', name)
    # 合并连续下划线
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    
    if len(safe_name) <= max_length:
        return safe_name
    
    # 截断并添加原始文件名的短哈希以避免冲突
    truncated = safe_name[:max_length - 8]
    short_hash = hashlib.md5(name.encode('utf-8')).hexdigest()[:6]
    return f"{truncated}_{short_hash}"


def load_manifest(project_root: Path) -> dict:
    """加载 manifest.json，如果不存在则创建空结构。"""
    manifest_path = project_root / MANIFEST_FILE
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_papers": []}


def save_manifest(project_root: Path, manifest: dict):
    """保存 manifest.json。"""
    manifest_path = project_root / MANIFEST_FILE
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def is_already_processed(manifest: dict, paper_id: str) -> bool:
    """检查论文是否已经处理过。"""
    for entry in manifest.get("processed_papers", []):
        if entry.get("paper_id") == paper_id:
            return True
    return False


def convert_pdf_with_marker(pdf_path: Path, output_dir: Path) -> bool:
    """
    调用 marker_single 将单个 PDF 转换为 Markdown。
    
    处理文件名中的空格：将 PDF 复制到临时目录的无空格短文件名，
    转换后再将输出移回目标位置。
    
    Args:
        pdf_path: PDF 文件的完整路径
        output_dir: 输出目录（marker 会在此目录下创建以文件名命名的子目录）
    
    Returns:
        True 表示转换成功
    """
    import tempfile
    import shutil
    
    # 如果文件名包含空格或特殊字符，使用临时短文件名
    original_name = pdf_path.stem
    has_special_chars = any(c in original_name for c in [' ', '\t', '\n', '(', ')', '&', ';', '|', '<', '>'])
    
    if has_special_chars or len(original_name) > 50:
        # 使用临时目录和无空格文件名
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_pdf = Path(tmp_dir) / "input.pdf"
            shutil.copy2(pdf_path, tmp_pdf)
            
            marker_cmd = os.environ.get("MARKER_CMD", "marker_single")
            cmd = [
                marker_cmd,
                str(tmp_pdf),
                "--output_dir", str(tmp_dir),
                "--output_format", "markdown",
            ]
            
            print(f"  执行命令（临时文件模式）: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                if result.returncode != 0:
                    print(f"  [错误] marker 转换失败 (返回码 {result.returncode})")
                    if result.stderr:
                        err_lines = result.stderr.strip().split('\n')
                        for line in err_lines[-5:]:
                            print(f"    {line}")
                    return False
                
                # marker 输出在 tmp_dir/input/ 目录下
                marker_output = Path(tmp_dir) / "input"
                if marker_output.exists():
                    return True
                return False
                
            except subprocess.TimeoutExpired:
                print(f"  [错误] marker 转换超时（>10分钟）")
                return False
            except FileNotFoundError:
                print(f"  [错误] 未找到 marker 命令，请确认已安装: pip install marker-pdf")
                return False
    else:
        # 正常模式：直接使用原文件
        marker_cmd = os.environ.get("MARKER_CMD", "marker_single")
        cmd = [
            marker_cmd,
            str(pdf_path),
            "--output_dir", str(output_dir),
            "--output_format", "markdown",
        ]
        
        print(f"  执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                print(f"  [错误] marker 转换失败 (返回码 {result.returncode})")
                if result.stderr:
                    err_lines = result.stderr.strip().split('\n')
                    for line in err_lines[-5:]:
                        print(f"    {line}")
                return False
            return True
        except subprocess.TimeoutExpired:
            print(f"  [错误] marker 转换超时（>10分钟）")
            return False
        except FileNotFoundError:
            print(f"  [错误] 未找到 marker 命令，请确认已安装: pip install marker-pdf")
            return False


def convert_pdf_with_copy(pdf_path: Path, output_dir: Path) -> bool:
    """
    备选方案：如果文件名过长导致 marker 失败，先将 PDF 复制到临时短文件名，
    再用 marker 转换，最后将输出目录重命名。
    
    Args:
        pdf_path: 原始 PDF 路径
        output_dir: 输出根目录
    
    Returns:
        True 表示转换成功
    """
    import tempfile
    
    # 创建临时目录和短文件名
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_pdf = Path(tmp_dir) / "paper.pdf"
        shutil.copy2(pdf_path, tmp_pdf)
        
        marker_cmd = os.environ.get("MARKER_CMD", "marker_single")
        cmd = [
            marker_cmd,
            str(tmp_pdf),
            "--output_dir", str(tmp_dir),
            "--output_format", "markdown",
        ]
        
        print(f"  执行命令（短文件名模式）: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode != 0:
                print(f"  [错误] marker 转换失败 (返回码 {result.returncode})")
                if result.stderr:
                    err_lines = result.stderr.strip().split('\n')
                    for line in err_lines[-5:]:
                        print(f"    {line}")
                return False
            
            # marker 输出在 tmp_dir/paper/ 目录下
            marker_output = Path(tmp_dir) / "paper"
            if marker_output.exists():
                return True
            return False
            
        except subprocess.TimeoutExpired:
            print(f"  [错误] marker 转换超时（>10分钟）")
            return False
        except FileNotFoundError:
            print(f"  [错误] 未找到 marker 命令，请确认已安装: pip install marker-pdf")
            return False


def main():
    parser = argparse.ArgumentParser(description="批量将 PDF 转换为 Markdown（通过 marker）")
    parser.add_argument("--staging", default=DEFAULT_STAGING_DIR, help="PDF 源目录（默认: _staging_pdf）")
    parser.add_argument("--output", default=DEFAULT_RAW_DIR, help="Markdown 输出目录（默认: raw）")
    parser.add_argument("--max-name-length", type=int, default=DEFAULT_MAX_NAME_LENGTH,
                        help=f"文件名最大长度（默认: {DEFAULT_MAX_NAME_LENGTH}）")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要处理的文件，不实际执行")
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.resolve()
    staging_dir = project_root / args.staging
    output_dir = project_root / args.output
    
    # 检查目录
    if not staging_dir.exists():
        print(f"[错误] 源目录不存在: {staging_dir}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 扫描 PDF 文件
    pdf_files = sorted(staging_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"[信息] 在 {staging_dir} 中未找到 PDF 文件。")
        sys.exit(0)
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件")
    print("=" * 50)
    
    # 加载 manifest
    manifest = load_manifest(project_root)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for pdf_path in pdf_files:
        original_name = pdf_path.stem  # 不含扩展名
        paper_id = sanitize_paper_id(original_name, args.max_name_length)
        
        print(f"\n📄 {pdf_path.name}")
        print(f"   paper_id: {paper_id}")
        
        # 检查是否已处理
        if is_already_processed(manifest, paper_id):
            print(f"   ⏭️  已处理过，跳过")
            skip_count += 1
            continue
        
        # 检查输出目录是否已存在
        raw_subdir = output_dir / paper_id
        raw_md = raw_subdir / f"{paper_id}.md"
        
        if raw_md.exists():
            print(f"   ⏭️  输出文件已存在，跳过")
            skip_count += 1
            continue
        
        if args.dry_run:
            print(f"   [DRY RUN] 将转换到: {raw_subdir}")
            success_count += 1
            continue
        
        # 如果文件名过长，使用短文件名模式
        if len(original_name) > args.max_name_length:
            print(f"   ⚠️  文件名过长（{len(original_name)}字符），使用短文件名模式转换")
            
            # 先创建目标目录
            raw_subdir.mkdir(parents=True, exist_ok=True)
            
            # 使用临时短文件名转换
            import tempfile
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_pdf = Path(tmp_dir) / "paper.pdf"
                shutil.copy2(pdf_path, tmp_pdf)
                
                success = convert_pdf_with_marker(tmp_pdf, Path(tmp_dir))
                
                if success:
                    # 将 marker 的输出（paper/ 目录）移动到目标位置
                    marker_output = Path(tmp_dir) / "paper"
                    if marker_output.exists():
                        # 如果目标目录已有内容，先清理
                        if raw_subdir.exists():
                            shutil.rmtree(raw_subdir)
                        shutil.copytree(marker_output, raw_subdir)
                        
                        # 重命名输出的 md 文件
                        for md_file in raw_subdir.glob("*.md"):
                            new_md = raw_subdir / f"{paper_id}.md"
                            if md_file != new_md:
                                md_file.rename(new_md)
                                break
                        
                        print(f"   ✅ 转换成功 → {raw_md}")
                        success_count += 1
                    else:
                        print(f"   [错误] marker 输出目录未找到")
                        error_count += 1
                else:
                    error_count += 1
        else:
            # 正常模式：直接用 marker 转换
            success = convert_pdf_with_marker(pdf_path, output_dir)
            
            if success:
                # marker 会在 output_dir 下创建以 PDF 文件名命名的子目录
                # 检查输出位置
                marker_output_dir = output_dir / original_name
                if marker_output_dir.exists() and marker_output_dir != raw_subdir:
                    # marker 用了原始文件名，需要重命名
                    shutil.move(str(marker_output_dir), str(raw_subdir))
                
                # 确保输出 md 文件名正确
                if raw_subdir.exists():
                    for md_file in raw_subdir.glob("*.md"):
                        if md_file.name != f"{paper_id}.md":
                            new_md = raw_subdir / f"{paper_id}.md"
                            md_file.rename(new_md)
                            break
                
                if raw_md.exists():
                    print(f"   ✅ 转换成功 → {raw_md}")
                    success_count += 1
                else:
                    print(f"   [错误] 未找到输出 Markdown 文件")
                    error_count += 1
            else:
                error_count += 1
        
        # 更新 manifest
        if raw_md.exists() and not args.dry_run:
            manifest["processed_papers"].append({
                "paper_id": paper_id,
                "raw_md_path": f"{args.output}/{paper_id}/{paper_id}.md",
                "source_pdf": f"{args.staging}/{pdf_path.name}",
                "original_filename": pdf_path.name,
                "converted_date": datetime.now().strftime("%Y-%m-%d"),
                "wiki_nodes_created": []
            })
            save_manifest(project_root, manifest)
    
    # 汇总
    print("\n" + "=" * 50)
    print(f"转换完成: ✅ {success_count} 成功 | ⏭️  {skip_count} 跳过 | ❌ {error_count} 失败")


if __name__ == "__main__":
    main()
