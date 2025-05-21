#!/bin/bash
set -e

echo "📦 清理旧文件..."
rm -rf dist build *.egg-info

echo "🔨 构建包..."
python -m build

echo "🚀 上传到 PyPI..."
twine upload dist/*

echo "✅ 发布完成！"