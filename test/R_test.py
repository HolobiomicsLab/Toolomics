#!/usr/bin/env python3

"""
Test client for Shell MCP Server
Demonstrates all functionality with realistic test scenarios.
"""

import asyncio
import json
from fastmcp import Client

async def test_r():
    """Test all Shell operations comprehensively."""
    
    port = 5103
    # Connect to the MCP server
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to Rscript MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Test 1
        print("=" * 50)
        print("TEST 1: calling simple code execution tool")
        print("=" * 50)

        r_code = '''library(mzR)
library(CAMERA)

# Use the direct path that worked with mzR
path <- 'storage/QC_0.mzML'  # or use full path: '/full/path/to/storage/QC_0.mzML'

# Verify file exists
if(!file.exists(path)) stop("File not found at: ", normalizePath(path))

# Read with xcms
xs <- xcmsSet(path, method="centWave", ppm=30, peakwidth=c(5,10))

print("xcmsSet completed successfully")'''

        # Test 2
        print("=" * 50)
        print("TEST 2: write find adduct csv")
        print("=" * 50)

        r_code = '''library(xcms)                                                                                                                                                                         
library(CAMERA)                                                                                                                                                                       
                                                                                                                                                                                    
# Read the mzML file                                                                                                                                                                  
xset <- xcmsSet("storage/QC_0.mzML", method="centWave", ppm=10, peakwidth=c(5,20), snthresh=10)                                                                                       
                                                                                                                                                                                    
# Group peaks                                                                                                                                                                         
xset <- group(xset, bw=5, mzwid=0.015, minfrac=0.5)                                                                                                                                   
                                                                                                                                                                                    
# Perform CAMERA analysis                                                                                                                                                             
an <- xsAnnotate(xset)                                                                                                                                                                
an <- groupFWHM(an, perfwhm=0.6)                                                                                                                                                      
an <- findAdducts(an, polarity="positive")                                                                                                                                            
                                                                                                                                                                                    
# Get and save results                                                                                                                                                                
adducts <- getPeaklist(an)                                                                                                                                                            
write.csv(adducts, file="storage/QC_0_adducts.csv", row.names=FALSE)                                                                                                                  
                                                                                                                                                                                    
# Print summary                                                                                                                                                                       
print(paste("Adduct detection completed. Found", nrow(adducts), "features.")) '''
        
        result = await client.call_tool("execute_r_code", {
            "r_code": r_code,
        })

        print(f"📋 Command output: {result[0].text}")
        


if __name__ == "__main__":
    print("🧪 Starting R MCP server.py Tests")
    asyncio.run(test_r())