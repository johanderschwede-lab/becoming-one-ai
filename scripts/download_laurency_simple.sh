#!/bin/bash

# Simple Laurency PDF Downloader
# ==============================
# One-liner approach using wget's recursive download with PDF filtering

# Configuration
BASE_URL="https://www.laurency.com"
OUTPUT_DIR="laurency_pdfs_simple"

echo "🚀 Simple Laurency PDF Download"
echo "==============================="
echo "Base URL: $BASE_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📥 Starting recursive download (PDFs only)..."

# Use wget to recursively download only PDF files
wget \
    --recursive \
    --no-clobber \
    --page-requisites \
    --convert-links \
    --restrict-file-names=windows \
    --domains laurency.com \
    --no-parent \
    --accept pdf \
    --directory-prefix="$OUTPUT_DIR" \
    --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    --wait=2 \
    --random-wait \
    --timeout=30 \
    --tries=3 \
    --progress=bar:force \
    "$BASE_URL"

echo ""
echo "✅ Download complete!"

# Count and organize results
total_pdfs=$(find "$OUTPUT_DIR" -name "*.pdf" | wc -l)
echo "📊 Total PDFs downloaded: $total_pdfs"

# List all downloaded PDFs
if [[ $total_pdfs -gt 0 ]]; then
    echo ""
    echo "📄 Downloaded PDFs:"
    find "$OUTPUT_DIR" -name "*.pdf" -exec basename {} \; | sort
    
    # Create a simple list for reference
    find "$OUTPUT_DIR" -name "*.pdf" -exec basename {} \; | sort > "$OUTPUT_DIR/pdf_list.txt"
    echo ""
    echo "📝 PDF list saved to: $OUTPUT_DIR/pdf_list.txt"
fi

echo ""
echo "🎉 All done! Check $OUTPUT_DIR for your PDFs"
