#!/bin/bash

# Tropical Cloud Detection - Cleanup Script
# Removes unnecessary files and directories

echo "🧹 Cleaning up Tropical Cloud Detection project..."

# Remove unnecessary files
echo "📁 Removing unnecessary files..."

# Remove test files
rm -f test_*.py
rm -f *_test.py

# Remove temporary files
rm -f *.tmp
rm -f *.temp
rm -f *.log

# Remove backup files
rm -f *.bak
rm -f *.backup

# Remove cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null

# Remove IDE files
rm -rf .vscode/
rm -rf .idea/
rm -f *.swp
rm -f *.swo

# Remove OS files
find . -name ".DS_Store" -delete
find . -name "Thumbs.db" -delete

# Remove large sample files (if any)
find . -name "*.h5" -size +10M -delete
find . -name "*.hdf5" -size +10M -delete

# Clean up media directory (keep structure)
find media/ -name "*.h5" -delete
find media/ -name "*.hdf5" -delete
find media/ -name "*.nc" -delete

# Remove empty directories
find . -type d -empty -delete

echo "✅ Cleanup completed!"
echo ""
echo "📊 Project size after cleanup:"
du -sh . 2>/dev/null || echo "Could not determine project size"

echo ""
echo "🎯 Next steps:"
echo "1. Test the application: python manage.py runserver"
echo "2. Deploy to production: ./deploy-cloud-run.sh"
echo "3. Monitor performance in Google Cloud Console" 