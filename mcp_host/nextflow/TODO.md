Made 2 changes in deploy.py

**deploy.py**
- [ ] **Updated Project Name:** Changed project_name = f"toolomics_{self.instance_id}"  ----->>>>   project_name = f"toolomics_{self.instance_id}_{service_name}"
  - This creates each container like this:toolomics_ea796447_nextflow-app, toolomics_ea796447_shell-app
- [ ] **Expose Workspace Path:** added the line: env['HOST_WORKSPACE_PATH'] = str(Path(workspace_path).resolve())


methylseq pipeline is causing the MCP client to time out but it fails to reconnect and gets stuck in "GET stream disconnected, reconnecting in 1000ms..."
**shared.py / Bug Fixes** Maybe?
- [ ] **Fix Mimosa Disconnects:** Update the `return_as_dict` decorator to be async-aware. 
  - *Fix:* Change wrapper to `async def` and use `await func(...)` to handle async MCP tools correctly.
