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
                        print(f"[Error] Multiple @progress annotations in {rel_path}, skipping!")
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

    print("\n📊 Summary")
    print("-----------")
    print(f"Marked files: {total_tracked}")
    print(f"Completed files: {completed}")
    print(f"Average progress: {average:.2%}")
    print(f"Unmarked files: {unmarked_count}")

def export_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['file', 'progress', 'note'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"\n✅ CSV file exported: {output_file}")

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze @progress annotations in code")
    parser.add_argument('path', nargs='?', default='.', help='Root directory path (default: current directory)')
    parser.add_argument('--csv', default='progress_report.csv', help='CSV output filename')
    parser.add_argument('--ext', help='Custom file extensions (comma-separated), e.g. .py,.js')
    parser.add_argument('--exclude', help='Exclude folders (comma-separated), e.g. node_modules,dist,build')
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
    print(f"\nElapsed time: {time.time() - start:.2f} seconds")

if __name__ == '__main__':
    main()