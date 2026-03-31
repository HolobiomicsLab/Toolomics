#!/usr/bin/env python3
"""
Batch docking script for covalent inhibitors.

Docks multiple ligands in parallel and generates a summary report.
"""

import argparse
import json
import subprocess
import concurrent.futures
from pathlib import Path
from glob import glob


def dock_single_ligand(
    ligand_sdf: str,
    receptor_pdb: str,
    receptor_atom: str,
    attachment_smarts: str,
    output_dir: str,
    seeds: list = None
) -> dict:
    """Dock a single ligand."""
    
    seeds = seeds or [0, 42, 123]
    ligand_name = Path(ligand_sdf).stem
    output_prefix = f"{output_dir}/{ligand_name}"
    
    result = {
        "ligand": ligand_name,
        "ligand_file": ligand_sdf,
        "success": False,
        "affinity": None,
        "error": None
    }
    
    try:
        # Run GNINA with multi-seed
        cmd = [
            "gnina",
            "--receptor", receptor_pdb,
            "--ligand", ligand_sdf,
            "--covalent", receptor_atom,
            "--cov_atom", attachment_smarts,
            "--covalent_optimize",
            "--num_modes", "5"
        ]
        
        # Add seeds
        for seed in seeds:
            cmd.extend(["--seed", str(seed)])
        
        cmd.extend(["--out", f"{output_prefix}_docked.sdf"])
        
        # Run docking
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if proc.returncode != 0:
            result["error"] = proc.stderr
            return result
        
        # Parse output to get affinity
        # This is simplified - real implementation would parse SDF output
        affinity = parse_affinity_from_output(proc.stdout)
        
        result["success"] = True
        result["affinity"] = affinity
        result["output_file"] = f"{output_prefix}_docked.sdf"
        
    except subprocess.TimeoutExpired:
        result["error"] = "Docking timeout"
    except FileNotFoundError:
        result["error"] = "GNINA not found"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def parse_affinity_from_output(stdout: str) -> float:
    """Parse affinity from GNINA output."""
    # Simplified - look for affinity in output
    # Real implementation would parse SDF file
    for line in stdout.split('\n'):
        if 'Affinity' in line or 'CNNaffinity' in line:
            try:
                # Extract number from line
                parts = line.split()
                for part in parts:
                    try:
                        return float(part)
                    except ValueError:
                        continue
            except:
                pass
    return -1.0  # Unknown


def main():
    parser = argparse.ArgumentParser(
        description="Batch dock multiple covalent ligands"
    )
    parser.add_argument("--ligands", required=True,
                       help="Ligand files (glob pattern or directory)")
    parser.add_argument("--receptor", required=True,
                       help="Receptor PDB file")
    parser.add_argument("--receptor_atom", required=True,
                       help="Receptor atom (format: chain:resnum:atom_name)")
    parser.add_argument("--attachment_smarts", default="[CD1]",
                       help="Attachment atom SMARTS pattern")
    parser.add_argument("--output_dir", default="batch_results",
                       help="Output directory")
    parser.add_argument("--seeds", default="0,42,123",
                       help="Comma-separated random seeds")
    parser.add_argument("--parallel", type=int, default=1,
                       help="Number of parallel processes")
    parser.add_argument("--output_json", default="batch_results.json",
                       help="Output JSON summary")
    
    args = parser.parse_args()
    
    # Parse seeds
    seeds = [int(s) for s in args.seeds.split(",")]
    
    # Find ligand files
    if Path(args.ligands).is_dir():
        ligand_files = list(Path(args.ligands).glob("*.sdf"))
    else:
        ligand_files = [Path(f) for f in glob(args.ligands)]
    
    if not ligand_files:
        print(f"Error: No ligand files found matching '{args.ligands}'")
        return 1
    
    print("="*60)
    print("BATCH COVALENT DOCKING")
    print("="*60)
    print(f"\nReceptor: {args.receptor}")
    print(f"Receptor atom: {args.receptor_atom}")
    print(f"Attachment SMARTS: {args.attachment_smarts}")
    print(f"Seeds: {seeds}")
    print(f"Ligands: {len(ligand_files)}")
    print(f"Parallel: {args.parallel}")
    print(f"Output directory: {args.output_dir}")
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Dock ligands
    print("\n" + "-"*60)
    print("DOCKING PROGRESS")
    print("-"*60)
    
    results = []
    
    if args.parallel > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.parallel) as executor:
            futures = {
                executor.submit(
                    dock_single_ligand,
                    str(ligand),
                    args.receptor,
                    args.receptor_atom,
                    args.attachment_smarts,
                    args.output_dir,
                    seeds
                ): ligand for ligand in ligand_files
            }
            
            for future in concurrent.futures.as_completed(futures):
                ligand = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    status = "✓" if result["success"] else "✗"
                    aff_str = f"{result['affinity']:.2f}" if result["affinity"] else "N/A"
                    print(f"  {status} {result['ligand']}: {aff_str} kcal/mol")
                except Exception as e:
                    print(f"  ✗ {ligand.name}: Error - {e}")
                    results.append({
                        "ligand": ligand.stem,
                        "success": False,
                        "error": str(e)
                    })
    else:
        for ligand in ligand_files:
            result = dock_single_ligand(
                str(ligand),
                args.receptor,
                args.receptor_atom,
                args.attachment_smarts,
                args.output_dir,
                seeds
            )
            results.append(result)
            
            status = "✓" if result["success"] else "✗"
            aff_str = f"{result['affinity']:.2f}" if result["affinity"] else "N/A"
            print(f"  {status} {result['ligand']}: {aff_str} kcal/mol")
    
    # Summary statistics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print("\n" + "-"*60)
    print("SUMMARY")
    print("-"*60)
    print(f"\nTotal: {len(results)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    
    if successful:
        affinities = [r["affinity"] for r in successful if r["affinity"]]
        if affinities:
            print(f"\nAffinity Statistics:")
            print(f"  Best: {min(affinities):.2f} kcal/mol")
            print(f"  Worst: {max(affinities):.2f} kcal/mol")
            print(f"  Mean: {sum(affinities)/len(affinities):.2f} kcal/mol")
            
            # Top 5
            sorted_results = sorted(successful, key=lambda x: x["affinity"] or 0)
            print(f"\nTop 5:")
            for i, r in enumerate(sorted_results[:5], 1):
                print(f"  {i}. {r['ligand']}: {r['affinity']:.2f} kcal/mol")
    
    if failed:
        print(f"\nFailed ligands:")
        for r in failed[:5]:
            print(f"  - {r['ligand']}: {r.get('error', 'Unknown error')}")
    
    # Save results
    output_data = {
        "receptor": args.receptor,
        "receptor_atom": args.receptor_atom,
        "attachment_smarts": args.attachment_smarts,
        "seeds": seeds,
        "summary": {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "best_affinity": min([r["affinity"] for r in successful if r["affinity"]], default=None)
        },
        "results": results
    }
    
    with open(args.output_json, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to: {args.output_json}")
    print("\n" + "="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
