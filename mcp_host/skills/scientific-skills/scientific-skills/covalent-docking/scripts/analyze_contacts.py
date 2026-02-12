#!/usr/bin/env python3
"""
Analyze protein-ligand contacts in docked poses.

Identifies hydrogen bonds, hydrophobic contacts, aromatic interactions, and ionic contacts.
"""

import argparse
import json
import numpy as np
from collections import defaultdict


def parse_pdb(pdb_file: str, hetatm_only: bool = False) -> list:
    """Parse PDB file and return list of atoms."""
    atoms = []
    
    with open(pdb_file) as f:
        for line in f:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            
            if hetatm_only and not line.startswith("HETATM"):
                continue
            
            atom = {
                "record": line[0:6].strip(),
                "atom_num": int(line[6:11]),
                "atom_name": line[12:16].strip(),
                "res_name": line[17:20].strip(),
                "chain": line[21],
                "res_num": int(line[22:26]),
                "x": float(line[30:38]),
                "y": float(line[38:46]),
                "z": float(line[46:54]),
                "element": line[76:78].strip() if len(line) > 76 else line[12:16].strip()[0]
            }
            atoms.append(atom)
    
    return atoms


def calculate_distance(atom1: dict, atom2: dict) -> float:
    """Calculate distance between two atoms."""
    coord1 = np.array([atom1["x"], atom1["y"], atom1["z"]])
    coord2 = np.array([atom2["x"], atom2["y"], atom2["z"]])
    return np.linalg.norm(coord1 - coord2)


def is_hydrophobic(atom: dict) -> bool:
    """Check if atom is hydrophobic."""
    # Carbon atoms (except carbonyl) are hydrophobic
    if atom["element"] == "C":
        # Check if it's a carbonyl carbon
        if atom["atom_name"].startswith("C") and "O" in atom["res_name"]:
            return False
        return True
    return False


def is_hbond_donor(atom: dict) -> bool:
    """Check if atom is H-bond donor."""
    # N-H or O-H groups
    if atom["element"] in ["N", "O"]:
        return True
    return False


def is_hbond_acceptor(atom: dict) -> bool:
    """Check if atom is H-bond acceptor."""
    # Lone pair bearing atoms
    if atom["element"] in ["N", "O"]:
        return True
    return False


def is_aromatic(atom: dict) -> bool:
    """Check if atom is part of aromatic system."""
    aromatic_residues = ["PHE", "TYR", "TRP", "HIS"]
    return atom["res_name"] in aromatic_residues and atom["element"] == "C"


def is_charged(atom: dict) -> bool:
    """Check if atom is charged."""
    # Simplified - would need proper charge assignment
    charged_atoms = {
        "ASP": ["OD1", "OD2"],
        "GLU": ["OE1", "OE2"],
        "LYS": ["NZ"],
        "ARG": ["NH1", "NH2"],
        "HIS": ["ND1", "NE2"]
    }
    
    if atom["res_name"] in charged_atoms:
        return atom["atom_name"] in charged_atoms[atom["res_name"]]
    return False


def classify_contact(ligand_atom: dict, receptor_atom: dict, distance: float) -> str:
    """Classify the type of contact."""
    
    # Repulsive/Clash
    if distance < 2.5:
        return "repulsive"
    
    # Hydrophobic
    if is_hydrophobic(ligand_atom) and is_hydrophobic(receptor_atom):
        if distance < 4.5:
            return "hydrophobic"
    
    # Hydrogen bond
    if distance < 3.5:
        if is_hbond_donor(ligand_atom) and is_hbond_acceptor(receptor_atom):
            return "hydrogen_bond"
        if is_hbond_acceptor(ligand_atom) and is_hbond_donor(receptor_atom):
            return "hydrogen_bond"
    
    # Aromatic
    if is_aromatic(ligand_atom) and is_aromatic(receptor_atom):
        if distance < 5.0:
            return "aromatic"
    
    # Ionic
    if is_charged(ligand_atom) and is_charged(receptor_atom):
        if distance < 4.0:
            return "ionic"
    
    return None


def analyze_contacts(docked_pdb: str, receptor_pdb: str, cutoff: float = 5.0) -> dict:
    """Analyze all protein-ligand contacts."""
    
    # Load structures
    receptor_atoms = parse_pdb(receptor_pdb)
    ligand_atoms = parse_pdb(docked_pdb, hetatm_only=True)
    
    if not ligand_atoms:
        print("Warning: No HETATM records found in docked file")
        ligand_atoms = parse_pdb(docked_pdb)
    
    # Initialize contact storage
    contacts = {
        "hydrophobic": [],
        "hydrogen_bond": [],
        "aromatic": [],
        "ionic": [],
        "repulsive": [],
        "all": []
    }
    
    # Analyze contacts
    for latom in ligand_atoms:
        for ratom in receptor_atoms:
            distance = calculate_distance(latom, ratom)
            
            if distance > cutoff:
                continue
            
            contact_type = classify_contact(latom, ratom, distance)
            
            contact_info = {
                "ligand_atom": latom["atom_name"],
                "receptor_residue": f"{ratom['res_name']} {ratom['res_num']}",
                "receptor_atom": ratom["atom_name"],
                "distance": round(distance, 2),
                "type": contact_type
            }
            
            contacts["all"].append(contact_info)
            
            if contact_type:
                contacts[contact_type].append(contact_info)
    
    return contacts


def summarize_by_residue(contacts: dict) -> dict:
    """Summarize contacts by receptor residue."""
    residue_contacts = defaultdict(lambda: defaultdict(int))
    
    for contact in contacts["all"]:
        residue = contact["receptor_residue"]
        ctype = contact["type"] or "other"
        residue_contacts[residue][ctype] += 1
    
    return dict(residue_contacts)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze protein-ligand contacts"
    )
    parser.add_argument("--docked", required=True,
                       help="Docked pose PDB file")
    parser.add_argument("--receptor", required=True,
                       help="Receptor PDB file")
    parser.add_argument("--cutoff", type=float, default=5.0,
                       help="Distance cutoff in Angstroms")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--summary", action="store_true",
                       help="Print summary only")
    
    args = parser.parse_args()
    
    print("="*60)
    print("CONTACT ANALYSIS")
    print("="*60)
    print(f"\nDocked file: {args.docked}")
    print(f"Receptor file: {args.receptor}")
    print(f"Distance cutoff: {args.cutoff} Å")
    
    # Analyze contacts
    contacts = analyze_contacts(args.docked, args.receptor, args.cutoff)
    
    # Print summary
    print("\n" + "-"*60)
    print("CONTACT SUMMARY")
    print("-"*60)
    print(f"\nTotal contacts within {args.cutoff} Å: {len(contacts['all'])}")
    print(f"\nBy type:")
    print(f"  Hydrophobic:    {len(contacts['hydrophobic']):3d}")
    print(f"  H-bonds:        {len(contacts['hydrogen_bond']):3d}")
    print(f"  Aromatic:       {len(contacts['aromatic']):3d}")
    print(f"  Ionic:          {len(contacts['ionic']):3d}")
    print(f"  Repulsive:      {len(contacts['repulsive']):3d}")
    
    # Summarize by residue
    by_residue = summarize_by_residue(contacts)
    
    print("\n" + "-"*60)
    print("TOP RESIDUES BY CONTACT COUNT")
    print("-"*60)
    
    sorted_residues = sorted(
        by_residue.items(),
        key=lambda x: sum(x[1].values()),
        reverse=True
    )[:10]
    
    for residue, types in sorted_residues:
        total = sum(types.values())
        type_str = ", ".join([f"{k}:{v}" for k, v in types.items()])
        print(f"  {residue:15s} {total:3d} contacts ({type_str})")
    
    # Detailed list if not summary mode
    if not args.summary and contacts['all']:
        print("\n" + "-"*60)
        print("DETAILED CONTACT LIST (first 20)")
        print("-"*60)
        print(f"{'Ligand':<10} {'Residue':<15} {'Atom':<6} {'Dist':<6} {'Type'}")
        print("-"*60)
        
        for c in contacts['all'][:20]:
            print(f"{c['ligand_atom']:<10} {c['receptor_residue']:<15} "
                  f"{c['receptor_atom']:<6} {c['distance']:<6.2f} {c['type'] or 'other'}")
    
    # Prepare output
    output = {
        "cutoff": args.cutoff,
        "summary": {
            "total_contacts": len(contacts['all']),
            "hydrophobic": len(contacts['hydrophobic']),
            "hydrogen_bonds": len(contacts['hydrogen_bond']),
            "aromatic": len(contacts['aromatic']),
            "ionic": len(contacts['ionic']),
            "repulsive": len(contacts['repulsive'])
        },
        "by_residue": by_residue,
        "contacts": contacts['all'] if not args.summary else None
    }
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    print("\n" + "="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
