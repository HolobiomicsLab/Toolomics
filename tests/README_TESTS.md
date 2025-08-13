# MCP Server Test Suite

Comprehensive test suite for all MCP servers in the Toolomics infrastructure. This test suite provides **MCP discovery**, **tools discovery**, **use case testing**, and **server health assertions** for each MCP server.

## 🧪 Available Tests

### Toolomics Custom Servers
- **`toolomics_rscript_test.py`** - R Script execution MCP server
- **`toolomics_browser_test.py`** - Web browsing and automation MCP server  
- **`toolomics_csv_test.py`** - CSV data processing MCP server
- **`toolomics_pdf_test.py`** - PDF processing and navigation MCP server
- **`toolomics_shell_test.py`** - Shell command execution MCP server

### ToolHive Registry Servers
- **`fetch_server_test.py`** - Web content fetching (gofetch)
- **`git_server_test.py`** - Git repository operations
- **`filesystem_server_test.py`** - File system operations
- **`time_server_test.py`** - Time and timezone operations

### Master Test Runner
- **`run_all_mcp_tests.py`** - Runs all tests with comprehensive reporting

## 🚀 Quick Start

### Prerequisites

1. **Start MCP servers**:
   ```bash
   ./start.sh
   ```

2. **Verify servers are running**:
   ```bash
   thv list
   ```

3. **Install test dependencies** (if not already installed):
   ```bash
   # Using UV (recommended)
   uv pip install -r requirements.txt
   
   # Using pip
   pip install -r requirements.txt
   ```

### Running Tests

#### Run All Tests
```bash
# Sequential execution (recommended)
python tests/run_all_mcp_tests.py

# Parallel execution (faster, may cause conflicts)
python tests/run_all_mcp_tests.py --parallel
```

#### Run Individual Server Tests
```bash
# Run specific server test
python tests/run_all_mcp_tests.py --server csv
python tests/run_all_mcp_tests.py --server browser
python tests/run_all_mcp_tests.py --server rscript

# Run individual test file directly
python tests/toolomics_csv_test.py
python tests/toolomics_browser_test.py
```

#### Available Server Names
- `rscript`, `r` - R Script MCP
- `browser` - Browser MCP  
- `csv` - CSV MCP
- `pdf` - PDF MCP
- `shell`, `bash` - Shell MCP
- `fetch` - Fetch MCP
- `git` - Git MCP
- `filesystem`, `fs` - Filesystem MCP
- `time` - Time MCP

## 📊 Test Structure

Each test follows the same comprehensive structure:

### 1. **MCP Discovery** 🔍
- Tests ToolManager-based discovery (via Mimosa-AI integration)
- Falls back to direct port scanning discovery
- Verifies server is accessible and responsive

### 2. **Tools Discovery** 🔧
- Lists all available tools from the MCP server
- Validates expected tools are present
- Reports tool descriptions and capabilities

### 3. **Use Case Testing** 🎯
- Tests realistic usage scenarios for each server
- Covers core functionality with practical examples
- Validates input/output formats and error handling

### 4. **Health Assertions** 💓
- Verifies server is running correctly
- Tests basic connectivity and response times
- Confirms server identity and tool availability

## 🎯 Test Examples

### CSV MCP Test Coverage
- Create datasets with multiple data types
- Add, update, delete rows
- Query data with conditions
- Generate statistics
- List datasets and pagination
- Error handling for invalid operations

### Browser MCP Test Coverage  
- Web search via SearxNG integration
- Navigate to web pages
- Extract page links and downloadable content
- Take screenshots
- Download files
- Handle different content types and errors

### R Script MCP Test Coverage
- Execute R code snippets
- Write and execute R script files
- List workspace and script files
- Statistical analysis examples
- Error handling for invalid R syntax

### PDF MCP Test Coverage
- Initialize PDF navigation sessions
- Navigate between pages (next/previous/specific)
- Add bookmarks and search within documents
- Extract text from specific page ranges
- Semantic search with RAG functionality
- Keyword search with context

### Shell MCP Test Coverage
- Execute basic shell commands (echo, ls, pwd)
- System information commands (uname, ps, df)
- File operations (create, read, modify)
- Security filtering for dangerous commands
- Error handling and timeouts

## 🛠️ Configuration

### Mimosa-AI Integration
Tests integrate with Mimosa-AI's `ToolManager` class for MCP discovery:

```python
from sources.core.tools_manager import ToolManager, MCP
from config import Config
```

If Mimosa-AI is not available, tests gracefully fall back to direct discovery.

### Test Timeouts
- **Discovery timeout**: 3-5 seconds per port
- **Tool operations**: 10-30 seconds depending on complexity
- **Network operations**: 30 seconds for web requests
- **File operations**: 15 seconds for I/O operations

## 📋 Test Output

### Success Output
```
🧪 Starting CSV MCP Server Tests
============================================================
✅ Discovered 6 MCP servers via ToolManager
✅ Found CSV MCP: CSV Processing MCP

📋 Testing tools discovery...
✅ Found 9 tools:
  - create_csv: Create a new CSV dataset
  - get_csv_info: Get information about a CSV dataset
  - get_csv_data: Retrieve data from a CSV dataset
  [... more tools ...]
✅ All expected CSV tools found

🧪 Testing CSV use cases...
📝 Test 1: Create CSV dataset
✅ CSV creation result: Dataset 'test_employees' created successfully
[... more tests ...]

🎉 All CSV MCP tests PASSED!
```

### Failure Output  
```
❌ Failed to discover CSV MCP server
   Make sure the server is running with: ./start.sh

❌ Some CSV MCP tests FAILED!
   Details: Discovery failed | Tools discovery failed
```

### Master Test Summary
```
📊 FINAL TEST SUMMARY
================================================================================
⏱️  Total execution time: 45.2 seconds
🧪 Total tests run: 9
✅ Tests passed: 7
❌ Tests failed: 2
📈 Success rate: 77.8%

📋 Detailed Results:
Server               Status     Duration   Details
--------------------------------------------------------------------------------
R Script MCP         ✅ PASS    5.2s       ✅ Discovery | ✅ Tools | ✅ Use cases
CSV MCP              ✅ PASS    3.1s       ✅ Discovery | ✅ Tools | ✅ Use cases  
Browser MCP          ❌ FAIL    12.3s      ❌ Discovery failed
[... more results ...]
```

## 🐛 Troubleshooting

### Common Issues

#### MCP Discovery Failed
```bash
# Check if servers are running
thv list

# Check server logs
thv logs toolomics-csv

# Restart servers
./start.sh --rebuild
```

#### Tool Discovery Failed
- Server is running but not responding to tool requests
- Check server logs for errors
- Verify correct port and transport configuration

#### Use Case Tests Failed
- **Network issues**: Check internet connectivity for browser/fetch tests
- **Missing dependencies**: Install R, PDF libraries, etc.
- **Permission issues**: Check file system permissions
- **Resource conflicts**: Don't run tests in parallel if experiencing issues

#### Specific Server Issues

**R Script MCP**:
```bash
# Check if xcmsrocker container is running
docker ps | grep xcmsrocker

# Check R installation
docker exec xcmsrocker R --version
```

**Browser MCP**:
```bash
# Check SearxNG is running
curl http://localhost:8080/

# Check browser dependencies
docker ps | grep selenium
```

**PDF MCP**:
```bash  
# Install PDF dependencies
pip install PyPDF2 PyMuPDF sentence-transformers scikit-learn
```

### Debug Mode

Run individual tests with detailed error output:
```bash
python -u tests/toolomics_csv_test.py 2>&1 | tee csv_test.log
```

### Test Development

To add new tests:

1. **Create test file**: `new_server_test.py`
2. **Follow the template** from existing tests
3. **Implement the 4 test phases**: Discovery, Tools, Use Cases, Health
4. **Add to master runner**: Update `run_all_mcp_tests.py`
5. **Test thoroughly**: Run individual and master tests

## 📁 File Structure

```
tests/
├── README_TESTS.md                 # This documentation
├── run_all_mcp_tests.py           # Master test runner
├── toolomics_rscript_test.py       # R Script MCP tests
├── toolomics_browser_test.py       # Browser MCP tests  
├── toolomics_csv_test.py           # CSV MCP tests
├── toolomics_pdf_test.py           # PDF MCP tests
├── toolomics_shell_test.py         # Shell MCP tests
├── fetch_server_test.py            # Fetch MCP tests
├── git_server_test.py              # Git MCP tests
├── filesystem_server_test.py       # Filesystem MCP tests
├── time_server_test.py             # Time MCP tests
│
# Legacy tests (still functional)  
├── R_test.py                       # Original R MCP test
├── csv_test.py                     # Original CSV MCP test
├── shell_test.py                   # Original Shell MCP test
├── workspace_test.py               # Workspace functionality test
├── test_url_normalization.py       # URL normalization test
└── test-network-integration.sh     # Network integration test
```

## 🎉 Success Criteria

A fully passing test suite indicates:

- ✅ All MCP servers are discoverable and responsive
- ✅ All expected tools are available and functional  
- ✅ Core functionality works with realistic use cases
- ✅ Error handling is robust and informative
- ✅ Integration between Toolomics and Mimosa-AI is working
- ✅ ToolHive registry servers are accessible and functional

This comprehensive test suite ensures your MCP infrastructure is ready for production use with AI agents and workflow systems.