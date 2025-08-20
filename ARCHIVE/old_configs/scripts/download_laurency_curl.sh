#!/bin/bash

# Laurency PDF Downloader using curl
# ==================================
# Alternative approach using curl for systems where wget isn't available

set -e

# Configuration
BASE_URL="https://www.laurency.com"
OUTPUT_DIR="laurency_pdfs_curl"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🚀 Laurency PDF Downloader (curl version)"
echo "========================================="

# Check if curl is available
if ! command -v curl &> /dev/null; then
    log_error "curl is required but not installed"
    exit 1
fi

# Create directories
log_info "Creating directories..."
mkdir -p "$OUTPUT_DIR"/{swedish,english,german,other,metadata}

# Function to extract PDF links from a page
extract_pdf_links() {
    local url="$1"
    local temp_file=$(mktemp)
    
    log_info "Checking: $url"
    
    # Download page and extract PDF links
    curl -s --user-agent "$USER_AGENT" --max-time 30 "$url" | \
    grep -oiE 'href="[^"]*\.pdf"' | \
    sed 's/href="//g' | \
    sed 's/"//g' > "$temp_file"
    
    # Convert relative URLs to absolute and output
    while IFS= read -r link; do
        if [[ $link == http* ]]; then
            echo "$link"
        else
            # Remove leading slash if present
            link=${link#/}
            echo "$BASE_URL/$link"
        fi
    done < "$temp_file"
    
    rm -f "$temp_file"
}

# Discover all PDF links
log_info "Discovering PDF links..."
TEMP_LINKS=$(mktemp)

# Pages to check
PAGES=(
    "$BASE_URL"
    "$BASE_URL/index.html"
    "$BASE_URL/english.html"
    "$BASE_URL/svenska.html"
    "$BASE_URL/deutsch.html"
)

for page in "${PAGES[@]}"; do
    extract_pdf_links "$page" >> "$TEMP_LINKS"
    sleep 1
done

# Remove duplicates
sort "$TEMP_LINKS" | uniq > "${TEMP_LINKS}.unique"
mv "${TEMP_LINKS}.unique" "$TEMP_LINKS"

PDF_COUNT=$(wc -l < "$TEMP_LINKS")
log_success "Found $PDF_COUNT unique PDF links"

if [[ $PDF_COUNT -eq 0 ]]; then
    log_error "No PDF files found!"
    rm -f "$TEMP_LINKS"
    exit 1
fi

# Save discovered links
cp "$TEMP_LINKS" "$OUTPUT_DIR/metadata/discovered_links.txt"

# Function to detect language
detect_language() {
    local url="$1"
    local url_lower=$(echo "$url" | tr '[:upper:]' '[:lower:]')
    
    if [[ $url_lower =~ (svenska|svensk|verklighetskunskap|människans|vises) ]]; then
        echo "swedish"
    elif [[ $url_lower =~ (english|knowledge|reality|philosopher|stone|way|man) ]]; then
        echo "english"  
    elif [[ $url_lower =~ (deutsch|german|erkenntnis|wirklichkeit) ]]; then
        echo "german"
    else
        echo "other"
    fi
}

# Download PDFs
log_info "Starting downloads..."

current=0
successful=0
failed=0

while IFS= read -r pdf_url; do
    [[ -z "$pdf_url" ]] && continue
    
    current=$((current + 1))
    filename=$(basename "$pdf_url")
    language=$(detect_language "$pdf_url")
    
    # Determine target directory
    case $language in
        "swedish") target_dir="$OUTPUT_DIR/swedish" ;;
        "english") target_dir="$OUTPUT_DIR/english" ;;
        "german") target_dir="$OUTPUT_DIR/german" ;;
        *) target_dir="$OUTPUT_DIR/other" ;;
    esac
    
    target_path="$target_dir/$filename"
    
    log_info "[$current/$PDF_COUNT] $filename ($language)"
    
    # Skip if exists
    if [[ -f "$target_path" ]]; then
        log_warning "Already exists, skipping"
        continue
    fi
    
    # Download with curl
    if curl --user-agent "$USER_AGENT" \
            --max-time 60 \
            --retry 3 \
            --retry-delay 5 \
            --location \
            --output "$target_path" \
            --progress-bar \
            "$pdf_url"; then
        
        file_size=$(du -h "$target_path" | cut -f1)
        log_success "Downloaded $filename ($file_size)"
        successful=$((successful + 1))
    else
        log_error "Failed to download $filename"
        [[ -f "$target_path" ]] && rm "$target_path"
        failed=$((failed + 1))
    fi
    
    sleep 2  # Be respectful
    
done < "$TEMP_LINKS"

# Generate summary
log_info "Generating summary..."

summary_file="$OUTPUT_DIR/metadata/summary.txt"
{
    echo "Laurency PDF Download Summary"
    echo "============================="
    echo "Date: $(date)"
    echo "Total discovered: $PDF_COUNT"
    echo "Successful: $successful"
    echo "Failed: $failed"
    echo ""
    
    for dir in swedish english german other; do
        count=$(find "$OUTPUT_DIR/$dir" -name "*.pdf" 2>/dev/null | wc -l)
        if [[ $count -gt 0 ]]; then
            echo "$dir: $count files"
        fi
    done
} > "$summary_file"

# Cleanup
rm -f "$TEMP_LINKS"

# Final summary
echo ""
log_success "=== DOWNLOAD COMPLETE ==="
echo "  Successful: $successful"
echo "  Failed: $failed"
echo "  Location: $OUTPUT_DIR"
echo ""

total_downloaded=$(find "$OUTPUT_DIR" -name "*.pdf" | wc -l)
log_success "🎉 Downloaded $total_downloaded PDF files total!"
