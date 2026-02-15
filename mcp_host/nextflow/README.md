# Nextflow MCP Server

⚠️ **STATUS: Under Development** - Only the first two tools have been tested (`create_methylseq_samplesheet` and `run_local_methylation_pipeline`)

## Overview

The Nextflow MCP Server is a Model Context Protocol (MCP) server that provides a suite of tools for managing and executing the nf-core/methylseq pipeline both locally and on the Seqera Platform. It simplifies DNA methylation analysis workflows through an MCP interface, enabling easy integration with AI assistants and other MCP clients.

## Key Features

- **Local Pipeline Execution**: Run nf-core/methylseq directly on your machine with full parameter control
- **Seqera Platform Integration**: Launch and monitor workflows on Seqera Platform's cloud infrastructure
- **Samplesheet Generation**: Automatically create valid samplesheets from FASTQ files
- **Cloud Storage Support**: Upload files to AWS S3 and Google Cloud Storage
- **Pipeline Monitoring**: Track workflow progress, retrieve metrics, and manage runs
- **Workflow Management**: Execute raw Nextflow commands, manage cache, and handle Singularity containers
- **Results Analysis**: Parse MultiQC reports and summarize pipeline output

## Available Tools

### Samplesheet & Local Execution

1. **create_methylseq_samplesheet** ✅ *Tested*
   - Automatically generate samplesheet CSV files from FASTQ files
   - Supports glob patterns and explicit file lists
   - Configurable sample naming and paired-end detection

2. **run_local_methylation_pipeline** ✅ *Tested*
   - Execute nf-core/methylseq locally with extensive parameter control
   - Support for different aligners (bismark, bwameth, etc.)
   - Configure library types, trimming, M-bias correction, and output options

### Seqera Platform Tools

3. **list_seqera_workspaces**
   - List all accessible Seqera workspaces
   - View workspace details and organization information

4. **list_seqera_compute_envs**
   - List compute environments in a Seqera workspace
   - View environment configuration and status

5. **run_methylseq_on_seqera**
   - Launch nf-core/methylseq on Seqera Platform
   - Auto-upload local samplesheets to S3
   - Configure all pipeline parameters for cloud execution
   - Resume capability for interrupted workflows

6. **get_seqera_workflow_status**
   - Monitor running workflow progress
   - View start/completion times and exit status

7. **get_seqera_workflow_metrics**
   - Retrieve resource usage metrics for completed workflows
   - CPU, memory, and timing statistics

8. **cancel_seqera_workflow**
   - Cancel running workflows on Seqera Platform

### Cloud Storage & Data Management

9. **upload_file_to_s3**
   - Upload local files to AWS S3 buckets
   - Automatic bucket/path parsing

10. **upload_file_to_gcs**
    - Upload files to Google Cloud Storage
    - Optional public sharing

### Pipeline Utilities

11. **execute_nextflow_command**
    - Execute arbitrary Nextflow commands safely
    - Log output to workspace logs directory

12. **pull_nfcore_pipeline**
    - Pull or update nf-core pipelines
    - Specify pipeline revision

13. **get_pipeline_info**
    - Retrieve detailed pipeline information

14. **list_workspace_files**
    - Browse workspace directory structure

15. **list_nextflow_runs**
    - View recent pipeline execution history
    - Get run names, timestamps, and status

16. **get_run_details**
    - Fetch detailed metrics for specific runs
    - CPU, memory, and duration statistics

17. **clean_nextflow_cache**
    - Clean Nextflow work and cache directories
    - Optional date filtering

18. **check_running_processes**
    - Check for active Nextflow processes

19. **create_nextflow_config**
    - Generate custom Nextflow configuration files
    - Set resource limits and container profiles

### Results Analysis

20. **parse_multiqc_report**
    - Parse MultiQC general statistics
    - Extract sample-level metrics

21. **summarize_pipeline_results**
    - Scan results directory for key output files
    - Get directory structure and total output size

22. **list_singularity_images**
    - List cached Singularity/Apptainer container images
    - View image sizes and paths

## Installation

### Requirements
- Python 3.9+
- Nextflow
- Singularity or Apptainer (for containerized execution)
- Docker (for local containerized runs)

### Dependencies
```bash
pip install -r requirements.txt
```

Key packages:
- `fastmcp>=1.0.0` - MCP server framework
- `requests>=2.31.0` - HTTP requests
- `aiohttp>=3.9.0` - Async HTTP

### Optional Dependencies
- `boto3` - For S3 uploads and auto-upload functionality
- `google-cloud-storage` - For Google Cloud Storage uploads

## Docker Deployment

### Build
```bash
docker build -t nextflow-mcp-server:latest .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

## Configuration

The server looks for environment variables:
- `WORKSPACE_PATH` - Workspace directory (default: `/app/workspace`)
- Seqera Platform credentials for cloud execution

## Usage Examples

### 1. Generate a Samplesheet
```python
result = create_methylseq_samplesheet(
    pattern="data/*.fastq.gz",
    output_csv="samplesheet.csv",
    paired_end=True
)
```

### 2. Run Pipeline Locally
```python
result = run_local_methylation_pipeline(
    samplesheet="samplesheet.csv",
    genome="GRCh38",
    aligner="bismark",
    outdir="results/methylseq"
)
```

### 3. Run on Seqera Platform
```python
result = run_methylseq_on_seqera(
    samplesheet_path="samplesheet.csv",
    workspace_id=12345,
    compute_env_id="compute-env-abc",
    work_dir="s3://my-bucket/work",
    auto_upload=True
)
```

## Logging

All pipeline executions are logged to:
- Workspace logs directory: `{WORKSPACE_PATH}/logs/`
- Server logs: stdout/stderr (when running in console mode)

## Known Issues & Limitations

- ⚠️ Only the first two tools have been fully tested
- Long-running pipelines may experience connection timeouts (see TODO.md)
- Seqera Platform functionality requires valid API credentials
- S3/GCS uploads require appropriate cloud credentials and SDK installation

## Project Structure

```
nextflow/
├── server.py                 # Main MCP server implementation
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── README.md                # This file
├── TODO.md                  # Development notes and known issues
├── config/                  # Configuration and old implementations
├── old_stuff/               # Previous versions and documentation
└── pipelines/
    └── methylseq/           # nf-core/methylseq pipeline
```

## Development Notes

See `TODO.md` for:
- Known bugs and fixes (e.g., async decorator issue)
- Planned improvements
- Integration notes with Mimosa AI

## License

Inherited from parent projects (Toolomics/Mimosa)

## Contributing

This is an internal development tool. Contact the maintainer for contributions.
