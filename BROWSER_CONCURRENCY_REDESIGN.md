# Browser MCP Server Concurrency Redesign

## Overview

The Browser MCP Server has been completely redesigned to support multiple clients querying the same server simultaneously. The original implementation used a single global browser instance with exclusive locking, which meant only one client could use browser functionality at a time.

## Key Changes

### 1. Browser Pool Architecture

**Before:**
- Single global `browser_instance` shared across all requests
- Global `browser_lock` that serialized ALL browser operations
- Only ONE client could use browser functionality at a time
- Other clients received "Browser is busy" errors

**After:**
- `BrowserPool` class manages multiple browser instances
- Each client gets a dedicated browser from the pool
- Configurable pool size (default: 5 browsers)
- Automatic session management and cleanup

### 2. Session Management

**New Features:**
- `BrowserSession` dataclass tracks browser metadata
- Session expiration based on idle time (default: 5 minutes)
- Automatic cleanup of expired/invalid sessions
- Background thread for pool maintenance

### 3. Concurrency Support

**Improvements:**
- Multiple clients can navigate, screenshot, and download simultaneously
- Context manager pattern for safe browser acquisition/release
- Timeout handling for pool exhaustion
- Graceful degradation when browsers are unavailable

### 4. New Monitoring Tool

**Added `get_pool_status` tool:**
```json
{
  "status": "success",
  "pool_stats": {
    "total_sessions": 5,
    "available_browsers": 3,
    "in_use_browsers": 2,
    "pool_size": 5,
    "max_idle_time": 300
  }
}
```

## Configuration

### Environment Variables

The browser pool can be configured using environment variables:

```bash
# Number of browser instances in the pool (default: 5)
export BROWSER_POOL_SIZE=10

# Maximum idle time before session cleanup in seconds (default: 300)
export BROWSER_MAX_IDLE_TIME=600
```

### Docker Configuration

When running via ToolHive, you can set these in the registry.json:

```json
{
  "toolomics-browser": {
    "env_vars": [
      {
        "name": "BROWSER_POOL_SIZE",
        "value": "10"
      },
      {
        "name": "BROWSER_MAX_IDLE_TIME", 
        "value": "600"
      }
    ]
  }
}
```

## Performance Characteristics

### Concurrency Benefits

1. **Multiple Simultaneous Operations**: Up to `BROWSER_POOL_SIZE` clients can operate concurrently
2. **Reduced Latency**: No waiting for other clients to finish
3. **Better Resource Utilization**: Browsers are reused efficiently
4. **Fault Tolerance**: Failed browsers are automatically replaced

### Resource Usage

- **Memory**: Each browser instance uses ~100-200MB RAM
- **CPU**: Distributed load across multiple browser processes
- **Startup Time**: Initial pool creation takes 10-30 seconds
- **Cleanup**: Automatic cleanup prevents resource leaks

## Testing

### Concurrency Test Suite

A comprehensive test suite is provided in `tests/browser_concurrency_test.py`:

```bash
# Run the concurrency tests
python tests/browser_concurrency_test.py
```

**Test Coverage:**
- Basic concurrency (5 clients)
- High concurrency (10 clients)  
- Sequential vs concurrent performance comparison
- Pool status monitoring
- Error handling and timeout scenarios

### Expected Results

With the new architecture, you should see:
- **Success Rate**: >80% for 5 clients, >60% for 10 clients
- **Concurrent Speedup**: 2-4x faster than sequential execution
- **No "Browser is busy" errors** under normal load

## Migration Guide

### For Existing Users

The API remains the same - no changes needed to existing client code:

```python
# These calls work exactly the same as before
navigate("https://example.com")
take_screenshot()
get_links()
download_file("https://example.com/file.pdf")
```

### For High-Load Scenarios

If you expect high concurrent usage:

1. **Increase Pool Size**: Set `BROWSER_POOL_SIZE=15` or higher
2. **Monitor Pool Status**: Use `get_pool_status()` to track utilization
3. **Adjust Timeouts**: Increase client timeouts for pool acquisition
4. **Resource Planning**: Plan for ~150MB RAM per browser instance

## Architecture Details

### BrowserPool Class

```python
class BrowserPool:
    def __init__(self, pool_size: int = 5, max_idle_time: int = 300):
        self.available_browsers = queue.Queue(maxsize=pool_size)
        self.all_sessions = {}  # session_id -> BrowserSession
        self.pool_lock = threading.RLock()
        # ... initialization and cleanup logic
        
    @contextmanager
    def get_browser(self, timeout: int = 30):
        # Safe browser acquisition with timeout
        # Automatic return to pool on completion
```

### Session Lifecycle

1. **Creation**: Browser instances created on server startup
2. **Acquisition**: Client requests browser from pool (with timeout)
3. **Usage**: Client performs browser operations
4. **Release**: Browser returned to pool automatically
5. **Cleanup**: Expired/invalid sessions cleaned up by background thread

### Error Handling

- **Pool Exhaustion**: Returns "Browser pool timeout" error
- **Invalid Sessions**: Automatically recreated
- **Browser Crashes**: Gracefully handled and replaced
- **Network Issues**: Proper timeout and retry logic

## Troubleshooting

### Common Issues

1. **"Browser pool timeout" errors**
   - Increase `BROWSER_POOL_SIZE`
   - Check if browsers are hanging (restart server)
   - Monitor with `get_pool_status()`

2. **High memory usage**
   - Reduce `BROWSER_POOL_SIZE`
   - Decrease `BROWSER_MAX_IDLE_TIME`
   - Monitor system resources

3. **Slow startup**
   - Normal for initial pool creation
   - Consider reducing pool size for faster startup
   - Background initialization in progress

### Monitoring Commands

```bash
# Check pool status via API
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_pool_status"}}'

# Monitor server logs
thv logs toolomics-browser

# Check resource usage
docker stats
```

## Future Enhancements

### Planned Improvements

1. **Dynamic Pool Scaling**: Automatically adjust pool size based on demand
2. **Session Persistence**: Maintain browser state across requests
3. **Load Balancing**: Distribute load across multiple server instances
4. **Metrics Collection**: Detailed performance and usage metrics
5. **Health Checks**: Proactive browser health monitoring

### Configuration Options

Future versions may support:
- Browser-specific configurations (Chrome vs Firefox)
- Per-client resource limits
- Priority queuing for different client types
- Geographic browser distribution

## Conclusion

The redesigned Browser MCP Server now properly supports multiple concurrent clients while maintaining the same simple API. The browser pool architecture provides:

- **Scalability**: Handle multiple clients simultaneously
- **Reliability**: Automatic error recovery and cleanup
- **Performance**: Significant speedup for concurrent workloads
- **Monitoring**: Real-time pool status and statistics

This addresses the original concurrency limitations and makes the server suitable for production multi-client environments.
