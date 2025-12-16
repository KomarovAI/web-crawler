#!/bin/bash

###############################################################################
# 🚀 ULTIMATE WEBSITE DOWNLOADER CLI
# Интегрирует: httrack, wget, monolith
# Максимальная скорость и контроль
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Config
DOWNLOAD_DIR="downloads"
THREADS=16
WAIT_TIME=0.5
MAX_RATE=0

# Functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  🚀 ULTIMATE WEBSITE DOWNLOADER             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo ""
}

print_usage() {
    echo -e "${YELLOW}USAGE:${NC}"
    echo "  ./cli.sh download <URL> [METHOD]"
    echo ""
    echo -e "${YELLOW}METHODS:${NC}"
    echo "  httrack    - Maximum control & speed (recommended) ⭐"
    echo "  wget       - Built-in, ultra-fast"
    echo "  monolith   - Single file archive"
    echo "  all        - Download all 3 methods"
    echo ""
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo "  ./cli.sh download https://example.com httrack"
    echo "  ./cli.sh download https://callmedley.com all"
    echo ""
}

check_tools() {
    local missing=0
    
    echo -e "${BLUE}📋 Checking required tools...${NC}"
    
    if ! command -v wget &> /dev/null; then
        echo -e "${RED}✗ wget not found${NC}"
        missing=1
    else
        echo -e "${GREEN}✓ wget installed${NC}"
    fi
    
    if ! command -v httrack &> /dev/null; then
        echo -e "${YELLOW}⚠ httrack not found (optional)${NC}"
        echo "   Install: brew install httrack (macOS)"
        echo "   Or: sudo apt-get install httrack (Linux)"
    else
        echo -e "${GREEN}✓ httrack installed${NC}"
    fi
    
    if ! command -v monolith &> /dev/null; then
        echo -e "${YELLOW}⚠ monolith not found (optional)${NC}"
        echo "   Install: brew install monolith (macOS)"
        echo "   Or: cargo install monolith (Rust required)"
    else
        echo -e "${GREEN}✓ monolith installed${NC}"
    fi
    
    echo ""
    
    if [ $missing -eq 1 ]; then
        echo -e "${RED}❌ Missing required tools!${NC}"
        exit 1
    fi
}

download_httrack() {
    local url=$1
    local output_dir="${DOWNLOAD_DIR}/httrack_$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}🔥 Starting HTTrack download...${NC}"
    echo "   URL: $url"
    echo "   Output: $output_dir"
    echo ""
    
    mkdir -p "$output_dir"
    
    httrack "$url" \
        -O "$output_dir" \
        -%e \
        -k \
        -N100000 \
        --max-rate=$MAX_RATE \
        -c$THREADS \
        -f 10000 \
        --continue
    
    echo -e "${GREEN}✓ HTTrack download complete!${NC}"
    echo -e "${YELLOW}📁 Location: $output_dir${NC}"
    du -sh "$output_dir" 2>/dev/null || true
}

download_wget() {
    local url=$1
    local output_dir="${DOWNLOAD_DIR}/wget_$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}⚡ Starting WGET download...${NC}"
    echo "   URL: $url"
    echo "   Output: $output_dir"
    echo ""
    
    mkdir -p "$output_dir"
    
    wget --mirror \
        --page-requisites \
        --adjust-extension \
        --span-hosts \
        --convert-links \
        --restrict-file-names=windows \
        --domains "$(echo $url | cut -d'/' -f3)" \
        --no-parent \
        --wait=$WAIT_TIME \
        -P "$output_dir" \
        "$url"
    
    echo -e "${GREEN}✓ WGET download complete!${NC}"
    echo -e "${YELLOW}📁 Location: $output_dir${NC}"
    du -sh "$output_dir" 2>/dev/null || true
}

download_monolith() {
    local url=$1
    local domain=$(echo $url | cut -d'/' -f3 | sed 's/www\.//')
    local output_file="${DOWNLOAD_DIR}/monolith_${domain}_$(date +%Y%m%d_%H%M%S).html"
    
    echo -e "${BLUE}📦 Starting Monolith download...${NC}"
    echo "   URL: $url"
    echo "   Output: $output_file"
    echo ""
    
    mkdir -p "$DOWNLOAD_DIR"
    
    monolith "$url" \
        -o "$output_file" \
        --timeout 30
    
    echo -e "${GREEN}✓ Monolith download complete!${NC}"
    echo -e "${YELLOW}📁 Location: $output_file${NC}"
    ls -lh "$output_file" 2>/dev/null || true
}

main() {
    print_header
    
    if [ $# -lt 2 ]; then
        print_usage
        exit 1
    fi
    
    local action=$1
    local url=$2
    local method=${3:-httrack}
    
    if [ "$action" != "download" ]; then
        print_usage
        exit 1
    fi
    
    # Validate URL
    if ! [[ $url =~ ^https?:// ]]; then
        url="https://$url"
    fi
    
    check_tools
    
    echo -e "${BLUE}🎯 Target: ${YELLOW}$url${NC}"
    echo -e "${BLUE}🔧 Method: ${YELLOW}$method${NC}"
    echo ""
    
    case $method in
        httrack)
            download_httrack "$url"
            ;;
        wget)
            download_wget "$url"
            ;;
        monolith)
            download_monolith "$url"
            ;;
        all)
            echo -e "${BLUE}📥 Downloading all 3 methods...${NC}"
            echo ""
            
            echo -e "${BLUE}1️⃣  Method 1: HTTrack${NC}"
            download_httrack "$url" && sleep 2
            echo ""
            
            echo -e "${BLUE}2️⃣  Method 2: WGET${NC}"
            download_wget "$url" && sleep 2
            echo ""
            
            echo -e "${BLUE}3️⃣  Method 3: Monolith${NC}"
            download_monolith "$url"
            
            echo ""
            echo -e "${GREEN}✓ All downloads complete!${NC}"
            echo -e "${YELLOW}📊 Total size:${NC}"
            du -sh "$DOWNLOAD_DIR" 2>/dev/null || true
            ;;
        *)
            echo -e "${RED}❌ Unknown method: $method${NC}"
            print_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ Success!${NC}"
    echo -e "${YELLOW}📁 Downloads directory: $DOWNLOAD_DIR${NC}"
}

main "$@"
