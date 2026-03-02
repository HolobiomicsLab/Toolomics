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
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import return_as_dict, get_workspace_path


# ============================================================================
# CONFIGURATION
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

WORKSPACE_DIR = get_workspace_path()  

# Load environment variables from .env file
env_file = WORKSPACE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)
    logger.info(f"✓ Loaded environment variables from {env_file}")
else:
    logger.warning(f"⚠️  No .env file found at {env_file}")

# Load Seqera configuration from environment
SEQERA_WORKSPACE_ID = os.environ.get("SEQERA_WORKSPACE_ID")
SEQERA_COMPUTE_ENV_ID = os.environ.get("SEQERA_COMPUTE_ENV_ID")
SEQERA_API_TOKEN = os.environ.get("TOWER_ACCESS_TOKEN")
SEQERA_API_URL = os.environ.get("TOWER_API_ENDPOINT", "https://api.cloud.seqera.io")



if SEQERA_WORKSPACE_ID:
    logger.info(f"✓ Seqera Workspace ID loaded: {SEQERA_WORKSPACE_ID}")
if SEQERA_COMPUTE_ENV_ID:
    logger.info(f"✓ Seqera Compute Env ID loaded: {SEQERA_COMPUTE_ENV_ID}")


CONFIGS_DIR = WORKSPACE_DIR / "configs"
LOGS_DIR = WORKSPACE_DIR / "logs"
PIPELINES_DIR = WORKSPACE_DIR / "pipelines"
NXF_SINGULARITY_CACHEDIR = WORKSPACE_DIR / "singularity_images"

# Only create subdirectories
CONFIGS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

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
    files: Union[str, List[str]],
    s3_path: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    region_name: Optional[str] = None,
    make_public: bool = False
) -> Dict[str, Any]:
    """
    Upload one or more local files to S3.
    
    Args:
        files: 
            Single path (str) or list of paths (List[str]) to local files.
            Example: "data/file.csv" or ["data/file1.csv", "data/file2.csv"]
        
        s3_path: 
            Destination S3 path.
            - If uploading a single file, this can be the full destination key.
            - If uploading multiple files OR if path ends in '/', this acts as the destination directory.
        
        aws_access_key_id: Optional AWS Access Key ID.
        aws_secret_access_key: Optional AWS Secret Access Key.
        aws_session_token: Optional AWS Session Token.
        region_name: Optional AWS Region (e.g., "us-east-1").
        make_public: Make uploaded files publicly readable (default: False).
    """
    try:
        import boto3
        from urllib.parse import urlparse
        
        # 1. Normalize input to list
        if isinstance(files, str):
            file_list = [files]
        else:
            file_list = files


        # NEW: Expand directories into lists of files
        expanded_files = []
        for path_str in file_list:
            local_path = WORKSPACE_DIR / path_str if not Path(path_str).is_absolute() else Path(path_str)
            if local_path.is_dir():
                # Grab all files in the directory and keep paths relative
                expanded_files.extend([str(p.relative_to(WORKSPACE_DIR)) for p in local_path.rglob('*') if p.is_file()])
            else:
                expanded_files.append(path_str)
        
        file_list = expanded_files
        
        if not file_list:
            return {"status": "error", "error": "No files provided"}
        
        # 2. Parse S3 Destination
        if not s3_path.startswith("s3://"):
            return {"status": "error", "error": "s3_path must start with s3://"}
        
        parsed = urlparse(s3_path)
        bucket_name = parsed.netloc
        base_key_prefix = parsed.path.lstrip('/')
        
        if not bucket_name:
            return {"status": "error", "error": "Invalid S3 path: bucket name missing"}

        # 3. Initialize S3 Client with explicit credentials if provided
        session_kwargs = {}
        if aws_access_key_id:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
        if aws_secret_access_key:
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key
        if aws_session_token:
            session_kwargs['aws_session_token'] = aws_session_token
        if region_name:
            session_kwargs['region_name'] = region_name
            
        session = boto3.Session(**session_kwargs)
        s3_client = session.client('s3')
        
        extra_args = {'ACL': 'public-read'} if make_public else None
        
        results = []
        uploaded_count = 0
        total_size_mb = 0.0

        # 4. Iterate and Upload
        for local_path_str in file_list:
            local_file = WORKSPACE_DIR / local_path_str if not Path(local_path_str).is_absolute() else Path(local_path_str)
            
            if not local_file.exists():
                results.append({"file": local_path_str, "status": "failed", "error": "File not found"})
                continue
            
            # Determine S3 Key
            is_directory_upload = (
                len(file_list) > 1 or 
                s3_path.endswith('/') or 
                not base_key_prefix
            )
            
            if is_directory_upload:
                clean_prefix = base_key_prefix.rstrip('/')
                if clean_prefix:
                    key = f"{clean_prefix}/{local_file.name}"
                else:
                    key = local_file.name
            else:
                key = base_key_prefix

            try:
                s3_client.upload_file(str(local_file), bucket_name, key, ExtraArgs=extra_args)
                
                size_mb = local_file.stat().st_size / (1024 * 1024)
                total_size_mb += size_mb
                uploaded_count += 1
                
                results.append({
                    "file": local_path_str,
                    "s3_dest": f"s3://{bucket_name}/{key}",
                    "status": "success",
                    "size_mb": round(size_mb, 2)
                })
                
            except Exception as e:
                # Ensure this line is not broken in your editor
                results.append({"file": local_path_str, "status": "failed", "error": str(e)})

        # 5. Summary
        status = "success" if uploaded_count == len(file_list) else "partial_success" if uploaded_count > 0 else "error"
        
        return {
            "status": status,
            "uploaded_count": uploaded_count,
            "failed_count": len(file_list) - uploaded_count,
            "total_size_mb": round(total_size_mb, 2),
            "destination_bucket": bucket_name,
            "public": make_public,
            "details": results
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
    outdir: str,
    workspace_id: Optional[int] = None,  
    compute_env_id: Optional[str] = None,  
    work_dir: Optional[str] = None,
    auto_upload: bool = False,
    genome: Optional[str] = None,
    fasta: Optional[str] = None,
    aligner: str = "bismark",
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
    igenomes_ignore: bool = False,
    igenomes_base: Optional[str] = None,
    # NEW: Resource limits
    max_memory: Optional[str] = None,
    max_cpus: Optional[int] = None,
    pipeline_revision: str = "2.6.0",
    config_profiles: Optional[List[str]] = None,
    config_text: Optional[str] = None,
    run_name: Optional[str] = None,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None,
    session_id: Optional[str] = None,
    pull_latest: bool = False,
    stub_run: bool = False,
    pre_run_script: Optional[str] = None,
    post_run_script: Optional[str] = None,
    extra_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Launch nf-core/methylseq pipeline on Seqera Platform with robust error handling.
    
    CRITICAL REQUIREMENTS:
    - samplesheet_path: Must be a cloud URL (s3://, gs://, etc.) OR set auto_upload=True
    - outdir: MUST be a cloud storage path (e.g., "s3://my-bucket/results/run1")
    - work_dir: Optional cloud path for intermediate files (defaults to compute env setting)
    
    Args:
        samplesheet_path: Path to samplesheet CSV. Must be cloud URL or local with auto_upload=True
        outdir: OUTPUT directory for results - MUST be cloud storage path (s3://bucket/path)
        workspace_id: Seqera workspace ID (defaults to SEQERA_WORKSPACE_ID env var)
        compute_env_id: Compute environment ID (defaults to SEQERA_COMPUTE_ENV_ID env var)
        work_dir: Work directory for scratch files (optional, uses compute env default if not set)
        auto_upload: Auto-upload local samplesheet to S3 (requires boto3 and S3 work_dir)
        
        genome: Reference genome from iGenomes (e.g., "GRCh38")
        fasta: Custom reference genome FASTA (must be cloud URL for Seqera)
        aligner: Alignment tool - "bismark", "bwameth", or "bismark_hisat" (default: "bismark")
        
        non_directional: Run alignment against all 4 strands (for non-directional libraries)
        library_type: Library prep kit - "rrbs", "pbat", "em_seq", "single_cell", "accel", "zymo"
        
        clip_r1: Bases to clip from 5' end of R1
        clip_r2: Bases to clip from 5' end of R2
        three_prime_clip_r1: Bases to clip from 3' end of R1
        three_prime_clip_r2: Bases to clip from 3' end of R2
        
        skip_trimming: Skip adapter trimming step
        save_trimmed: Save trimmed FastQ files
        
        ignore_r1: Ignore methylation in first N bases of R1
        ignore_r2: Ignore methylation in first N bases of R2 (default: 2)
        ignore_3prime_r1: Ignore methylation in last N bases of R1
        ignore_3prime_r2: Ignore methylation in last N bases of R2 (default: 2)
        
        skip_deduplication: Skip deduplication step
        save_reference: Save reference genome files
        save_align_intermeds: Save intermediate BAM files
        cytosine_report: Generate cytosine methylation report (default: True)
        comprehensive: Generate comprehensive methylation report
        min_depth: Minimum read depth for methylation calling
        
        igenomes_ignore: Ignore iGenomes references
        igenomes_base: Custom iGenomes base path
        
        max_memory: Maximum memory per process (e.g., "128.GB", "64.GB")
        max_cpus: Maximum CPUs per process (e.g., 16, 32)
        
        pipeline_revision: Git tag/branch of nf-core/methylseq (default: "2.6.0")
        config_profiles: Config profiles to apply (default: ["docker"])
        config_text: Custom Nextflow config as text (will be merged with resource limits if provided)
        run_name: Custom run name (auto-generated if not provided)
        
        api_token: Seqera API token (defaults to TOWER_ACCESS_TOKEN env var)
        api_url: Seqera API URL (defaults to TOWER_API_ENDPOINT or cloud.seqera.io)
        
        session_id: Nextflow session ID from a previous run to resume from.
                   Get this from get_seqera_workflow_status() for failed runs.
                   Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        pull_latest: Pull latest pipeline version from repository
        stub_run: Run in stub mode for testing (processes return dummy results)
        pre_run_script: Script to run before pipeline execution
        post_run_script: Script to run after pipeline completion
        extra_params: Additional pipeline parameters as dict
    
    IMPORTANT NOTES ON RESUME:
    - Resume requires a session_id from a previous failed/cancelled run
    - Get the session_id using get_seqera_workflow_status() on the failed workflow
    - Then pass that session_id to this function
    - Do NOT use resume without a session_id - it will fail with "Missing resume session id"
    
    Returns:
        Dict with status, workflow_id, monitoring URL, and launch details
    
    Example:
        # Fresh run with resource limits
        result = await run_methylseq_on_seqera(
            samplesheet_path="s3://my-bucket/samplesheet.csv",
            outdir="s3://my-bucket/results/run1",
            genome="GRCh38",
            max_memory="128.GB",
            max_cpus=32
        )
        
        # Resume a failed run
        status = await get_seqera_workflow_status(workflow_id="xyz", workspace_id=123)
        result = await run_methylseq_on_seqera(
            samplesheet_path="s3://my-bucket/samplesheet.csv",
            outdir="s3://my-bucket/results/run1",
            genome="GRCh38",
            session_id=status["session_id"]
        )
    """
    try:
        # ============================================================================
        # VALIDATION: Workspace and Compute Environment
        # ============================================================================
        final_workspace_id = workspace_id or (int(SEQERA_WORKSPACE_ID) if SEQERA_WORKSPACE_ID else None)
        final_compute_env_id = compute_env_id or SEQERA_COMPUTE_ENV_ID
        
        if not final_workspace_id:
            return {
                "status": "error",
                "error": "workspace_id not provided and SEQERA_WORKSPACE_ID not set",
                "solution": "Provide workspace_id parameter or set SEQERA_WORKSPACE_ID environment variable"
            }
        
        if not final_compute_env_id:
            return {
                "status": "error",
                "error": "compute_env_id not provided and SEQERA_COMPUTE_ENV_ID not set",
                "solution": "Provide compute_env_id parameter or set SEQERA_COMPUTE_ENV_ID environment variable"
            }
        
        # ============================================================================
        # VALIDATION: Output Directory (CRITICAL)
        # ============================================================================
        # outdir MUST be a cloud path for Seqera Platform
        if not any(outdir.startswith(p) for p in ["s3://", "gs://", "az://", "https://", "http://"]):
            return {
                "status": "error",
                "error": f"outdir must be a cloud storage path, got: {outdir}",
                "solution": "Set outdir to a cloud path like 's3://my-bucket/results/run1' or 'gs://my-bucket/results'",
                "example": "outdir='s3://mim-methylseq-data/results/run1'"
            }
        
        # ============================================================================
        # INITIALIZE CLIENT
        # ============================================================================
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        
        # ============================================================================
        # HANDLE SAMPLESHEET: Local vs Cloud
        # ============================================================================
        is_cloud_path = any(samplesheet_path.startswith(p) for p in ["s3://", "gs://", "az://", "http://", "https://"])
        final_samplesheet_path = samplesheet_path
        
        if not is_cloud_path:
            local_path = WORKSPACE_DIR / samplesheet_path if not Path(samplesheet_path).is_absolute() else Path(samplesheet_path)
            if not local_path.exists():
                return {
                    "status": "error",
                    "error": f"Local samplesheet not found: {samplesheet_path}",
                    "solution": "Check the file path or provide a cloud URL"
                }
            
            if auto_upload:
                if not work_dir or not work_dir.startswith("s3://"):
                    return {
                        "status": "error",
                        "error": "auto_upload requires work_dir to be an S3 path",
                        "solution": "Set work_dir='s3://my-bucket/work' or manually upload samplesheet"
                    }
                
                try:
                    import boto3
                    from urllib.parse import urlparse
                    
                    parsed = urlparse(work_dir)
                    bucket = parsed.netloc
                    prefix = parsed.path.strip('/')
                    
                    # Upload to a samplesheets subfolder
                    timestamp = generate_timestamp()
                    upload_key = f"{prefix}/samplesheets/{timestamp}_{local_path.name}" if prefix else f"samplesheets/{timestamp}_{local_path.name}"
                    final_samplesheet_path = f"s3://{bucket}/{upload_key}"
                    
                    s3_client = boto3.client('s3')
                    s3_client.upload_file(str(local_path), bucket, upload_key)
                    logger.info(f"✅ Uploaded samplesheet to {final_samplesheet_path}")
                    
                except ImportError:
                    return {
                        "status": "error",
                        "error": "auto_upload requires boto3",
                        "solution": "Install boto3: pip install boto3"
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "error": f"Failed to upload samplesheet: {str(e)}",
                        "solution": "Check AWS credentials and S3 bucket permissions"
                    }
            else:
                return {
                    "status": "error",
                    "error": "Samplesheet is a local path but auto_upload=False",
                    "solution": "Set auto_upload=True OR manually upload and provide cloud URL"
                }
        
        # ============================================================================
        # VALIDATE FASTA (if provided)
        # ============================================================================
        if fasta:
            is_fasta_cloud = any(fasta.startswith(p) for p in ["s3://", "gs://", "az://", "http://", "https://"])
            if not is_fasta_cloud:
                return {
                    "status": "error",
                    "error": f"fasta must be a cloud URL for Seqera Platform, got: {fasta}",
                    "solution": "Upload FASTA file to cloud storage first using upload_file_to_s3 tool"
                }
        
        # ============================================================================
        # BUILD RESOURCE LIMITS CONFIG (if max_memory or max_cpus specified)
        # ============================================================================
        resource_config = ""
        if max_memory or max_cpus:
            # Calculate scaled resources
            cpu_low = min(2, max_cpus) if max_cpus else 2
            cpu_medium = min(6, max_cpus) if max_cpus else 6
            cpu_high = max_cpus if max_cpus else 8
            
            mem_low = max_memory if max_memory else "12.GB"
            mem_medium = max_memory if max_memory else "36.GB"
            mem_high = max_memory if max_memory else "72.GB"
            
            # Build resource limits configuration with correct Groovy syntax
            resource_lines = []
            resource_lines.append("// Resource limits for Seqera Platform")
            resource_lines.append("process {")
            resource_lines.append("    // Process label resource overrides")
            resource_lines.append("    withLabel: 'process_low' {")
            resource_lines.append(f"        cpus = {cpu_low}")
            resource_lines.append(f"        memory = {mem_low}")  # No quotes - must be parsed as MemoryUnit
            resource_lines.append("        time = '4.h'")
            resource_lines.append("    }")
            resource_lines.append("    withLabel: 'process_medium' {")
            resource_lines.append(f"        cpus = {cpu_medium}")
            resource_lines.append(f"        memory = {mem_medium}")  # No quotes
            resource_lines.append("        time = '8.h'")
            resource_lines.append("    }")
            resource_lines.append("    withLabel: 'process_high' {")
            resource_lines.append(f"        cpus = {cpu_high}")
            resource_lines.append(f"        memory = {mem_high}")  # No quotes
            resource_lines.append("        time = '16.h'")
            resource_lines.append("    }")
            resource_lines.append("    withLabel: 'process_long' {")
            resource_lines.append("        time = '20.h'")
            resource_lines.append("    }")
            resource_lines.append("}")
            resource_config = "\n".join(resource_lines)
        
        # Merge with user-provided config_text
        final_config_text = None
        if resource_config or config_text:
            parts = []
            if resource_config:
                parts.append(resource_config)
            if config_text:
                parts.append(config_text)
            final_config_text = "\n\n".join(parts)
        
        # ============================================================================
        # BUILD PIPELINE PARAMETERS (as dict, will be converted to JSON)
        # ============================================================================
        # CRITICAL: ALL required params must be included
        params = {
            "input": final_samplesheet_path,
            "outdir": outdir,
            "aligner": aligner,
        }
        
        # Add genome or fasta
        if fasta:
            params["fasta"] = fasta
            params["igenomes_ignore"] = True
        elif genome:
            params["genome"] = genome
        
        # Add optional parameters only if they differ from defaults or are explicitly set
        if non_directional:
            params["non_directional"] = True
        if library_type:
            params["library_type"] = library_type
        
        # Clipping parameters
        if clip_r1 > 0:
            params["clip_r1"] = clip_r1
        if clip_r2 > 0:
            params["clip_r2"] = clip_r2
        if three_prime_clip_r1 > 0:
            params["three_prime_clip_r1"] = three_prime_clip_r1
        if three_prime_clip_r2 > 0:
            params["three_prime_clip_r2"] = three_prime_clip_r2
        
        # M-bias ignore parameters (only add if non-default)
        if ignore_r1 > 0:
            params["ignore_r1"] = ignore_r1
        if ignore_r2 != 2:  # 2 is the default
            params["ignore_r2"] = ignore_r2
        if ignore_3prime_r1 > 0:
            params["ignore_3prime_r1"] = ignore_3prime_r1
        if ignore_3prime_r2 != 2:  # 2 is the default
            params["ignore_3prime_r2"] = ignore_3prime_r2
        
        # Boolean flags (only add if True)
        if skip_trimming:
            params["skip_trimming"] = True
        if skip_deduplication:
            params["skip_deduplication"] = True
        if save_trimmed:
            params["save_trimmed"] = True
        if save_reference:
            params["save_reference"] = True
        if save_align_intermeds:
            params["save_align_intermeds"] = True
        if not cytosine_report:  # False is non-default
            params["cytosine_report"] = False
        if comprehensive:
            params["comprehensive"] = True
        
        if min_depth > 0:
            params["min_depth"] = min_depth
        
        if igenomes_ignore:
            params["igenomes_ignore"] = True
        if igenomes_base:
            params["igenomes_base"] = igenomes_base
        
        # Add any extra parameters
        if extra_params:
            params.update(extra_params)
        
        # ============================================================================
        # CONVERT PARAMS TO JSON STRING (Seqera Platform expects paramsText)
        # ============================================================================
        params_json = json.dumps(params, indent=2)
        
        # ============================================================================
        # BUILD LAUNCH PAYLOAD
        # ============================================================================
        run_name = run_name or f"methylseq_{generate_timestamp()}"
        config_profiles = config_profiles or ["singularity"]
        
        # Build the launch configuration
        launch_config = {
            "computeEnvId": final_compute_env_id,
            "pipeline": "nf-core/methylseq",
            "revision": pipeline_revision,
            "runName": run_name,
            "paramsText": params_json,  # Pipeline parameters as JSON string
            "configProfiles": config_profiles,
            "pullLatest": pull_latest,
        }
        
        # CRITICAL FIX: Only enable resume if session_id is provided
        if session_id:
            launch_config["sessionId"] = session_id
            launch_config["resume"] = True
            logger.info(f"  Resume:       Enabled (session: {session_id})")
        
        # Add work directory if provided
        if work_dir:
            launch_config["workDir"] = work_dir
        
        # Add resource config or custom config
        if final_config_text:
            launch_config["configText"] = final_config_text
        
        # Add optional launch configurations
        if stub_run:
            launch_config["stubRun"] = True
        if pre_run_script:
            launch_config["preRunScript"] = pre_run_script
        if post_run_script:
            launch_config["postRunScript"] = post_run_script
        
        # ============================================================================
        # LAUNCH PIPELINE VIA API
        # ============================================================================
        logger.info(f"Launching methylseq pipeline on Seqera Platform...")
        logger.info(f"  Workspace ID: {final_workspace_id}")
        logger.info(f"  Compute Env:  {final_compute_env_id}")
        logger.info(f"  Pipeline:     nf-core/methylseq@{pipeline_revision}")
        logger.info(f"  Run name:     {run_name}")
        logger.info(f"  Input:        {final_samplesheet_path}")
        logger.info(f"  Output:       {outdir}")
        if max_memory:
            logger.info(f"  Max Memory:   {max_memory}")
        if max_cpus:
            logger.info(f"  Max CPUs:     {max_cpus}")
        
        payload = {"launch": launch_config}
        
        try:
            response = client._request(
                "POST",
                f"/workflow/launch?workspaceId={final_workspace_id}",
                json=payload
            )
        except Exception as api_error:
            return {
                "status": "error",
                "error": f"API launch failed: {str(api_error)}",
                "details": {
                    "workspace_id": final_workspace_id,
                    "compute_env_id": final_compute_env_id,
                    "run_name": run_name,
                },
                "solution": "Check API credentials, workspace/compute env IDs, and parameter values"
            }
        
        # ============================================================================
        # EXTRACT WORKFLOW ID AND BUILD RESPONSE
        # ============================================================================
        workflow_id = response.get("workflowId")
        
        if not workflow_id:
            return {
                "status": "error",
                "error": "No workflow ID returned from API",
                "api_response": response
            }
        
        # Build monitoring URL
        monitor_url = f"https://cloud.seqera.io/orgs/{final_workspace_id}/watch/{workflow_id}"
        
        return {
            "status": "success",
            "message": "✅ Pipeline launched successfully on Seqera Platform",
            "workflow_id": workflow_id,
            "run_name": run_name,
            "workspace_id": final_workspace_id,
            "compute_env_id": final_compute_env_id,
            "pipeline": f"nf-core/methylseq@{pipeline_revision}",
            "monitor_url": monitor_url,
            "input_samplesheet": final_samplesheet_path,
            "output_directory": outdir,
            "work_directory": work_dir or "(using compute environment default)",
            "config_profiles": config_profiles,
            "resource_limits": {
                "max_memory": max_memory or "Not set (using compute env defaults)",
                "max_cpus": max_cpus or "Not set (using compute env defaults)"
            },
            "resume_from_session": session_id or "None (fresh run)",
            "parameters": params,  # Show all parameters used
            "next_steps": [
                f"Monitor progress at: {monitor_url}",
                f"Or use: get_seqera_workflow_status(workflow_id='{workflow_id}', workspace_id={final_workspace_id})",
                f"Results will be published to: {outdir}",
                "If this run fails, get the session_id from workflow details to resume later"
            ]
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in run_methylseq_on_seqera: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__,
            "solution": "Check logs for detailed traceback"
        }

@mcp.tool
@return_as_dict
async def fetch_sra_to_s3_via_seqera(
    accession_ids: Union[str, List[str]],
    output_s3_path: str,
    workspace_id: Optional[int] = None,
    compute_env_id: Optional[str] = None,
    work_dir: Optional[str] = None,
    download_method: str = "ftp",
    nf_core_pipeline: str = "sratools",
    run_name: Optional[str] = None,
    api_token: Optional[str] = None,
    api_url: Optional[str] = None,
    wait_for_completion: bool = False,
    auto_launch_methylseq: bool = False,
    methylseq_genome: Optional[str] = None,
    methylseq_outdir: Optional[str] = None,
    methylseq_params: Optional[Dict[str, Any]] = None  # NEW: Pass custom methylseq parameters
) -> Dict[str, Any]:
    """
    Download SRA data DIRECTLY to S3 bucket using Seqera Platform (no local download).
    
    This is MUCH faster than downloading locally then uploading because:
    - AWS Batch instances download directly from SRA to S3 (both in AWS)
    - No bandwidth limits from your local machine
    - Can handle massive datasets (hundreds of GB)
    - Parallel downloads across multiple samples
    
    WORKFLOW:
    1. Creates an input CSV with SRA accession IDs
    2. Uploads the CSV to S3
    3. Launches nf-core/fetchngs on Seqera Platform (AWS Batch)
    4. fetchngs downloads SRA data directly to your S3 bucket
    5. Generates a samplesheet for downstream analysis
    6. Optionally launches methylseq pipeline automatically
    
    Args:
        accession_ids: SRA accession ID(s). Can be:
                      - Single ID: "SRR11605097"
                      - Comma-separated: "SRR11605097,ERR4007730,DRR171822"
                      - List: ["SRR11605097", "ERR4007730", "DRR171822"]
        
        output_s3_path: S3 path where SRA data will be downloaded
                       Example: "s3://my-bucket/sra-data/project1"
        
        workspace_id: Seqera workspace ID (defaults to SEQERA_WORKSPACE_ID env var)
        compute_env_id: Compute environment ID (defaults to SEQERA_COMPUTE_ENV_ID env var)
        work_dir: Work directory for scratch files (optional)
        
        download_method: How to download from SRA:
                        - "ftp": Standard FTP download (default, most reliable)
                        - "sratools": Use SRA Toolkit (faster, requires more setup)
                        - "aspera": Use Aspera (fastest, requires IBM Aspera)
        
        nf_core_pipeline: Which nf-core pipeline to use (default: "sratools")
        run_name: Custom name for the fetchngs run
        api_token: Seqera API token (defaults to TOWER_ACCESS_TOKEN env var)
        api_url: Seqera API URL (defaults to cloud.seqera.io)
        
        wait_for_completion: If True, wait for fetchngs to complete before returning
                            If False, return immediately with workflow_id to monitor
        
        auto_launch_methylseq: If True, automatically launch methylseq after fetchngs completes
                              Requires wait_for_completion=True to work
        
        methylseq_genome: Genome to use for methylseq (required if auto_launch_methylseq=True)
                         Example: "GRCh38", "GRCm39", "hg38"
        
        methylseq_outdir: Output directory for methylseq results
                         If not provided, uses "{output_s3_path}_methylseq_results"
        
        methylseq_params: Dictionary of additional methylseq parameters. Examples:
                         {
                             "aligner": "bismark",  # or "bwameth", "bismark_hisat"
                             "non_directional": True,  # For non-directional libraries
                             "library_type": "rrbs",  # or "pbat", "em_seq", etc.
                             "clip_r1": 10,  # Clip 10bp from 5' end of R1
                             "clip_r2": 10,
                             "ignore_r1": 5,  # Ignore first 5bp for methylation
                             "ignore_r2": 5,
                             "skip_trimming": False,
                             "save_trimmed": True,
                             "comprehensive": True,
                             "min_depth": 10
                         }
                         See run_methylseq_on_seqera documentation for all options.
    
    Returns:
        Dict with fetchngs workflow_id, monitoring URL, and samplesheet location
    
    Example:
        # Simple: Download SRA data to S3
        result = await fetch_sra_to_s3_via_seqera(
            accession_ids="SRR11605097,SRR11605098",
            output_s3_path="s3://my-bucket/sra-downloads/project1"
        )
        
        # Advanced: Auto-launch methylseq with custom parameters
        result = await fetch_sra_to_s3_via_seqera(
            accession_ids=["SRR11605097", "SRR11605098"],
            output_s3_path="s3://my-bucket/sra-downloads/rrbs_study",
            wait_for_completion=True,
            auto_launch_methylseq=True,
            methylseq_genome="GRCh38",
            methylseq_outdir="s3://my-bucket/methylseq-results/rrbs_study",
            methylseq_params={
                "aligner": "bismark",
                "library_type": "rrbs",  # RRBS library
                "non_directional": False,
                "clip_r1": 10,  # Clip adapter artifacts
                "clip_r2": 10,
                "ignore_r1": 5,  # Ignore M-bias artifacts
                "ignore_r2": 5,
                "comprehensive": True,
                "save_trimmed": True,
                "min_depth": 10
            }
        )
        
        # WGBS example with different parameters
        result = await fetch_sra_to_s3_via_seqera(
            accession_ids="SRR12345678",
            output_s3_path="s3://my-bucket/wgbs-data",
            wait_for_completion=True,
            auto_launch_methylseq=True,
            methylseq_genome="GRCm39",
            methylseq_params={
                "aligner": "bwameth",  # Faster for WGBS
                "non_directional": False,
                "skip_deduplication": False,
                "comprehensive": True
            }
        )
    """
    try:
        # ============================================================================
        # VALIDATION: Workspace and Compute Environment
        # ============================================================================
        final_workspace_id = workspace_id or (int(SEQERA_WORKSPACE_ID) if SEQERA_WORKSPACE_ID else None)
        final_compute_env_id = compute_env_id or SEQERA_COMPUTE_ENV_ID
        
        if not final_workspace_id:
            return {
                "status": "error",
                "error": "workspace_id not provided and SEQERA_WORKSPACE_ID not set",
                "solution": "Provide workspace_id parameter or set SEQERA_WORKSPACE_ID environment variable"
            }
        
        if not final_compute_env_id:
            return {
                "status": "error",
                "error": "compute_env_id not provided and SEQERA_COMPUTE_ENV_ID not set",
                "solution": "Provide compute_env_id parameter or set SEQERA_COMPUTE_ENV_ID environment variable"
            }
        
        # Validate auto_launch_methylseq requirements
        if auto_launch_methylseq:
            if not wait_for_completion:
                return {
                    "status": "error",
                    "error": "auto_launch_methylseq=True requires wait_for_completion=True",
                    "solution": "Set wait_for_completion=True to enable auto-launch"
                }
            if not methylseq_genome:
                return {
                    "status": "error",
                    "error": "auto_launch_methylseq=True requires methylseq_genome parameter",
                    "solution": "Provide methylseq_genome (e.g., 'GRCh38', 'GRCm39')"
                }
        
        # Validate output path is S3
        if not output_s3_path.startswith("s3://"):
            return {
                "status": "error",
                "error": f"output_s3_path must be an S3 path, got: {output_s3_path}",
                "solution": "Use an S3 path like 's3://my-bucket/sra-data/project1'"
            }
        
        # ============================================================================
        # PARSE AND VALIDATE ACCESSION IDs
        # ============================================================================
        if isinstance(accession_ids, str):
            acc_list = [acc.strip() for acc in accession_ids.split(',') if acc.strip()]
        elif isinstance(accession_ids, list):
            acc_list = [str(acc).strip() for acc in accession_ids if acc]
        else:
            return {
                "status": "error",
                "error": f"accession_ids must be string or list, got: {type(accession_ids)}"
            }
        
        if not acc_list:
            return {
                "status": "error",
                "error": "No accession IDs provided"
            }
        
        # Validate accession ID formats
        valid_prefixes = ['SRR', 'ERR', 'DRR', 'SRX', 'ERX', 'DRX', 'GSM', 'GSE', 
                         'SRS', 'ERS', 'DRS', 'SAMN', 'SAMEA', 'SAMD', 'SRP', 
                         'ERP', 'DRP', 'SRA', 'ERA', 'DRA', 'PRJNA', 'PRJEB', 'PRJDB']
        
        invalid_ids = []
        for acc_id in acc_list:
            if not any(acc_id.upper().startswith(prefix) for prefix in valid_prefixes):
                invalid_ids.append(acc_id)
        
        if invalid_ids:
            return {
                "status": "error",
                "error": f"Invalid accession IDs: {', '.join(invalid_ids)}",
                "valid_formats": "Must start with: " + ", ".join(valid_prefixes)
            }
        
        logger.info(f"Validated {len(acc_list)} SRA accession IDs")
        
        # ============================================================================
        # CREATE INPUT CSV AND UPLOAD TO S3
        # ============================================================================
        try:
            import boto3
            from urllib.parse import urlparse
        except ImportError:
            return {
                "status": "error",
                "error": "boto3 not installed",
                "solution": "Install boto3: pip install boto3"
            }
        
        timestamp = generate_timestamp()
        csv_filename = f"sra_ids_{timestamp}.csv"
        local_csv = WORKSPACE_DIR / csv_filename
        
        with open(local_csv, 'w') as f:
            for acc_id in acc_list:
                f.write(f"{acc_id}\n")
        
        logger.info(f"Created local CSV with {len(acc_list)} accession IDs")
        
        # Upload CSV to S3
        parsed = urlparse(output_s3_path)
        bucket = parsed.netloc
        prefix = parsed.path.strip('/')
        
        csv_s3_key = f"{prefix}/input/{csv_filename}" if prefix else f"input/{csv_filename}"
        csv_s3_path = f"s3://{bucket}/{csv_s3_key}"
        
        try:
            s3_client = boto3.client('s3')
            s3_client.upload_file(str(local_csv), bucket, csv_s3_key)
            logger.info(f"✅ Uploaded input CSV to {csv_s3_path}")
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to upload CSV to S3: {str(e)}",
                "solution": "Check AWS credentials and S3 bucket permissions"
            }
        
        # ============================================================================
        # PREPARE FETCHNGS PIPELINE PARAMETERS
        # ============================================================================
        pipeline_name = "nf-core/fetchngs"
        
        fetchngs_params = {
            "input": csv_s3_path,
            "outdir": output_s3_path,
            "download_method": download_method,
        }
        
        if nf_core_pipeline == "aspera":
            fetchngs_params["download_method"] = "aspera"
        
        params_json = json.dumps(fetchngs_params, indent=2)
        
        # ============================================================================
        # BUILD LAUNCH CONFIGURATION
        # ============================================================================
        run_name = run_name or f"fetchngs_sra_{timestamp}"
        
        launch_config = {
            "computeEnvId": final_compute_env_id,
            "pipeline": pipeline_name,
            "revision": "1.12.0",
            "runName": run_name,
            "paramsText": params_json,
            "configProfiles": ["docker"],
            "pullLatest": False,
        }
        
        if work_dir:
            launch_config["workDir"] = work_dir
        
        # ============================================================================
        # LAUNCH FETCHNGS ON SEQERA PLATFORM
        # ============================================================================
        client = SeqeraClient(api_token=api_token, api_url=api_url)
        
        logger.info(f"Launching fetchngs on Seqera Platform...")
        logger.info(f"  Pipeline:     {pipeline_name}")
        logger.info(f"  Accessions:   {len(acc_list)}")
        logger.info(f"  Output:       {output_s3_path}")
        logger.info(f"  Method:       {download_method}")
        
        payload = {"launch": launch_config}
        
        try:
            response = client._request(
                "POST",
                f"/workflow/launch?workspaceId={final_workspace_id}",
                json=payload
            )
        except Exception as api_error:
            return {
                "status": "error",
                "error": f"API launch failed: {str(api_error)}",
                "solution": "Check API credentials, workspace/compute env IDs"
            }
        
        workflow_id = response.get("workflowId")
        
        if not workflow_id:
            return {
                "status": "error",
                "error": "No workflow ID returned from API",
                "api_response": response
            }
        
        monitor_url = f"https://cloud.seqera.io/orgs/{final_workspace_id}/watch/{workflow_id}"
        
        logger.info(f"✅ fetchngs launched successfully: {workflow_id}")
        
        # ============================================================================
        # WAIT FOR COMPLETION (if requested)
        # ============================================================================
        if wait_for_completion:
            logger.info("Waiting for fetchngs to complete...")
            import time
            
            max_wait_time = 7200  # 2 hours max
            check_interval = 30
            elapsed = 0
            
            while elapsed < max_wait_time:
                try:
                    status_result = client.get_workflow_status(workflow_id, final_workspace_id)
                    workflow_status = status_result.get("status")
                    
                    logger.info(f"  Status: {workflow_status} (elapsed: {elapsed}s)")
                    
                    if workflow_status in ["SUCCEEDED", "COMPLETED"]:
                        logger.info("✅ fetchngs completed successfully!")
                        break
                    elif workflow_status in ["FAILED", "CANCELLED", "UNKNOWN"]:
                        return {
                            "status": "error",
                            "error": f"fetchngs workflow failed with status: {workflow_status}",
                            "workflow_id": workflow_id,
                            "monitor_url": monitor_url
                        }
                    
                    time.sleep(check_interval)
                    elapsed += check_interval
                    
                except Exception as e:
                    logger.warning(f"Error checking status: {e}")
                    time.sleep(check_interval)
                    elapsed += check_interval
            
            if elapsed >= max_wait_time:
                return {
                    "status": "timeout",
                    "error": "fetchngs did not complete within 2 hours",
                    "workflow_id": workflow_id,
                    "monitor_url": monitor_url,
                    "solution": "Monitor manually and check results in S3"
                }
        
        # ============================================================================
        # FIND GENERATED SAMPLESHEET
        # ============================================================================
        expected_samplesheet = f"{output_s3_path.rstrip('/')}/samplesheet/samplesheet.csv"
        
        # ============================================================================
        # AUTO-LAUNCH METHYLSEQ (if requested and fetchngs completed)
        # ============================================================================
        methylseq_workflow_id = None
        methylseq_launch_params = None
        
        if auto_launch_methylseq and wait_for_completion:
            methylseq_outdir = methylseq_outdir or f"{output_s3_path.rstrip('/')}_methylseq_results"
            
            logger.info(f"Auto-launching methylseq pipeline...")
            logger.info(f"  Genome:       {methylseq_genome}")
            logger.info(f"  Output:       {methylseq_outdir}")
            
            # Build methylseq parameters by merging defaults with user-provided params
            methylseq_launch_params = {
                "samplesheet_path": expected_samplesheet,
                "outdir": methylseq_outdir,
                "workspace_id": final_workspace_id,
                "compute_env_id": final_compute_env_id,
                "genome": methylseq_genome,
                "work_dir": work_dir,
                "api_token": api_token,
                "api_url": api_url
            }
            
            # Merge user-provided methylseq parameters
            if methylseq_params:
                logger.info(f"  Custom params: {list(methylseq_params.keys())}")
                methylseq_launch_params.update(methylseq_params)
            
            # Log key methylseq settings
            if methylseq_params:
                for key in ["aligner", "library_type", "non_directional", "clip_r1", "clip_r2"]:
                    if key in methylseq_params:
                        logger.info(f"  {key}: {methylseq_params[key]}")
            
            try:
                methylseq_result = await run_methylseq_on_seqera(**methylseq_launch_params)
                
                if methylseq_result.get("status") == "success":
                    methylseq_workflow_id = methylseq_result.get("workflow_id")
                    logger.info(f"✅ methylseq launched: {methylseq_workflow_id}")
                else:
                    logger.error(f"Failed to launch methylseq: {methylseq_result.get('error')}")
                    return {
                        "status": "partial_success",
                        "message": "fetchngs completed but methylseq launch failed",
                        "fetchngs_workflow_id": workflow_id,
                        "fetchngs_status": "completed",
                        "methylseq_error": methylseq_result.get("error"),
                        "expected_samplesheet": expected_samplesheet,
                        "solution": "Launch methylseq manually using the samplesheet"
                    }
            except Exception as e:
                logger.error(f"Error launching methylseq: {e}", exc_info=True)
                return {
                    "status": "partial_success",
                    "message": "fetchngs completed but methylseq launch failed",
                    "fetchngs_workflow_id": workflow_id,
                    "methylseq_error": str(e),
                    "expected_samplesheet": expected_samplesheet
                }
        
        # ============================================================================
        # BUILD RESPONSE
        # ============================================================================
        result = {
            "status": "success",
            "message": "✅ SRA download to S3 launched successfully",
            "fetchngs_workflow_id": workflow_id,
            "run_name": run_name,
            "monitor_url": monitor_url,
            "accession_ids": acc_list,
            "accession_count": len(acc_list),
            "download_method": download_method,
            "output_s3_path": output_s3_path,
            "expected_samplesheet": expected_samplesheet,
            "input_csv_s3": csv_s3_path,
            "next_steps": [
                f"Monitor fetchngs progress at: {monitor_url}",
                f"Or use: get_seqera_workflow_status(workflow_id='{workflow_id}', workspace_id={final_workspace_id})",
                f"Downloaded files will be in: {output_s3_path}",
                f"Samplesheet for methylseq will be at: {expected_samplesheet}",
            ]
        }
        
        if methylseq_workflow_id:
            result["methylseq_workflow_id"] = methylseq_workflow_id
            result["methylseq_auto_launched"] = True
            result["methylseq_params_used"] = methylseq_params or {}
            result["next_steps"].append(f"methylseq is running: workflow_id={methylseq_workflow_id}")
        elif auto_launch_methylseq and not wait_for_completion:
            result["next_steps"].append(
                "To auto-launch methylseq, set wait_for_completion=True"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in fetch_sra_to_s3_via_seqera: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        }


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
