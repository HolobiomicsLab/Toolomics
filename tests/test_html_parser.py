#!/usr/bin/env python3

"""
Test script for HTML Code Extraction functionality

This script tests the HTML parsing logic with sample HTML content
to ensure it works correctly before deploying the MCP server.
"""

from html_parser import HTMLCodeExtractor

def test_html_parser():
    """Test the HTML parser with sample content."""
    
    # Sample HTML content similar to notebook exports
    sample_html = """
    <html>
    <head><title>Test Notebook</title></head>
    <body>
    <h4 class="date">2024-12-05</h4>
    
    <p>Data importation</p>
    <pre class="r"><code>sample_info = read.csv("sample_information.csv")</code></pre>
    
    <pre class="r"><code>estcounts=read.csv("estcounts_final.csv")
rownames(estcounts)=estcounts$X
colnames(estcounts)</code></pre>
    
    <p>Some Python code:</p>
    <pre class="python"><code>import pandas as pd
df = pd.read_csv("data.csv")
print(df.head())</code></pre>
    
    <p>SQL query:</p>
    <pre><code>SELECT * FROM users WHERE age > 25;</code></pre>
    
    </body>
    </html>
    """
    
    print("Testing HTML Code Extractor...")
    print("=" * 50)
    
    extractor = HTMLCodeExtractor()
    
    # Test 1: Extract all code blocks
    print("\n1. Extracting all code blocks:")
    all_blocks = extractor.extract_code_blocks(sample_html)
    for i, block in enumerate(all_blocks):
        print(f"Block {i+1} ({block['language']}):")
        print(f"  Code: {block['code'][:50]}...")
        print()
    
    # Test 2: Extract only R code
    print("\n2. Extracting only R code blocks:")
    r_blocks = extractor.extract_code_blocks(sample_html, language='r')
    for i, block in enumerate(r_blocks):
        print(f"R Block {i+1}:")
        print(f"  Code: {block['code']}")
        print()
    
    # Test 3: Combine code blocks
    print("\n3. Combining all code blocks:")
    combined = extractor.combine_code_blocks(all_blocks)
    print("Combined code:")
    print(combined)
    print()
    
    # Test 4: Get summary
    print("\n4. Code summary:")
    summary = extractor.get_code_summary(all_blocks)
    print(f"Total blocks: {summary['total_blocks']}")
    print(f"Languages: {summary['languages']}")
    print(f"Total lines: {summary['total_lines']}")
    print(f"Total characters: {summary['total_characters']}")
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")

if __name__ == "__main__":
    test_html_parser()
