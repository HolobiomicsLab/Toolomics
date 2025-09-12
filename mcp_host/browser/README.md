# Browser MCP Server

A Model Context Protocol (MCP) server that provides web browsing, search, and navigation tools using a headless browser and SearxNG search engine.

## Features

- **Web Search**: Search the web using SearxNG search engine
- **Browser Navigation**: Navigate to web pages and extract content
- **Link Extraction**: Get all clickable links from current page
- **Download Support**: Download files from URLs
- **Screenshot Capture**: Take screenshots of web pages

## Dependencies

This MCP server automatically manages **SearxNG** for web search functionality.

### Automatic SearxNG Management

When the browser MCP server starts, it will:
- Automatically check if SearxNG is already running
- Start SearxNG and Redis services if needed using docker-compose
- Stop SearxNG services when the MCP server shuts down

The services include:
- SearxNG search engine on port 8080
- Redis cache for SearxNG

No manual intervention is required - everything is handled automatically.

## Usage

The server provides the following tools:

- `search(query)` - Search the web using SearxNG
- `navigate(url)` - Navigate to a URL and get page content
- `get_links()` - Get all clickable links from current page
- `get_downloadable_links()` - Get downloadable resource links
- `download_file(url)` - Download a file from URL
- `take_screenshot()` - Capture screenshot of current page

## Troubleshooting

### Search not working
If you get connection errors when searching:
1. Check if Docker is running
2. Verify SearxNG started properly by checking the MCP server logs
3. Test manually: `curl http://localhost:8080/`

### Browser initialization failed
The browser requires a display environment. In headless environments, ensure proper display setup.

### SearxNG fails to start
If SearxNG fails to start automatically:
1. Ensure Docker and docker-compose are installed
2. Check if port 8080 is available
3. Verify the searxng directory exists in the browser MCP directory

## Configuration

- SearxNG runs on port 8080 by default
- Browser operations have a 30-second timeout
- Screenshots are saved to `/workspace/.screenshots/` directory