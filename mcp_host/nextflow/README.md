# Nextflow Methylseq MCP Server

🚧 **Development Status: In Active Development** 🚧

A Model Context Protocol (MCP) server that provides tools for running the nf-core/methylseq pipeline both locally and on Seqera Platform.

## Current Capabilities

### ✅ Local Execution
- **Fully functional** local methylseq pipeline execution
- Requires Nextflow installation on the machine
- Supports Singularity/Apptainer containerization
- Automatic samplesheet validation and creation

### ⚠️ Seqera Platform Integration
- **Partially functional** cloud execution via Seqera Platform API
- Can successfully launch jobs on Seqera Platform
- **Known Issue**: Current AWS setup uses free tier account, causing runs to fail due to insufficient compute resources
- API integration and job management features are working as expected

## Features

### Pipeline Execution
- **Local Runs**: Execute methylseq pipeline with full control over parameters
- **Cloud Runs**: Launch jobs on Seqera Platform with AWS Batch compute environments
- **Flexible Profiles**: Support for Docker, Singularity, and Conda profiles
- **Resource Management**: Configurable CPU, memory, and time limits

### Data Management
- **SRA Integration**: Fetch sequencing data directly from SRA using accession IDs
- **Samplesheet Tools**: Create, validate, and convert samplesheets
- **Quality Control**: Built-in FastQC and Bismark QC support
- **MultiQC Reports**: Automatic generation of comprehensive QC reports

### Monitoring & Management
- **Real-time Status**: Monitor pipeline execution status
- **Log Management**: Access and parse Nextflow logs
- **Metrics Tracking**: View workflow metrics and resource usage
- **Error Handling**: Detailed error reporting and troubleshooting

## Prerequisites

### Seqera Platform Execution
- Seqera Platform account
- AWS account with configured compute environment
- API token from Seqera Platform
- Workspace and compute environment IDs


### Available Tools

The server exposes numerous tools through the MCP protocol:

#### System Tools
- `check_system_requirements` - Verify Nextflow and Singularity installation
- `list_singularity_images` - View cached container images
- `get_workspace_info` - Display workspace configuration

#### Samplesheet Tools
- `create_methylseq_samplesheet` - Generate samplesheet from FASTQ files
- `validate_methylseq_samplesheet` - Check samplesheet format and files
- `update_samplesheet_paths` - Modify file paths in samplesheet

#### Pipeline Execution
- `run_methylseq_local` - Execute pipeline locally with Nextflow
- `launch_methylseq_seqera` - Launch pipeline on Seqera Platform
- `fetch_sra_for_methylseq` - Download SRA data and prepare for analysis

#### Monitoring & Management
- `get_workflow_status` - Check pipeline execution status
- `get_workflow_logs` - Retrieve execution logs
- `cancel_workflow` - Stop running workflow
- `list_recent_runs` - View recent pipeline executions

#### Configuration
- `create_methylseq_config` - Generate custom Nextflow configuration
- `create_methylseq_params` - Build parameter file for pipeline
- `list_available_genomes` - Show supported reference genomes


## Known Issues & Limitations

### AWS Free Tier Resource Constraints
The current Seqera Platform integration is configured to use AWS free tier, which has insufficient resources for typical methylseq runs. This causes jobs to fail with resource allocation errors. Solutions:
- Upgrade to a paid AWS tier with adequate compute resources
- Configure smaller test datasets for free tier compatibility
- Use local execution mode for full-scale analyses


**Status**: 🚧 Active Development | **Last Updated**: March 2026
