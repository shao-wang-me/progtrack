import os
import re
import csv
import time
import argparse

DEFAULT_EXTENSIONS = ('.py', '.js', '.ts', '.vue', '.html')
DEFAULT_EXCLUDE_DIRS = {'node_modules', '.git', '__pycache__'}

def normalize_progress(value):
    value = value.lower()
    if value == 'done':
        return 1.0
    if value.endswith('%'):
        return float(value.strip('%')) / 100
    return float(value)

def clean_note(note):
    if note:
        return note.strip().strip('"').strip("'")
    return ''

def collect_progress(root_dir, allowed_exts, excluded_dirs):
    results = []
    unmarked_count = 0
    pattern = re.compile(r'@progress\s+(?P<value>\d+%?|\d*\.\d+|done)\s*:?\s*(?P<note>"[^"]*"|\'[^\']*\')?', re.IGNORECASE)

    for root, dirs, files in os.walk(root_dir):
        # 排除指定文件夹
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for f in files:
            if not f.endswith(allowed_exts):
                continue

            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, root_dir)

            try:
                with open(path, encoding='utf-8') as file:
                    content = file.read()
                    matches = list(pattern.finditer(content))

                    if len(matches) > 1:
                        print(f"[错误] {rel_path} 中有多个 @progress 标记，跳过处理！")
                        continue
                    elif len(matches) == 1:
                        match = matches[0]
                        raw_value = match.group('value')
                        note = clean_note(match.group('note'))
                        try:
                            percent = normalize_progress(raw_value)
                        except ValueError:
                            percent = None
                        results.append({
                            'file': rel_path,
                            'progress': percent,
                            'note': note
                        })
                    else:
                        unmarked_count += 1

            except UnicodeDecodeError:
                continue  # 跳过非 UTF-8 编码文件

    return results, unmarked_count

def summarize(results, unmarked_count):
    valid = [r for r in results if r['progress'] is not None]
    total_tracked = len(results)
    completed = sum(1 for r in valid if r['progress'] == 1.0)
    average = sum(r['progress'] for r in valid) / len(valid) if valid else 0.0

    print("\n📊 汇总信息")
    print("-----------")
    print(f"有标记的文件数：{total_tracked}")
    print(f"已完成的文件数：{completed}")
    print(f"平均完成度：{average:.2%}")
    print(f"未标记文件数：{unmarked_count}")

def export_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['file', 'progress', 'note'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"\n✅ 已导出 CSV 文件：{output_file}")

def parse_args():
    parser = argparse.ArgumentParser(description="统计代码中的 @progress 注释进度")
    parser.add_argument('path', nargs='?', default='.', help='根目录路径，默认为当前目录')
    parser.add_argument('--csv', default='progress_report.csv', help='CSV 输出文件名')
    parser.add_argument('--ext', help='自定义文件扩展名（用逗号分隔），如：.py,.js')
    parser.add_argument('--exclude', help='排除目录（用逗号分隔），如：node_modules,dist,build')
    return parser.parse_args()

def main():
    from tabulate import tabulate

    args = parse_args()
    path = args.path

    # 处理扩展名
    extensions = tuple(args.ext.split(',')) if args.ext else DEFAULT_EXTENSIONS

    # 处理排除目录
    exclude_dirs = set(args.exclude.split(',')) if args.exclude else DEFAULT_EXCLUDE_DIRS

    start = time.time()
    data, unmarked_count = collect_progress(path, extensions, exclude_dirs)

    print(tabulate(data, headers={'file': 'file', 'progress': 'progress', 'note': 'note'}, floatfmt=".2f"))
    summarize(data, unmarked_count)
    export_csv(data, args.csv)
    print(f"\n解析耗时：{time.time() - start:.2f} 秒")

if __name__ == '__main__':
    main()