#!/usr/bin/env python3
"""
Validate covalent bond geometry in docked poses.

Measures receptor-ligand distance and compares to expected bond lengths.
"""

import argparse
import json
import numpy as np
from pathlib import Path


def parse_atom_line(line: str) -> dict:
    """Parse PDB ATOM/HETATM line."""
    return {
        "record": line[0:6].strip(),
        "atom_num": int(line[6:11]),
        "atom_name": line[12:16].strip(),
        "res_name": line[17:20].strip(),
        "chain": line[21],
        "res_num": int(line[22:26]),
        "x": float(line[30:38]),
        "y": float(line[38:46]),
        "z": float(line[46:54])
    }


def find_receptor_atom(pdb_file: str, chain: str, res_num: int, atom_name: str) -> dict:
    """Find specific atom in receptor PDB."""
    with open(pdb_file) as f:
        for line in f:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            
            atom = parse_atom_line(line)
            if (atom["chain"] == chain and 
                atom["res_num"] == res_num and 
                atom["atom_name"] == atom_name):
                return atom
    
    return None


def find_ligand_attachment_atom(pdb_file: str) -> dict:
    """Find the ligand atom closest to where covalent bond should form."""
    # In covalent docking, the ligand should be positioned such that
    # the warhead attachment atom is near the receptor reactive atom
    
    # For now, find the first HETATM that's likely the attachment point
    # (closest to the receptor atom would require knowing both)
    
    hetatms = []
    with open(pdb_file) as f:
        for line in f:
            if line.startswith("HETATM"):
                atom = parse_atom_line(line)
                hetatms.append(atom)
    
    if not hetatms:
        return None
    
    # Return first carbon atom (likely attachment point)
    for atom in hetatms:
        if atom["atom_name"].startswith("C"):
            return atom
    
    return hetatms[0]


def calculate_distance(atom1: dict, atom2: dict) -> float:
    """Calculate distance between two atoms."""
    coord1 = np.array([atom1["x"], atom1["y"], atom1["z"]])
    coord2 = np.array([atom2["x"], atom2["y"], atom2["z"]])
    return np.linalg.norm(coord1 - coord2)


def validate_bond_length(bond_type: str, distance: float, tolerance: float) -> dict:
    """Validate bond length against expected range."""
    BOND_LENGTHS = {
        "C-Se": (1.85, 2.05),
        "C-S": (1.75, 1.95),
        "C-N": (1.40, 1.55),
        "C-O": (1.40, 1.50)
    }
    
    if bond_type not in BOND_LENGTHS:
        return {
            "valid": False,
            "error": f"Unknown bond type: {bond_type}"
        }
    
    expected_min, expected_max = BOND_LENGTHS[bond_type]
    
    if expected_min - tolerance <= distance <= expected_max + tolerance:
        if expected_min <= distance <= expected_max:
            assessment = "optimal"
        else:
            assessment = "acceptable"
        is_valid = True
    else:
        assessment = "poor"
        is_valid = False
    
    return {
        "valid": is_valid,
        "assessment": assessment,
        "distance": round(distance, 2),
        "expected_min": expected_min,
        "expected_max": expected_max,
        "tolerance": tolerance
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate covalent bond geometry"
    )
    parser.add_argument("--docked", required=True, 
                       help="Docked pose PDB/SDF file")
    parser.add_argument("--receptor", required=True,
                       help="Receptor PDB file")
    parser.add_argument("--receptor_atom", required=True,
                       help="Receptor atom (format: chain:resnum:atom_name)")
    parser.add_argument("--bond_type", default="C-Se",
                       choices=["C-Se", "C-S", "C-N", "C-O"],
                       help="Expected covalent bond type")
    parser.add_argument("--tolerance", type=float, default=0.1,
                       help="Tolerance beyond expected range (Angstroms)")
    parser.add_argument("--output", help="Output JSON file (optional)")
    
    args = parser.parse_args()
    
    print("="*60)
    print("COVALENT BOND GEOMETRY VALIDATION")
    print("="*60)
    
    # Parse receptor atom specification
    try:
        chain, resnum, atom_name = args.receptor_atom.split(":")
        resnum = int(resnum)
    except ValueError:
        print(f"Error: Invalid receptor atom format. Use 'chain:resnum:atom_name'")
        return 1
    
    print(f"\nReceptor atom: {chain}:{resnum}:{atom_name}")
    print(f"Expected bond type: {args.bond_type}")
    
    # Find receptor atom
    receptor_atom = find_receptor_atom(args.receptor, chain, resnum, atom_name)
    if receptor_atom is None:
        print(f"Error: Could not find receptor atom {args.receptor_atom}")
        return 1
    
    print(f"  Found at: ({receptor_atom['x']:.3f}, {receptor_atom['y']:.3f}, {receptor_atom['z']:.3f})")
    
    # Find ligand attachment atom
    ligand_atom = find_ligand_attachment_atom(args.docked)
    if ligand_atom is None:
        print(f"Error: Could not find ligand attachment atom")
        return 1
    
    print(f"\nLigand atom: {ligand_atom['atom_name']}")
    print(f"  Found at: ({ligand_atom['x']:.3f}, {ligand_atom['y']:.3f}, {ligand_atom['z']:.3f})")
    
    # Calculate distance
    distance = calculate_distance(receptor_atom, ligand_atom)
    print(f"\nDistance: {distance:.2f} Å")
    
    # Validate
    result = validate_bond_length(args.bond_type, distance, args.tolerance)
    
    print(f"\nExpected range: {result['expected_min']:.2f} - {result['expected_max']:.2f} Å")
    print(f"Assessment: {result['assessment'].upper()}")
    
    if result['valid']:
        print("\n✓ Geometry VALID")
    else:
        print("\n✗ Geometry INVALID")
        print(f"  Distance {distance:.2f} Å outside acceptable range")
    
    # Prepare output
    output = {
        "success": result['valid'],
        "distance": result['distance'],
        "expected_range": [result['expected_min'], result['expected_max']],
        "assessment": result['assessment'],
        "receptor_atom": {
            "name": receptor_atom['atom_name'],
            "residue": f"{receptor_atom['res_name']} {receptor_atom['res_num']}",
            "chain": receptor_atom['chain'],
            "coordinates": [receptor_atom['x'], receptor_atom['y'], receptor_atom['z']]
        },
        "ligand_atom": {
            "name": ligand_atom['atom_name'],
            "coordinates": [ligand_atom['x'], ligand_atom['y'], ligand_atom['z']]
        }
    }
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    print("\n" + "="*60)
    
    return 0 if result['valid'] else 1


if __name__ == "__main__":
    exit(main())
