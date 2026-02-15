

2- deploy.py scriptinde değişiklik yaptın 


        project_name = f"toolomics_{self.instance_id}"        ----->>>>         project_name = f"toolomics_{self.instance_id}_{service_name}"

Bunu branch olarak açtıktan sonra Martin'le konuş.


---
3- deploy.py'de ikinci değişiklik:
HOST_WORKSPACE_PATH with the absolute path (line 195)




---
4- Mimosa'da bi sıkıntı olabilir. methylseq uzun sürdüğü için disconnect oluyo ama geri connect olmuyo, bu şekilde kalıyo:

▶ Executing tool: run_methylation_pipeline...
⏳ Please wait...
2026-02-14 23:32:45 [    INFO] mcp.client.streamable_http:181 - _maybe_extract_session_id_from_response() - Received session ID: af7c7b50b88b427fa7ad36dfed1180df
2026-02-14 23:32:45 [    INFO] mcp.client.streamable_http:193 - _maybe_extract_protocol_version_from_message() - Negotiated protocol version: 2025-11-25
2026-02-14 23:37:45 [    INFO] mcp.client.streamable_http:298 - handle_get_stream() - GET stream disconnected, reconnecting in 1000ms...


Bunun sebebi şu olabilir:

🚨 CRITICAL BUG FOUND!
Your return_as_dict decorator is NOT async-aware, but all your MCP tools are async def functions!
The Problem:
python# Current decorator (synchronous)
def return_as_dict(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)  # ❌ Doesn't await!
        # ...
python# Your tools (asynchronous)
@mcp.tool
@return_as_dict  # ❌ This won't work properly!
async def create_methylseq_samplesheet(...):
    # async code
What's Happening:
When you call an async function without await, it returns a coroutine object instead of the actual result. The decorator then tries to process this coroutine object as if it were the result, which will cause bugs.

✅ FIXED VERSION:
Replace your return_as_dict in shared.py with this:
pythondef return_as_dict(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):  # ← Make it async
        result = await func(*args, **kwargs)  # ← Add await
        
        # Convert to dict
        if isinstance(result, CommandResult):
            result_dict = asdict(result)
        elif hasattr(result, "__dataclass_fields__"):
            result_dict = asdict(result)
        else:
            return result
        
        # Truncate stdout and stderr if present to avoid context saturation
        max_length = 16192
        if 'stdout' in result_dict:
            result_dict['stdout'] = result_dict['stdout'][:max_length]
        if 'stderr' in result_dict:
            result_dict['stderr'] = result_dict['stderr'][:max_length]
            
        return result_dict
    
    return wrapper
