# Nextflow MCP Server

**Under Development** - Only the first two tools have been tested (`create_methylseq_samplesheet` and `run_local_methylation_pipeline`)

## Overview

The Nextflow MCP Server is a Model Context Protocol (MCP) server that provides a suite of tools for managing and executing the nf-core/methylseq pipeline both locally and on the Seqera Platform. It simplifies DNA methylation analysis workflows through an MCP interface, enabling easy integration with AI assistants and other MCP clients.

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


## Requirements
- Python 3.9+
- Nextflow
- Singularity or Apptainer (for containerized execution)
- Docker (for local containerized runs)

### Optional Dependencies
- `boto3` - For S3 uploads and auto-upload functionality
- `google-cloud-storage` - For Google Cloud Storage uploads


## Configuration

The server looks for environment variables:
- `WORKSPACE_PATH` - Workspace directory (default: `/app/workspace`)
- Seqera Platform credentials for cloud execution

## Known Issues & Limitations

- ⚠️ Only the first two tools have been fully tested
- Long-running pipelines may experience connection timeouts (see TODO.md)
- Seqera Platform functionality requires valid API credentials
- S3/GCS uploads require appropriate cloud credentials and SDK installation
