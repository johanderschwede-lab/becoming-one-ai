#!/bin/bash

# Laurency PDF Downloader - Bash Script
# =====================================
# Downloads all PDF files from laurency.com
# Organizes by language (Swedish, English, German)

set -e  # Exit on any error

# Configuration
BASE_URL="https://www.laurency.com"
OUTPUT_DIR="laurency_pdfs"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    mkdir -p "$OUTPUT_DIR"/{swedish_originals,english_translations,german_translations,other_languages,metadata}
    log_success "Directories created in $OUTPUT_DIR"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v wget &> /dev/null; then
        log_error "wget is required but not installed."
        echo "Install with:"
        echo "  macOS: brew install wget"
        echo "  Ubuntu/Debian: sudo apt-get install wget"
        echo "  CentOS/RHEL: sudo yum install wget"
        exit 1
    fi
    
    if ! command -v grep &> /dev/null; then
        log_error "grep is required but not installed."
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Discover PDF links
discover_pdfs() {
    log_info "Discovering PDF links from $BASE_URL..."
    
    # Create temporary file for links
    TEMP_LINKS=$(mktemp)
    
    # Pages to check for PDF links
    PAGES=(
        "$BASE_URL"
        "$BASE_URL/index.html"
        "$BASE_URL/english.html"
        "$BASE_URL/svenska.html"
        "$BASE_URL/deutsch.html"
        "$BASE_URL/books.html"
        "$BASE_URL/downloads.html"
        "$BASE_URL/texts.html"
    )
    
    # Download each page and extract PDF links
    for page in "${PAGES[@]}"; do
        log_info "Checking page: $page"
        
        # Download page content and extract PDF links
        wget --quiet --timeout=30 --user-agent="$USER_AGENT" -O - "$page" 2>/dev/null | \
        grep -oiE 'href="[^"]*\.pdf"' | \
        sed 's/href="//g' | \
        sed 's/"//g' | \
        while read -r pdf_link; do
            # Convert relative URLs to absolute
            if [[ $pdf_link == http* ]]; then
                echo "$pdf_link" >> "$TEMP_LINKS"
            else
                echo "$BASE_URL/$pdf_link" >> "$TEMP_LINKS"
            fi
        done
        
        sleep 1  # Be respectful to the server
    done
    
    # Remove duplicates and sort
    sort "$TEMP_LINKS" | uniq > "${TEMP_LINKS}.unique"
    mv "${TEMP_LINKS}.unique" "$TEMP_LINKS"
    
    PDF_COUNT=$(wc -l < "$TEMP_LINKS")
    log_success "Found $PDF_COUNT unique PDF files"
    
    # Save discovered links for reference
    cp "$TEMP_LINKS" "$OUTPUT_DIR/metadata/discovered_pdf_links.txt"
    
    echo "$TEMP_LINKS"  # Return temp file path
}

# Detect language from filename/URL
detect_language() {
    local url="$1"
    local filename=$(basename "$url")
    local url_lower=$(echo "$url" | tr '[:upper:]' '[:lower:]')
    local filename_lower=$(echo "$filename" | tr '[:upper:]' '[:lower:]')
    
    # Swedish indicators
    if [[ $url_lower =~ (svenska|svensk|sv|verklighetskunskap|människans|vises|sten|hylozoik) ]]; then
        echo "swedish"
    # English indicators  
    elif [[ $url_lower =~ (english|eng|en|knowledge|reality|philosopher|stone|way|man|hylozoics) ]]; then
        echo "english"
    # German indicators
    elif [[ $url_lower =~ (deutsch|german|de|erkenntnis|wirklichkeit|philosoph|weg|mensch) ]]; then
        echo "german"
    else
        echo "other"
    fi
}

# Download PDFs
download_pdfs() {
    local links_file="$1"
    
    log_info "Starting PDF downloads..."
    
    local total_count=$(wc -l < "$links_file")
    local current=0
    local successful=0
    local failed=0
    
    # Download log
    local download_log="$OUTPUT_DIR/metadata/download_log.txt"
    echo "Laurency PDF Download Log - $(date)" > "$download_log"
    echo "========================================" >> "$download_log"
    
    while IFS= read -r pdf_url; do
        current=$((current + 1))
        
        if [[ -z "$pdf_url" ]]; then
            continue
        fi
        
        log_info "[$current/$total_count] Processing: $pdf_url"
        
        # Get filename and detect language
        filename=$(basename "$pdf_url")
        language=$(detect_language "$pdf_url")
        
        # Determine target directory
        case $language in
            "swedish")
                target_dir="$OUTPUT_DIR/swedish_originals"
                ;;
            "english")
                target_dir="$OUTPUT_DIR/english_translations"
                ;;
            "german")
                target_dir="$OUTPUT_DIR/german_translations"
                ;;
            *)
                target_dir="$OUTPUT_DIR/other_languages"
                ;;
        esac
        
        target_path="$target_dir/$filename"
        
        # Skip if already exists
        if [[ -f "$target_path" ]]; then
            log_warning "Skipping existing file: $filename"
            echo "SKIPPED: $pdf_url -> $target_path (already exists)" >> "$download_log"
            continue
        fi
        
        # Download the PDF
        if wget --timeout=60 --user-agent="$USER_AGENT" --quiet --show-progress -O "$target_path" "$pdf_url"; then
            file_size=$(du -h "$target_path" | cut -f1)
            log_success "Downloaded: $filename ($file_size) -> $language"
            echo "SUCCESS: $pdf_url -> $target_path ($file_size)" >> "$download_log"
            successful=$((successful + 1))
        else
            log_error "Failed to download: $filename"
            echo "FAILED: $pdf_url -> $target_path" >> "$download_log"
            failed=$((failed + 1))
            
            # Remove partial file if exists
            [[ -f "$target_path" ]] && rm "$target_path"
        fi
        
        # Be respectful to the server
        sleep 2
        
    done < "$links_file"
    
    echo "" >> "$download_log"
    echo "Summary:" >> "$download_log"
    echo "Total: $total_count" >> "$download_log"
    echo "Successful: $successful" >> "$download_log"
    echo "Failed: $failed" >> "$download_log"
    
    log_success "Download complete! Successful: $successful, Failed: $failed"
}

# Generate summary
generate_summary() {
    log_info "Generating download summary..."
    
    local summary_file="$OUTPUT_DIR/metadata/download_summary.txt"
    
    echo "Laurency PDF Download Summary" > "$summary_file"
    echo "=============================" >> "$summary_file"
    echo "Date: $(date)" >> "$summary_file"
    echo "Source: $BASE_URL" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Count files by language
    for lang_dir in swedish_originals english_translations german_translations other_languages; do
        if [[ -d "$OUTPUT_DIR/$lang_dir" ]]; then
            count=$(find "$OUTPUT_DIR/$lang_dir" -name "*.pdf" | wc -l)
            if [[ $count -gt 0 ]]; then
                echo "$lang_dir: $count files" >> "$summary_file"
                echo "" >> "$summary_file"
                find "$OUTPUT_DIR/$lang_dir" -name "*.pdf" -exec basename {} \; | sort >> "$summary_file"
                echo "" >> "$summary_file"
            fi
        fi
    done
    
    # Total files
    total_files=$(find "$OUTPUT_DIR" -name "*.pdf" | wc -l)
    echo "Total PDF files downloaded: $total_files" >> "$summary_file"
    
    log_success "Summary saved to: $summary_file"
    
    # Display summary
    echo ""
    log_success "=== DOWNLOAD SUMMARY ==="
    for lang_dir in swedish_originals english_translations german_translations other_languages; do
        if [[ -d "$OUTPUT_DIR/$lang_dir" ]]; then
            count=$(find "$OUTPUT_DIR/$lang_dir" -name "*.pdf" | wc -l)
            if [[ $count -gt 0 ]]; then
                echo "  $lang_dir: $count files"
            fi
        fi
    done
    echo "  Total: $total_files PDF files"
    echo ""
}

# Main function
main() {
    echo "🚀 Laurency PDF Downloader"
    echo "=========================="
    echo "Base URL: $BASE_URL"
    echo "Output Directory: $OUTPUT_DIR"
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Create directories
    create_directories
    
    # Discover PDF links
    links_file=$(discover_pdfs)
    
    if [[ ! -s "$links_file" ]]; then
        log_error "No PDF links found!"
        rm -f "$links_file"
        exit 1
    fi
    
    # Download PDFs
    download_pdfs "$links_file"
    
    # Generate summary
    generate_summary
    
    # Cleanup
    rm -f "$links_file"
    
    log_success "🎉 All done! Check $OUTPUT_DIR for your downloaded PDFs"
}

# Handle command line arguments
if [[ $# -gt 0 ]]; then
    BASE_URL="$1"
fi

if [[ $# -gt 1 ]]; then
    OUTPUT_DIR="$2"
fi

# Run main function
main "$@"
