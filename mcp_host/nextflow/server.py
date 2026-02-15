#!/usr/bin/env python3
"""
Nextflow MCP Server - Simplified
Provides tools for running nf-core/methylseq pipeline locally and on Seqera Platform
"""

import glob
import os
import re
import sys
import json
import logging
import subprocess
import csv
import shlex
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from fastmcp import FastMCP
from shared import return_as_dict


# ============================================================================
# CONFIGURATION
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_PATH", "/app/workspace"))
PIPELINES_DIR = Path("/app/pipelines_default")
CONFIGS_DIR = WORKSPACE_DIR / "configs"
LOGS_DIR = WORKSPACE_DIR / "logs"

# Ensure directories exist
for directory in [WORKSPACE_DIR, CONFIGS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP("nextflow-methylseq")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_relative_path(path: Path) -> str:
    """Convert absolute path to relative path from workspace."""
    try:
        return str(path.relative_to(WORKSPACE_DIR))
    except ValueError:
        return str(path)

def validate_path_exists(path: Path, description: str) -> Dict[str, Any]:
    """Validate that a path exists, return error dict if not."""
    if not path.exists():
        return {"status": "error", "error": f"{description} not found: {path}"}
    return {"status": "ok"}

def generate_timestamp() -> str:
    """Generate timestamp for unique file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def run_subprocess(cmd: List[str], timeout: int = 30, cwd: Optional[Path] = None) -> Dict[str, Any]:
    """Run subprocess with consistent error handling."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            cwd=str(cwd) if cwd else None
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_nextflow_installed() -> Dict[str, Any]:
    """Verify Nextflow is installed and get version."""
    result = run_subprocess(["nextflow", "-version"], timeout=10)
    if result["success"]:
        return {"status": "ok", "version": result["stdout"]}
    return {"status": "error", "error": result.get("error", "Nextflow not found")}

def check_singularity_installed() -> Dict[str, Any]:
    """Verify Singularity/Apptainer is installed."""
    for cmd in ["singularity", "apptainer"]:
        result = run_subprocess([cmd, "--version"], timeout=10)
        if result["success"]:
            return {"status": "ok", "command": cmd, "version": result["stdout"]}
    return {"status": "error", "error": "Neither Singularity nor Apptainer found"}
# ============================================================================
# SEQERA CLIENT
# ============================================================================

class SeqeraClient:
    """Client for interacting with Seqera Platform API."""
    
    def __init__(self, api_token: Optional[str] = None, api_url: Optional[str] = None):
        self.api_token = api_token or os.environ.get("TOWER_ACCESS_TOKEN")
        self.api_url = api_url or os.environ.get("TOWER_API_ENDPOINT", "https://api.cloud.seqera.io")
        
        if not self.api_token:
            raise ValueError("Seqera API token required. Set TOWER_ACCESS_TOKEN or pass api_token parameter")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling."""
        url = f"{self.api_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json() if response.status_code != 204 else {"status": "success"}
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Seqera API error: HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """List all accessible workspaces."""
        return self._request("GET", "/user-info").get("user", {}).get("workspaces", [])
    
    def get_compute_envs(self, workspace_id: int) -> List[Dict[str, Any]]:
        """List compute environments in a workspace."""
        return self._request("GET", f"/compute-envs?workspaceId={workspace_id}").get("computeEnvs", [])
    
    def launch_pipeline(self, workspace_id: int, compute_env_id: str, pipeline: str, 
                       params: Dict[str, Any], work_dir: str, **kwargs) -> Dict[str, Any]:
        """Launch a pipeline run on Seqera Platform."""
        payload = {
            "launch": {
                "computeEnvId": compute_env_id,
                "pipeline": pipeline,
                "workDir": work_dir,
                "params": params,
                **{k: v for k, v in kwargs.items() if v is not None}
            }
        }
        return self._request("POST", f"/workflow/launch?workspaceId={workspace_id}", json=payload)
    
    def get_workflow_status(self, workflow_id: str, workspace_id: int) -> Dict[str, Any]:
        """Get status of a workflow run."""
        return self._request("GET", f"/workflow/{workflow_id}?workspaceId={workspace_id}").get("workflow", {})
    
    def get_workflow_metrics(self, workflow_id: str, workspace_id: int) -> Dict[str, Any]:
        """Get metrics for a workflow run."""
        return self._request("GET", f"/workflow/{workflow_id}/metrics?workspaceId={workspace_id}").get("metrics", {})
    
    def cancel_workflow(self, workflow_id: str, workspace_id: int) -> Dict[str, Any]:
        """Cancel a running workflow."""
        return self._request("DELETE", f"/workflow/{workflow_id}?workspaceId={workspace_id}")



# ============================================================================
# TOOLS - LOCAL EXECUTION
# ============================================================================

@mcp.tool
@return_as_dict
async def create_methylseq_samplesheet(
    pattern: Union[str, List[str]] = "*.fastq.gz",
    output_csv: str = "samplesheet.csv",
    sample_naming: str = "auto",
    paired_end: bool = True
) -> Dict[str, Any]:
    """
    Create a samplesheet CSV for nf-core/methylseq from FASTQ files.
    
    Args:
        pattern: 
            The file search pattern or list of specific files to include.
            - String: A glob pattern like "*.fastq.gz" (searches current directory) or "data/*.fq" (searches 'data' folder).
            - List: A specific list of file paths (e.g., ["data/sample1_R1.fastq.gz", "data/sample1_R2.fastq.gz"]).
        
        output_csv: 
            The name of the CSV file to create. 
            Defaults to "samplesheet.csv".
        
        sample_naming: 
            Determines how the 'sample' column in the CSV is automatically generated.
            - "auto" (Default): Smartly cleans the filename. It removes extensions (.fastq.gz) and common suffixes (_R1, _1, _val_1) to find the core sample name.
              (e.g., "Sample_A_R1_001.fastq.gz" -> "Sample_A")
            - "filename": Uses the exact filename but removes extensions. Does NOT strip _R1/_R2 suffixes. Useful if your filenames are very simple.
              (e.g., "Sample_A.fastq.gz" -> "Sample_A")
            - "directory": Uses the name of the folder containing the file. Useful if each sample is stored in its own folder.
              (e.g., "data/Sample_A/read1.fastq.gz" -> "Sample_A")
        
        paired_end: 
            Controls whether the pipeline treats files as paired-end (R1 & R2) or single-end.
            - True (Default): Looks for matching R1 and R2 pairs. Creates three columns: [sample, fastq_1, fastq_2].
            - False: Treats every file as an independent single-end read. Creates two columns: [sample, fastq_1].
    """
    
    try:
        # --- 1. File Discovery ---
        if isinstance(pattern, list):
            logger.info(f"🔍 Using {len(pattern)} explicit file paths")
            fastq_files = []
            missing_files = []
            for file_path in pattern:
                abs_path = file_path if file_path.startswith('/') else str(WORKSPACE_DIR / file_path)
                if not Path(abs_path).exists():
                    logger.warning(f"⚠️  File not found: {abs_path}")
                    missing_files.append(file_path)
                else:
                    fastq_files.append(abs_path)
            
            if not fastq_files:
                return {"status": "error", "error": "None of the provided files were found", "missing_files": missing_files}
            fastq_files = sorted(fastq_files)
            
        else:
            search_pattern = pattern if pattern.startswith('/') else str(WORKSPACE_DIR / pattern)
            logger.info(f"🔍 Searching for FASTQ files: {search_pattern}")
            fastq_files = sorted(glob.glob(search_pattern))
            
            if not fastq_files:
                return {"status": "error", "error": f"No FASTQ files found matching pattern: {pattern}"}

        logger.info(f"✅ Found {len(fastq_files)} FASTQ files")
        
        # --- 2. Grouping Logic ---
        samples = {}
        r1_regex = re.compile(r'[._-]([rR]?1)(?:[._-]|$)')
        r2_regex = re.compile(r'[._-]([rR]?2)(?:[._-]|$)')

        for fq_path in fastq_files:
            fq_file = Path(fq_path)
            
            # Sample Name Extraction
            if sample_naming == "filename":
                sample_name = fq_file.stem
                for suffix in ['.fastq', '.fq', '.gz']:
                    sample_name = sample_name.replace(suffix, '')
            elif sample_naming == "directory":
                sample_name = fq_file.parent.name
            else:  # auto
                name_clean = fq_file.stem
                for suffix in ['.fastq', '.fq', '.gz']:
                    name_clean = name_clean.replace(suffix, '')
                
                # Only strip R1/R2 markers if we are actively pairing
                if paired_end:
                    name_clean = r1_regex.sub('', name_clean)
                    name_clean = r2_regex.sub('', name_clean)
                sample_name = name_clean.strip('._-')

            sample_name = sample_name.replace(' ', '_')

            # R1/R2 Detection
            match_r2 = r2_regex.search(fq_file.name)
            
            if sample_name not in samples:
                samples[sample_name] = {'r1': [], 'r2': []}

            # Distribute files based on paired_end flag
            if paired_end and match_r2:
                samples[sample_name]['r2'].append(str(fq_file))
            else:
                # If single-end mode OR if it's R1, put in R1
                samples[sample_name]['r1'].append(str(fq_file))

        # --- 3. Write Samplesheet ---
        samplesheet_path = Path(output_csv)
        if not samplesheet_path.is_absolute():
            samplesheet_path = WORKSPACE_DIR / output_csv
        
        samplesheet_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(samplesheet_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header adaptation based on Paired End setting
            if paired_end:
                writer.writerow(['sample', 'fastq_1', 'fastq_2'])
            else:
                writer.writerow(['sample', 'fastq_1'])
            
            for sample_name, reads in sorted(samples.items()):
                r1_files = sorted(reads['r1'])
                r2_files = sorted(reads['r2'])
                
                # Validation warning
                if paired_end and not r2_files and r1_files:
                     logger.warning(f"⚠️ Sample {sample_name}: R1 found but missing R2 (will be written with empty R2 column)")

                # Logic to handle multiple lanes (max_files ensures we capture everything)
                max_files = max(len(r1_files), len(r2_files)) if paired_end else len(r1_files)
                
                for i in range(max_files):
                    r1 = r1_files[i] if i < len(r1_files) else ''
                    
                    if paired_end:
                        r2 = r2_files[i] if i < len(r2_files) else ''
                        writer.writerow([sample_name, r1, r2])
                    else:
                        writer.writerow([sample_name, r1])
                        
        logger.info(f"📝 Generated samplesheet: {samplesheet_path}")

        # --- 4. Summary Stats ---
        sample_summary = {}
        for sample_name, reads in samples.items():
            sample_summary[sample_name] = {
                "type": "paired-end" if (paired_end and reads['r2']) else "single-end",
                "files_count": len(reads['r1']) + len(reads['r2'])
            }

        return {
            "status": "success",
            "samplesheet": str(samplesheet_path),
            "total_samples": len(samples),
            "samples": sample_summary,
            "paired_end_mode": paired_end
        }

    except Exception as e:
        logger.error(f"Error creating samplesheet: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def run_local_methylation_pipeline(
    samplesheet: str,
    genome: Optional[str] = None,
    fasta: Optional[str] = None,
    aligner: str = "bismark",
    outdir: str = "results/methylseq",
    # --- Library & Protocol Specifics ---
    non_directional: bool = False,  # Critical: Run alignment against all 4 strands
    library_type: Optional[str] = None,  # Options: "rrbs", "pbat", "em_seq", "single_cell", "accel", "zymo"
    # --- Trimming / Clipping (Adapter Removal) ---
    clip_r1: int = 0,
    clip_r2: int = 0,
    three_prime_clip_r1: int = 0,
    three_prime_clip_r2: int = 0,
    # --- M-Bias Correction (Methylation Calling) ---
    # Critical: Ignore methylation in first/last N bases (often artifacts)
    ignore_r1: int = 0,
    ignore_r2: int = 2,  # Pipeline default is 2
    ignore_3prime_r1: int = 0,
    ignore_3prime_r2: int = 2, # Pipeline default is 2
    # --- Standard Options ---
    max_memory: Optional[str] = "14.GB",
    max_cpus: Optional[int] = 14,
    skip_trimming: bool = False,
    skip_deduplication: bool = False,
    save_trimmed: bool = False,
    save_reference: bool = False,
    save_align_intermeds: bool = False, # Useful for debugging alignment issues
    cytosine_report: bool = True,
    comprehensive: bool = False,
    min_depth: int = 0,
    resume: bool = True
) -> Dict[str, Any]:
    """
    Run the nf-core/methylseq pipeline using Singularity containers.
    
    Args:
        samplesheet: Path to samplesheet CSV
        genome: Reference genome (e.g., "GRCh38")
        fasta: Custom FASTA file path
        aligner: Aligner to use ("bismark", "bwameth", "gem")
        outdir: Output directory
        non_directional: Run alignment against all 4 strands
        library_type: Library prep type ("rrbs", "pbat", "em_seq", etc.)
        clip_r1/clip_r2: Bases to clip from 5' end
        three_prime_clip_r1/r2: Bases to clip from 3' end
        ignore_r1/r2: Ignore methylation in first N bases
        ignore_3prime_r1/r2: Ignore methylation in last N bases
        max_memory/max_cpus: Resource limits
        skip_trimming/skip_deduplication: Skip processing steps
        save_trimmed/save_reference/save_align_intermeds: Save intermediate files
        cytosine_report: Generate cytosine report
        comprehensive: Generate comprehensive reports
        min_depth: Minimum coverage depth
        resume: Enable resume (-resume flag)
    """
    try:
        # ===== VALIDATION PHASE =====
        logger.info("=" * 80)
        logger.info("METHYLATION PIPELINE EXECUTION")
        logger.info("=" * 80)
        
        # Check prerequisites
        nf_check = check_nextflow_installed()
        if nf_check["status"] == "error":
            return nf_check
        
        sg_check = check_singularity_installed()
        if sg_check["status"] == "error":
            return sg_check
        
        # Resolve and validate samplesheet
        samplesheet_path = WORKSPACE_DIR / samplesheet
        validation = validate_path_exists(samplesheet_path, "Samplesheet")
        if validation["status"] == "error":
            return validation
        
        logger.info(f"✓ Samplesheet: {samplesheet_path}")
        
        # Validate genome/fasta
        if not genome and not fasta:
            return {
                "status": "error",
                "error": "Must provide either 'genome' or 'fasta' parameter"
            }
        
        if fasta:
            fasta_path = WORKSPACE_DIR / fasta
            validation = validate_path_exists(fasta_path, "FASTA file")
            if validation["status"] == "error":
                return validation
            logger.info(f"✓ Custom FASTA: {fasta_path}")
        else:
            logger.info(f"✓ Reference genome: {genome}")
        
        # ===== CONFIGURATION PHASE =====
        timestamp = generate_timestamp()
        run_config_dir = CONFIGS_DIR / f"run_{timestamp}"
        run_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Build parameters for params.json
        params = {
            "input": str(samplesheet_path),
            "outdir": str(WORKSPACE_DIR / outdir),
            "aligner": aligner,
            "non_directional": non_directional,
            "clip_r1": clip_r1,
            "clip_r2": clip_r2,
            "three_prime_clip_r1": three_prime_clip_r1,
            "three_prime_clip_r2": three_prime_clip_r2,
            "ignore_r1": ignore_r1,
            "ignore_r2": ignore_r2,
            "ignore_3prime_r1": ignore_3prime_r1,
            "ignore_3prime_r2": ignore_3prime_r2,
            "skip_trimming": skip_trimming,
            "skip_deduplication": skip_deduplication,
            "save_trimmed": save_trimmed,
            "save_reference": save_reference,
            "save_align_intermeds": save_align_intermeds,
            "cytosine_report": cytosine_report,
            "comprehensive": comprehensive,
            "min_depth": min_depth
        }
        
        # Add optional parameters
        if library_type:
            params["library_type"] = library_type
        
        if fasta:
            params["fasta"] = str(fasta_path)
            params["igenomes_ignore"] = True
        else:
            params["genome"] = genome
        
        # Write parameters file
        params_file = run_config_dir / "params.json"
        with open(params_file, 'w') as f:
            json.dump(params, f, indent=2)
        
        logger.info(f"✓ Parameters file: {params_file}")
        

### TODO: added this only to test on local computer 
        # Create Nextflow config with proper resource limits
        nextflow_config = run_config_dir / "nextflow.config"
        
        config_content = f"""
// Local variables for resource limits (not added to params)
workflow.containerEngine = 'singularity'

// Nextflow 24.04+ resourceLimits directive
// This enforces absolute maximum resources at the process level
process {{
    resourceLimits = [
        memory: '{max_memory}',
        cpus: {max_cpus},
        time: '24.h'
    ]
    
    // Override process labels with fixed resource limits
    withLabel: 'process_low' {{
        cpus   = {{ 2 }}
        memory = {{ 12.GB }}
        time   = {{ 4.h }}
    }}
    withLabel: 'process_medium' {{
        cpus   = {{ 6 }}
        memory = {{ {max_memory} }}
        time   = {{ 8.h }}
    }}
    withLabel: 'process_high' {{
        cpus   = {{ {max_cpus} }}
        memory = {{ {max_memory} }}
        time   = {{ 16.h }}
    }}
    withLabel: 'process_long' {{
        time   = {{ 20.h }}
    }}
}}
"""
        
        with open(nextflow_config, 'w') as f:
            f.write(config_content)
        
        logger.info(f"✓ Nextflow config: {nextflow_config}")
        
        # ===== EXECUTION PHASE =====
        pipeline_path = PIPELINES_DIR / "methylseq" / "main.nf"
        if not pipeline_path.exists():
            return {
                "status": "error",
                "error": f"Pipeline not found: {pipeline_path}",
                "expected_location": str(pipeline_path)
            }
        
        work_dir = WORKSPACE_DIR / "work" / "methylseq"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "nextflow",
            "run",
            str(pipeline_path),
            "-params-file", str(params_file),
            "-c", str(nextflow_config),
            "-profile", "singularity",
            "-w", str(work_dir)
        ]
        
        if resume:
            cmd.append("-resume")
        
        logger.info("=" * 80)
        logger.info("LAUNCHING NEXTFLOW")
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info("=" * 80)
        
        log_file = LOGS_DIR / f"methylseq_{timestamp}.log"
        
        with open(log_file, 'w') as log_fh:
            log_fh.write(f"Nextflow methylseq pipeline execution\n")
            log_fh.write(f"Started: {datetime.now().isoformat()}\n")
            log_fh.write(f"Command: {' '.join(cmd)}\n")
            log_fh.write("=" * 80 + "\n\n")
            log_fh.flush()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(WORKSPACE_DIR)
            )
            
            for line in process.stdout:
                log_fh.write(line)
                log_fh.flush()
                if any(x in line for x in ["ERROR", "WARN", "Completed", "Failed"]):
                    logger.info(line.rstrip())
            
            return_code = process.wait()
            
            log_fh.write("\n" + "=" * 80 + "\n")
            log_fh.write(f"Finished: {datetime.now().isoformat()}\n")
            log_fh.write(f"Exit code: {return_code}\n")
        
        output_dir = WORKSPACE_DIR / outdir
        
        if return_code == 0:
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            return {
                "status": "success",
                "message": "Pipeline completed successfully",
                "output_directory": get_relative_path(output_dir),
                "log_file": get_relative_path(log_file),
                "config_directory": get_relative_path(run_config_dir),
                "exit_code": return_code,
                "timestamp": timestamp
            }
        else:
            logger.error("PIPELINE FAILED")
            return {
                "status": "failed",
                "message": f"Pipeline failed with exit code {return_code}",
                "log_file": get_relative_path(log_file),
                "config_directory": get_relative_path(run_config_dir),
                "exit_code": return_code,
                "timestamp": timestamp,
                "hint": "Check the log file for detailed error messages"
            }
    
    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# TOOLS - SEQERA PLATFORM
# ============================================================================

@mcp.tool
@return_as_dict
async def list_seqera_workspaces(
    api_token: Optional[str] = None,
    api_url: Optional[str] = None
) -> Dict[str, Any]:
    """List all accessible Seqera Platform workspaces."""
    try:
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        workspaces = client.get_workspaces()
        
        workspace_list = [
            {
                "id": ws.get("workspaceId"),
                "name": ws.get("workspaceName"),
                "org_name": ws.get("orgName"),
                "full_name": f"{ws.get('orgName')}/{ws.get('workspaceName')}" if ws.get("orgName") else ws.get("workspaceName")
            }
            for ws in workspaces
        ]
        
        return {"status": "success", "workspace_count": len(workspace_list), "workspaces": workspace_list}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def list_seqera_compute_envs(
    workspace_id: int,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None
) -> Dict[str, Any]:
    """List compute environments in a Seqera workspace."""
    try:
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        compute_envs = client.get_compute_envs(workspace_id)
        
        env_list = [
            {
                "id": env.get("id"),
                "name": env.get("name"),
                "platform": env.get("platform"),
                "status": env.get("status"),
                "primary": env.get("primary", False)
            }
            for env in compute_envs
        ]
        
        return {"status": "success", "workspace_id": workspace_id, "compute_env_count": len(env_list), "compute_envs": env_list}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def upload_file_to_s3(
    local_path: str,
    s3_path: str,
    make_public: bool = False
) -> Dict[str, Any]:
    """
    Upload a local file to S3.
    
    Args:
        local_path: Path to local file
        s3_path: Destination S3 path (e.g., "s3://my-bucket/path/file.csv")
        make_public: Make file publicly readable (default: False)
    
    Requires: pip install boto3 and AWS credentials configured
    """
    try:
        import boto3
        from urllib.parse import urlparse
        
        local_file = WORKSPACE_DIR / local_path if not Path(local_path).is_absolute() else Path(local_path)
        if not local_file.exists():
            return {"status": "error", "error": f"Local file not found: {local_path}"}
        
        if not s3_path.startswith("s3://"):
            return {"status": "error", "error": "s3_path must start with s3://"}
        
        parsed = urlparse(s3_path)
        bucket, key = parsed.netloc, parsed.path.lstrip('/')
        
        if not bucket or not key:
            return {"status": "error", "error": "Invalid S3 path format"}
        
        s3_client = boto3.client('s3')
        extra_args = {'ACL': 'public-read'} if make_public else None
        s3_client.upload_file(str(local_file), bucket, key, ExtraArgs=extra_args)
        
        return {
            "status": "success",
            "local_path": str(local_file),
            "s3_path": s3_path,
            "file_size_mb": round(local_file.stat().st_size / (1024 * 1024), 2),
            "public": make_public
        }
    except ImportError:
        return {"status": "error", "error": "boto3 not installed", "solution": "Run: pip install boto3"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def upload_file_to_gcs(
    local_path: str,
    gcs_path: str,
    make_public: bool = False
) -> Dict[str, Any]:
    """
    Upload a local file to Google Cloud Storage.
    
    Args:
        local_path: Path to local file
        gcs_path: Destination GCS path (e.g., "gs://my-bucket/path/file.csv")
        make_public: Make file publicly readable (default: False)
    
    Requires: pip install google-cloud-storage and GCP credentials configured
    """
    try:
        from google.cloud import storage
        from urllib.parse import urlparse
        
        local_file = WORKSPACE_DIR / local_path if not Path(local_path).is_absolute() else Path(local_path)
        if not local_file.exists():
            return {"status": "error", "error": f"Local file not found: {local_path}"}
        
        if not gcs_path.startswith("gs://"):
            return {"status": "error", "error": "gcs_path must start with gs://"}
        
        parsed = urlparse(gcs_path)
        bucket_name, blob_name = parsed.netloc, parsed.path.lstrip('/')
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(local_file))
        
        if make_public:
            blob.make_public()
        
        return {
            "status": "success",
            "local_path": str(local_file),
            "gcs_path": gcs_path,
            "file_size_mb": round(local_file.stat().st_size / (1024 * 1024), 2),
            "public": make_public
        }
    except ImportError:
        return {"status": "error", "error": "google-cloud-storage not installed", "solution": "Run: pip install google-cloud-storage"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def run_methylseq_on_seqera(
    samplesheet_path: str,
    workspace_id: int,
    compute_env_id: str,
    work_dir: str,
    auto_upload: bool = False,
    genome: Optional[str] = None,
    fasta: Optional[str] = None,
    aligner: str = "bismark",
    outdir: str = "results/methylseq",
    non_directional: bool = False,
    library_type: Optional[str] = None,
    clip_r1: int = 0,
    clip_r2: int = 0,
    three_prime_clip_r1: int = 0,
    three_prime_clip_r2: int = 0,
    skip_trimming: bool = False,
    save_trimmed: bool = False,
    ignore_r1: int = 0,
    ignore_r2: int = 2,
    ignore_3prime_r1: int = 0,
    ignore_3prime_r2: int = 2,
    skip_deduplication: bool = False,
    save_reference: bool = False,
    save_align_intermeds: bool = False,
    cytosine_report: bool = True,
    comprehensive: bool = False,
    min_depth: int = 0,
    pipeline_revision: str = "2.6.0",
    config_profiles: Optional[List[str]] = None,
    run_name: Optional[str] = None,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None,
    resume: bool = True
) -> Dict[str, Any]:
    """
    Launch nf-core/methylseq pipeline on Seqera Platform.
    
    Args:
        samplesheet_path: Path to samplesheet (cloud path or local with auto_upload=True)
        workspace_id: Seqera workspace ID
        compute_env_id: Compute environment ID
        work_dir: Work directory (e.g., "s3://my-bucket/work")
        auto_upload: If True and samplesheet is local, auto-upload to S3 (requires boto3)
        [additional args same as run_local_methylation_pipeline]
    """
    try:
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        
        # Handle local samplesheet upload if needed
        is_cloud_path = any(samplesheet_path.startswith(p) for p in ["s3://", "gs://", "az://", "http://", "https://"])
        final_samplesheet_path = samplesheet_path
        
        if not is_cloud_path:
            local_path = WORKSPACE_DIR / samplesheet_path if not Path(samplesheet_path).is_absolute() else Path(samplesheet_path)
            if not local_path.exists():
                return {"status": "error", "error": f"Local samplesheet not found: {samplesheet_path}"}
            
            if auto_upload:
                try:
                    import boto3
                    from urllib.parse import urlparse
                    
                    if not work_dir.startswith("s3://"):
                        return {"status": "error", "error": "auto_upload only supports S3. work_dir must start with s3://"}
                    
                    parsed = urlparse(work_dir)
                    bucket = parsed.netloc
                    prefix = parsed.path.lstrip('/')
                    upload_key = f"{prefix}/samplesheets/{local_path.name}" if prefix else f"samplesheets/{local_path.name}"
                    upload_url = f"s3://{bucket}/{upload_key}"
                    
                    s3_client = boto3.client('s3')
                    s3_client.upload_file(str(local_path), bucket, upload_key)
                    final_samplesheet_path = upload_url
                    logger.info(f"✅ Samplesheet uploaded to {upload_url}")
                except ImportError:
                    return {"status": "error", "error": "auto_upload requires boto3", "solution": "Run: pip install boto3"}
                except Exception as e:
                    return {"status": "error", "error": f"Failed to upload samplesheet: {str(e)}"}
            else:
                return {
                    "status": "error",
                    "error": "Samplesheet is local but auto_upload=False",
                    "solution": "Either set auto_upload=True or manually upload and provide cloud URL"
                }
        
        # Build parameters
        params = {
            "input": final_samplesheet_path,
            "outdir": outdir,
            "aligner": aligner,
            "genome": genome,
            "non_directional": non_directional,
            "clip_r1": clip_r1,
            "clip_r2": clip_r2,
            "three_prime_clip_r1": three_prime_clip_r1,
            "three_prime_clip_r2": three_prime_clip_r2,
            "ignore_r1": ignore_r1,
            "ignore_r2": ignore_r2,
            "ignore_3prime_r1": ignore_3prime_r1,
            "ignore_3prime_r2": ignore_3prime_r2,
            "skip_trimming": skip_trimming,
            "skip_deduplication": skip_deduplication,
            "save_trimmed": save_trimmed,
            "save_reference": save_reference,
            "save_align_intermeds": save_align_intermeds,
            "cytosine_report": cytosine_report,
            "comprehensive": comprehensive,
            "min_depth": min_depth,
            "library_type": library_type
        }
        
        if fasta:
            params["fasta"] = fasta
            params["igenomes_ignore"] = True
        
        params = {k: v for k, v in params.items() if v is not None and v is not False}
        
        if resume:
            params["resume"] = True
        
        run_name = run_name or f"methylseq_{generate_timestamp()}"
        config_profiles = config_profiles or ["docker"]
        
        # Launch
        response = client.launch_pipeline(
            workspace_id=workspace_id,
            compute_env_id=compute_env_id,
            pipeline="nf-core/methylseq",
            params=params,
            work_dir=work_dir,
            revision=pipeline_revision,
            configProfiles=config_profiles,
            runName=run_name
        )
        
        workflow_id = response.get("workflowId")
        
        return {
            "status": "success",
            "message": "Pipeline launched on Seqera Platform",
            "workflow_id": workflow_id,
            "run_name": run_name,
            "workspace_id": workspace_id,
            "monitor_url": f"https://cloud.seqera.io/watch/{workflow_id}"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def get_seqera_workflow_status(
    workflow_id: str,
    workspace_id: int,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None
) -> Dict[str, Any]:
    """Get the current status of a Seqera Platform workflow."""
    try:
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        workflow = client.get_workflow_status(workflow_id, workspace_id)
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "run_name": workflow.get("runName"),
            "workflow_status": workflow.get("status"),
            "progress": workflow.get("progress", 0),
            "start_time": workflow.get("start"),
            "complete_time": workflow.get("complete"),
            "duration": workflow.get("duration"),
            "exit_status": workflow.get("exitStatus"),
            "error_message": workflow.get("errorMessage")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def get_seqera_workflow_metrics(
    workflow_id: str,
    workspace_id: int,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None
) -> Dict[str, Any]:
    """Get resource usage metrics for a Seqera workflow."""
    try:
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        metrics = client.get_workflow_metrics(workflow_id, workspace_id)
        return {"status": "success", "workflow_id": workflow_id, "metrics": metrics}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def cancel_seqera_workflow(
    workflow_id: str,
    workspace_id: int,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None
) -> Dict[str, Any]:
    """Cancel a running Seqera Platform workflow."""
    try:
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        client.cancel_workflow(workflow_id, workspace_id)
        return {"status": "success", "message": f"Workflow {workflow_id} cancelled", "workflow_id": workflow_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============================================================================
# TOOLS - UTILITY
# ============================================================================

@mcp.tool
@return_as_dict
async def execute_nextflow_command(
    command: str,
    working_directory: str = ".",
    log_prefix: str = "nextflow_custom",
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute a raw Nextflow command safely.
    
    Args:
        command: Nextflow command args (e.g. "run hello -resume"). Do NOT include "nextflow" prefix.
        working_directory: Relative path for execution context
        log_prefix: Prefix for log filename
        timeout: Max execution time in seconds
    """
    try:
        work_dir = WORKSPACE_DIR / working_directory
        if not work_dir.exists():
            return {"status": "error", "error": f"Working directory not found: {work_dir}"}
        
        cmd_args = shlex.split(command)
        full_cmd = ["nextflow"] + cmd_args
        
        timestamp = generate_timestamp()
        log_file = LOGS_DIR / f"{log_prefix}_{timestamp}.log"
        
        logger.info(f"⚡ Executing: nextflow {command}")
        
        with open(log_file, 'w') as log_fh:
            log_fh.write(f"Nextflow command execution\n")
            log_fh.write(f"Started: {datetime.now().isoformat()}\n")
            log_fh.write(f"Command: nextflow {command}\n")
            log_fh.write("=" * 80 + "\n\n")
            log_fh.flush()
            
            try:
                process = subprocess.run(
                    full_cmd,
                    cwd=str(work_dir),
                    stdout=log_fh,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=timeout
                )
                return_code = process.returncode
                status = "success" if return_code == 0 else "failed"
            except subprocess.TimeoutExpired:
                log_fh.write(f"\n\nTIMEOUT: Command exceeded {timeout} seconds\n")
                return_code = "TIMEOUT"
                status = "timeout"
            
            log_fh.write(f"\nFinished: {datetime.now().isoformat()}\n")
            log_fh.write(f"Exit code: {return_code}\n")
        
        # Read tail of log
        with open(log_file, 'r') as f:
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(max(file_size - 4000, 0))
            output_preview = f.read()
            if file_size > 4000:
                output_preview = "[...truncated...]\n" + output_preview.partition('\n')[2]
        
        return {
            "status": status,
            "log_file": get_relative_path(log_file),
            "exit_code": return_code,
            "output": output_preview
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def pull_nfcore_pipeline(pipeline_name: str, revision: str = "latest") -> Dict[str, Any]:
    """Pull/update an nf-core pipeline."""
    cmd = ["nextflow", "pull", f"nf-core/{pipeline_name}"]
    if revision != "latest":
        cmd.extend(["-r", revision])
    
    result = run_subprocess(cmd, timeout=300, cwd=WORKSPACE_DIR)
    return {
        "status": "success" if result["success"] else "failed",
        "pipeline": f"nf-core/{pipeline_name}",
        "revision": revision,
        "output": result.get("stdout", ""),
        "exit_code": result.get("returncode", -1)
    }

@mcp.tool
@return_as_dict
async def get_pipeline_info(pipeline: str) -> Dict[str, Any]:
    """Get detailed information about a Nextflow pipeline."""
    result = run_subprocess(["nextflow", "info", pipeline], timeout=30)
    return {
        "status": "success" if result["success"] else "failed",
        "pipeline": pipeline,
        "info": result.get("stdout", ""),
        "exit_code": result.get("returncode", -1)
    }

@mcp.tool()
async def list_workspace_files(directory: str = ".") -> Dict[str, Any]:
    """List files in the workspace directory."""
    try:
        target_dir = WORKSPACE_DIR / directory
        if not target_dir.exists():
            return {"status": "error", "error": f"Directory not found: {directory}"}
        
        files = []
        directories = []
        for item in sorted(target_dir.rglob("*")):
            rel_path = get_relative_path(item)
            if item.is_file():
                files.append({
                    "path": rel_path,
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            elif item.is_dir():
                directories.append(rel_path)
        
        return {
            "status": "success",
            "directory": directory,
            "file_count": len(files),
            "directory_count": len(directories),
            "files": files[:100],
            "directories": directories[:50]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def check_pipeline_status() -> Dict[str, Any]:
    """Check the status of the Nextflow environment and pipelines."""
    try:
        pipelines = []
        if PIPELINES_DIR.exists():
            for pipeline_dir in PIPELINES_DIR.iterdir():
                if pipeline_dir.is_dir() and (pipeline_dir / "main.nf").exists():
                    pipelines.append(pipeline_dir.name)
        
        return {
            "status": "success",
            "workspace": str(WORKSPACE_DIR),
            "nextflow": check_nextflow_installed(),
            "singularity": check_singularity_installed(),
            "available_pipelines": pipelines
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def list_nextflow_runs(limit: int = 10) -> Dict[str, Any]:
    """List recent Nextflow pipeline runs."""
    result = run_subprocess(["nextflow", "log", "-q"], timeout=30, cwd=WORKSPACE_DIR)
    if not result["success"]:
        return {"status": "failed", "error": result.get("stderr", "")}
    
    runs = []
    for line in result["stdout"].strip().split('\n')[:limit]:
        if line:
            parts = line.split('\t')
            if len(parts) >= 4:
                runs.append({
                    "timestamp": parts[0],
                    "session_id": parts[1],
                    "run_name": parts[2],
                    "status": parts[3]
                })
    
    return {"status": "success", "run_count": len(runs), "runs": runs}

@mcp.tool
@return_as_dict
async def get_run_details(
    run_name: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed information about a specific pipeline run."""
    cmd = ["nextflow", "log"]
    if run_name:
        cmd.append(run_name)
    elif session_id:
        cmd.extend(["-s", session_id])
    else:
        cmd.append("last")
    
    cmd.extend(["-f", "name,status,exit,duration,realtime,%cpu,%mem"])
    
    result = run_subprocess(cmd, timeout=30, cwd=WORKSPACE_DIR)
    return {
        "status": "success" if result["success"] else "failed",
        "details": result.get("stdout", ""),
        "exit_code": result.get("returncode", -1)
    }

@mcp.tool
@return_as_dict
async def clean_nextflow_cache(before_date: Optional[str] = None) -> Dict[str, Any]:
    """Clean Nextflow work and cache directories."""
    cmd = ["nextflow", "clean", "-f"]
    if before_date:
        cmd.extend(["-before", before_date])
    
    result = run_subprocess(cmd, timeout=30, cwd=WORKSPACE_DIR)
    return {
        "status": "success" if result["success"] else "failed",
        "details": result.get("stdout", ""),
        "exit_code": result.get("returncode", -1)
    }

@mcp.tool
@return_as_dict
async def check_running_processes() -> Dict[str, Any]:
    """Check if any Nextflow processes are currently running."""
    result = run_subprocess(["pgrep", "-f", "nextflow"])
    pids = [int(pid) for pid in result.get("stdout", "").strip().split('\n') if pid]
    
    return {
        "status": "success",
        "running": len(pids) > 0,
        "process_count": len(pids),
        "pids": pids
    }

@mcp.tool
@return_as_dict
async def create_nextflow_config(
    profile: str = "singularity",
    max_cpus: int = 16,
    max_memory: str = "128.GB",
    max_time: str = "240.h",
    output_file: str = "custom.config"
) -> Dict[str, Any]:
    """Create a custom Nextflow configuration file."""
    try:
        config_path = CONFIGS_DIR / output_file
        
        config_content = f"""// Custom Nextflow Configuration
// Generated: {datetime.now().isoformat()}

params {{
    max_cpus = {max_cpus}
    max_memory = '{max_memory}'
    max_time = '{max_time}'
}}

process {{
    executor = 'local'
    containerOptions = '--cleanenv'
    
    resourceLimits = [
        cpus: {max_cpus},
        memory: '{max_memory}',
        time: '{max_time}'
    ]
}}

profiles {{
    {profile} {{
        {profile}.enabled = true
        {profile}.autoMounts = true
    }}
}}
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return {
            "status": "success",
            "config_file": get_relative_path(config_path),
            "profile": profile,
            "resources": {"max_cpus": max_cpus, "max_memory": max_memory, "max_time": max_time}
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def parse_multiqc_report(
    report_path: str = "results/multiqc/multiqc_data/multiqc_general_stats.txt"
) -> Dict[str, Any]:
    """Parse MultiQC general statistics file."""
    try:
        full_path = WORKSPACE_DIR / report_path
        if not full_path.exists():
            return {"status": "error", "error": f"MultiQC report not found: {report_path}"}
        
        stats = []
        with open(full_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                stats.append(row)
        
        return {
            "status": "success",
            "report_path": report_path,
            "sample_count": len(stats),
            "statistics": stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def summarize_pipeline_results(results_dir: str = "results") -> Dict[str, Any]:
    """Summarize pipeline output directory structure and key files."""
    try:
        results_path = WORKSPACE_DIR / results_dir
        if not results_path.exists():
            return {"status": "error", "error": f"Results directory not found: {results_dir}"}
        
        key_files = {
            "multiqc_report": list(results_path.rglob("multiqc_report.html")),
            "logs": list(results_path.rglob("*.log")),
            "bam_files": list(results_path.rglob("*.bam")),
            "fastq_files": list(results_path.rglob("*.fastq.gz"))
        }
        
        return {
            "status": "success",
            "results_directory": results_dir,
            "total_size_gb": round(sum(f.stat().st_size for f in results_path.rglob('*') if f.is_file()) / (1024**3), 2),
            "key_files": {k: [get_relative_path(f) for f in v] for k, v in key_files.items()},
            "subdirectories": [get_relative_path(d) for d in results_path.iterdir() if d.is_dir()]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def list_singularity_images(cache_dir: Optional[str] = None) -> Dict[str, Any]:
    """List Singularity/Apptainer container images in cache."""
    try:
        if cache_dir is None:
            cache_dir = os.environ.get("NXF_SINGULARITY_CACHEDIR", str(Path.home() / ".singularity" / "cache"))
        
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            return {"status": "success", "images": [], "cache_dir": str(cache_path)}
        
        images = []
        for img_file in cache_path.rglob("*.img"):
            images.append({
                "name": img_file.name,
                "size_gb": round(img_file.stat().st_size / (1024**3), 2),
                "path": str(img_file)
            })
        
        return {
            "status": "success",
            "cache_dir": str(cache_path),
            "image_count": len(images),
            "images": images,
            "total_size_gb": round(sum(img["size_gb"] for img in images), 2)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool
@return_as_dict
async def fetch_sra_for_methylseq(
    accession_ids: str,
    output_dir: str = "fetchngs_output",
    download_method: str = "ftp"
) -> Dict[str, Any]:
    """
    Download SRA data using nf-core/fetchngs and format for methylseq pipeline.
    
    Args:
        accession_ids: Comma-separated SRA accession IDs (e.g., "SRR11605097, ERR4007730, DRR171822")
        output_dir: Output directory name (default: "fetchngs_output")
        download_method: Download method - "ftp", "sratools", or "aspera" (default: "ftp")
    """
    try:
        # Parse comma-separated string into list
        accession_ids = [id.strip() for id in accession_ids.split(',') if id.strip()]
        
        # Validate IDs
        valid_prefixes = ['SRR', 'ERR', 'DRR', 'SRX', 'ERX', 'DRX', 'GSM', 'GSE', 
                         'SRS', 'ERS', 'DRS', 'SAMN', 'SAMEA', 'SAMD', 'SRP', 
                         'ERP', 'DRP', 'SRA', 'ERA', 'DRA', 'PRJNA', 'PRJEB', 'PRJDB']
        
        for acc_id in accession_ids:
            if not any(acc_id.startswith(prefix) for prefix in valid_prefixes):
                return {"status": "error", "error": f"Invalid accession ID: {acc_id}"}
        
        # Check if Nextflow is installed
        nf_check = check_nextflow_installed()
        if nf_check["status"] != "ok":
            return {"status": "error", "error": "Nextflow not installed"}
        
        # Create input CSV file
        timestamp = generate_timestamp()
        input_csv = WORKSPACE_DIR / f"sra_ids_{timestamp}.csv"
        with open(input_csv, 'w') as f:
            for acc_id in accession_ids:
                f.write(f"{acc_id}\n")
        
        # Check if fetchngs pipeline exists, if not pull it
        fetchngs_dir = PIPELINES_DIR / "fetchngs"
        if not fetchngs_dir.exists():
            logger.info("Pulling nf-core/fetchngs pipeline...")
            pull_result = run_subprocess(
                ["nextflow", "pull", "nf-core/fetchngs"],
                timeout=180,
                cwd=WORKSPACE_DIR
            )
            if not pull_result["success"]:
                return {
                    "status": "error",
                    "error": f"Failed to pull fetchngs pipeline: {pull_result.get('stderr', 'Unknown error')}"
                }
        
        # Prepare output directory
        output_path = WORKSPACE_DIR / output_dir
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Run fetchngs pipeline
        logger.info(f"Running fetchngs for {len(accession_ids)} accession(s)...")
        cmd = [
            "nextflow", "run", "nf-core/fetchngs",
            "-profile", "singularity",
            "--input", str(input_csv),
            "--outdir", str(output_path),
            "--download_method", download_method
        ]
        
        fetchngs_result = run_subprocess(cmd, timeout=3600, cwd=WORKSPACE_DIR)
        
        if not fetchngs_result["success"]:
            return {
                "status": "error",
                "error": f"Fetchngs pipeline failed: {fetchngs_result.get('stderr', 'Unknown error')}",
                "stdout": fetchngs_result.get("stdout", "")
            }
        
        # Look for the generated samplesheet
        samplesheet_path = output_path / "samplesheet" / "samplesheet.csv"
        if not samplesheet_path.exists():
            # Try alternative location
            alt_paths = list(output_path.rglob("samplesheet.csv"))
            if alt_paths:
                samplesheet_path = alt_paths[0]
            else:
                return {
                    "status": "error",
                    "error": "Samplesheet not found in fetchngs output",
                    "output_dir": get_relative_path(output_path)
                }
        
        # Convert fetchngs samplesheet to methylseq format
        methylseq_sheet = output_path / f"methylseq_samplesheet_{timestamp}.csv"
        
        with open(samplesheet_path, 'r') as infile, open(methylseq_sheet, 'w', newline='') as outfile:
            reader = csv.DictReader(infile)
            writer = csv.writer(outfile)
            
            # Write methylseq header
            writer.writerow(['sample', 'fastq_1', 'fastq_2'])
            
            for row in reader:
                sample = row.get('sample', row.get('run_accession', 'unknown'))
                fastq_1 = row.get('fastq_1', '')
                fastq_2 = row.get('fastq_2', '')
                
                # Only write if we have at least fastq_1
                if fastq_1:
                    writer.writerow([sample, fastq_1, fastq_2 if fastq_2 else ''])
        
        return {
            "status": "success",
            "message": f"Successfully fetched {len(accession_ids)} SRA accession(s)",
            "accession_ids": accession_ids,
            "download_method": download_method,
            "output_directory": get_relative_path(output_path),
            "fetchngs_samplesheet": get_relative_path(samplesheet_path),
            "methylseq_samplesheet": get_relative_path(methylseq_sheet),
            "next_step": f"Use methylseq_samplesheet for running nf-core/methylseq pipeline"
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}




# ============================================================================
# END OF TOOLS - SERVER STARTUP
# ============================================================================


if __name__ == "__main__":
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
    elif "FASTMCP_PORT" in os.environ:
        port = int(os.environ["FASTMCP_PORT"])
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        logger.error("No port specified")
        sys.exit(1)
    
    logger.info(f"Starting Nextflow Methylseq MCP Server on port {port}")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
