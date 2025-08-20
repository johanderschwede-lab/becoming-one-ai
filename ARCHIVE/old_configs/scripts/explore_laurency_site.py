#!/usr/bin/env python3
"""
Laurency Site Explorer
=====================

Explores the frame-based laurency.com site to find PDF links
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def explore_laurency():
    base_url = "https://www.laurency.com"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print("🔍 Exploring laurency.com structure...")
    
    # Start with main page
    response = session.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("📄 Main page structure:")
    print(f"Title: {soup.title.text if soup.title else 'No title'}")
    
    # Find frame sources
    frames = soup.find_all('frame')
    frame_urls = []
    
    for frame in frames:
        src = frame.get('src')
        if src:
            full_url = urllib.parse.urljoin(base_url, src)
            frame_urls.append(full_url)
            print(f"📋 Frame: {frame.get('name', 'unnamed')} -> {src}")
    
    # Explore each frame
    all_links = set()
    pdf_links = set()
    
    for frame_url in frame_urls:
        print(f"\n🔍 Exploring frame: {frame_url}")
        try:
            response = session.get(frame_url)
            frame_soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = frame_soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                full_url = urllib.parse.urljoin(frame_url, href)
                all_links.add(full_url)
                
                if href.lower().endswith('.pdf'):
                    pdf_links.add(full_url)
                    print(f"  📄 PDF: {href} -> {link.get_text(strip=True)}")
            
            # Also look for option values (dropdown menus)
            options = frame_soup.find_all('option', value=True)
            for option in options:
                value = option.get('value')
                if value and not value.startswith('javascript:'):
                    full_url = urllib.parse.urljoin(frame_url, value)
                    all_links.add(full_url)
                    
                    if value.lower().endswith('.pdf'):
                        pdf_links.add(full_url)
                        print(f"  📄 PDF (option): {value} -> {option.get_text(strip=True)}")
        
        except Exception as e:
            print(f"  ❌ Error exploring {frame_url}: {e}")
    
    # Now explore some of the other pages we found
    print(f"\n🔍 Found {len(all_links)} total links, exploring for more PDFs...")
    
    explored_count = 0
    for link in list(all_links)[:20]:  # Limit to first 20 to avoid overwhelming
        if explored_count >= 10:  # Limit exploration
            break
            
        if link.startswith(base_url) and not link.endswith('.pdf'):
            try:
                print(f"🔍 Checking: {link}")
                response = session.get(link, timeout=10)
                page_soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for PDF links on this page
                page_links = page_soup.find_all('a', href=True)
                for page_link in page_links:
                    href = page_link.get('href')
                    if href and href.lower().endswith('.pdf'):
                        full_pdf_url = urllib.parse.urljoin(link, href)
                        if full_pdf_url not in pdf_links:
                            pdf_links.add(full_pdf_url)
                            print(f"  📄 New PDF: {href} -> {page_link.get_text(strip=True)}")
                
                explored_count += 1
                
            except Exception as e:
                print(f"  ❌ Error checking {link}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"Total links found: {len(all_links)}")
    print(f"PDF files found: {len(pdf_links)}")
    
    if pdf_links:
        print(f"\n📄 All PDF links:")
        for pdf_url in sorted(pdf_links):
            print(f"  {pdf_url}")
    else:
        print("\n❌ No PDF files found on laurency.com")
        print("The site might:")
        print("  - Not have PDFs available for download")
        print("  - Have PDFs behind authentication")
        print("  - Use a different file format")
        print("  - Have PDFs on a different domain")
    
    # Check if there are references to other domains
    print(f"\n🔍 Looking for external references...")
    for link in all_links:
        if 'hylozoik' in link.lower() or 'laurency' in link.lower():
            if not link.startswith(base_url):
                print(f"  🌐 External: {link}")

if __name__ == "__main__":
    explore_laurency()
