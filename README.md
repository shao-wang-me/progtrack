# progtrack

📊 **Track `@progress` comments in your codebase to monitor development progress.**

`progtrack` is a simple CLI tool that scans your source code files for `@progress` annotations and summarizes the implementation status across files. It helps you track how much of your code is complete, in progress, or untracked.

## ✨ Features

- Detects `@progress` annotations like:
  ```python
  # @progress 80%: "needs testing"
  # @progress 80%: 'needs testing'
  # @progress 0.5
  # @progress done
  ```
- Supports multiple file types: .py, .js, .ts, .vue, .html (customisable)
- Generates CLI summary and optional CSV report
- Reports average completion rate
- Ignores unmarked files by default
- Configurable exclude folders (e.g. node_modules)

## 🧰 Installation

```bash
pip install progtrack
```

## 🚀 Usage

```bash
# Basic
progress
progress .
# Output to CSV
progress --csv my_report.csv
# Custom file types
progress --ext .py,.vue,.ts
# Exclude folders
progress --exclude node_modules,dist,build
```

## 📦 Example Output

```txt
file                 progress    note
------------------  ----------  ----------------------
main.py               1.00
api/data.py           0.80       needs tests
auth/login.vue        0.50       basic done

📊 Summary
-----------
Marked files: 3
Completed files: 1
Average progress: 76.67%
Unmarked files: 2
```

## 🪪 License

MIT © 2025

## 🤖 GitHub / PyPI
- GitHub: https://github.com/shao-wang-me/progtrack
- PyPI: https://pypi.org/project/progtrack