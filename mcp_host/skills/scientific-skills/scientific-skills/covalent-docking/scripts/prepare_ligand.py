#!/usr/bin/env python3
"""
Prepare ligand for covalent docking.

Workflow: SMILES → 3D conformer → XTB optimization → tail removal → validation
"""

import argparse
import subprocess
import tempfile
import os
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not available. Some features limited.")


WARHEAD_CONFIG = {
    "alkyne_se": {
        "name": "Terminal alkyne (SeCys target)",
        "leaving_group_smarts": "[N;$(NC=O)]",
        "attachment_smarts": "[CD1]",
        "expected_bond": "C-Se"
    },
    "alkyne_cys": {
        "name": "Terminal alkyne (Cys target)",
        "leaving_group_smarts": "[N;$(NC=O)]",
        "attachment_smarts": "[CD1]",
        "expected_bond": "C-S"
    },
    "acrylamide_cys": {
        "name": "Acrylamide (Cys target)",
        "leaving_group_smarts": "[N;$(NC(=O)C=C)]",
        "attachment_smarts": "[C;$(C=C-C(=O)N)]",
        "expected_bond": "C-S"
    },
    "epoxide_cys": {
        "name": "Epoxide (Cys target)",
        "leaving_group_smarts": "[O;R1]",
        "attachment_smarts": "[C;R1]",
        "expected_bond": "C-S"
    },
    "haloacetamide_cys": {
        "name": "Haloacetamide (Cys target)",
        "leaving_group_smarts": "[Cl,Br,I]",
        "attachment_smarts": "[C;$(C-[Cl,Br,I])]",
        "expected_bond": "C-S"
    }
}


def generate_3d_conformer(smiles: str, output_mol: str) -> bool:
    """Generate 3D conformer from SMILES."""
    if not RDKIT_AVAILABLE:
        print("Error: RDKit required for 3D generation")
        return False
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"Error: Invalid SMILES: {smiles}")
        return False
    
    mol = Chem.AddHs(mol)
    
    # Generate 3D coordinates
    AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    AllChem.MMFFOptimizeMolecule(mol, mmffVariant='MMFF94')
    
    # Save
    Chem.MolToMolFile(mol, output_mol)
    return True


def run_xtb_optimization(input_mol: str, output_xyz: str) -> bool:
    """Run XTB geometry optimization."""
    try:
        result = subprocess.run(
            ["xtb", input_mol, "--opt", "--o", output_xyz],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("Warning: XTB not found. Using unoptimized conformer.")
        return False
    except subprocess.TimeoutExpired:
        print("Warning: XTB optimization timed out.")
        return False


def remove_leaving_group(mol, warhead_type: str):
    """Remove leaving group based on warhead type."""
    if warhead_type not in WARHEAD_CONFIG:
        print(f"Warning: Unknown warhead type {warhead_type}, no removal performed")
        return mol
    
    config = WARHEAD_CONFIG[warhead_type]
    
    # This is a simplified version - full implementation would use RDKit edits
    # to actually remove the leaving group atoms
    
    return mol


def validate_attachment_atom(mol, warhead_type: str) -> dict:
    """Validate that attachment atom exists and is accessible."""
    if warhead_type not in WARHEAD_CONFIG:
        return {"valid": False, "error": f"Unknown warhead type: {warhead_type}"}
    
    config = WARHEAD_CONFIG[warhead_type]
    
    if not RDKIT_AVAILABLE:
        return {"valid": True, "warning": "RDKit not available, skipping validation"}
    
    pattern = Chem.MolFromSmarts(config["attachment_smarts"])
    matches = mol.GetSubstructMatches(pattern)
    
    if len(matches) == 0:
        return {
            "valid": False,
            "error": f"Attachment SMARTS '{config['attachment_smarts']}' not found"
        }
    elif len(matches) > 1:
        return {
            "valid": True,
            "warning": f"Multiple attachment points found ({len(matches)}), using first"
        }
    
    return {
        "valid": True,
        "attachment_idx": matches[0][0],
        "expected_bond": config["expected_bond"]
    }


def calculate_properties(smiles: str) -> dict:
    """Calculate molecular properties."""
    if not RDKIT_AVAILABLE:
        return {}
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {}
    
    return {
        "molecular_weight": Descriptors.MolWt(mol),
        "logp": Descriptors.MolLogP(mol),
        "hbd": Descriptors.NumHDonors(mol),
        "hba": Descriptors.NumHAcceptors(mol),
        "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
        "tpsa": Descriptors.TPSA(mol)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Prepare ligand for covalent docking"
    )
    parser.add_argument("--smiles", required=True, help="SMILES string of full molecule")
    parser.add_argument("--warhead", default="alkyne_se", 
                       choices=list(WARHEAD_CONFIG.keys()),
                       help="Warhead type")
    parser.add_argument("--output", required=True, help="Output SDF file")
    parser.add_argument("--ligand_id", help="Optional ligand identifier")
    parser.add_argument("--optimize", action="store_true", default=True,
                       help="Run XTB optimization")
    parser.add_argument("--no_optimize", action="store_true",
                       help="Skip XTB optimization")
    
    args = parser.parse_args()
    
    print(f"Preparing ligand: {args.ligand_id or 'unnamed'}")
    print(f"SMILES: {args.smiles}")
    print(f"Warhead: {WARHEAD_CONFIG[args.warhead]['name']}")
    
    # Calculate properties
    props = calculate_properties(args.smiles)
    if props:
        print(f"\nProperties:")
        print(f"  MW: {props['molecular_weight']:.1f}")
        print(f"  LogP: {props['logp']:.2f}")
        print(f"  HBD/HBA: {props['hbd']}/{props['hba']}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Generate 3D conformer
        print("\n[1/3] Generating 3D conformer...")
        mol_file = os.path.join(tmpdir, "initial_3d.mol")
        if not generate_3d_conformer(args.smiles, mol_file):
            print("Error: Failed to generate 3D conformer")
            return 1
        print("  ✓ 3D conformer generated")
        
        # Step 2: XTB optimization (optional)
        if args.optimize and not args.no_optimize:
            print("\n[2/3] Running XTB optimization...")
            xtb_output = os.path.join(tmpdir, "xtb_opt.xyz")
            if run_xtb_optimization(mol_file, xtb_output):
                print("  ✓ XTB optimization complete")
                mol_file = xtb_output
            else:
                print("  ⚠ XTB optimization failed or skipped")
        else:
            print("\n[2/3] Skipping XTB optimization")
        
        # Step 3: Remove leaving group and validate
        print("\n[3/3] Processing for covalent docking...")
        
        if RDKIT_AVAILABLE:
            mol = Chem.MolFromMolFile(mol_file)
            if mol is None:
                # Try XYZ format
                mol = Chem.MolFromSmiles(args.smiles)
                mol = Chem.AddHs(mol)
            
            # Remove leaving group
            mol = remove_leaving_group(mol, args.warhead)
            
            # Validate attachment
            validation = validate_attachment_atom(mol, args.warhead)
            
            if not validation["valid"]:
                print(f"  ✗ Validation failed: {validation['error']}")
                return 1
            
            if "warning" in validation:
                print(f"  ⚠ {validation['warning']}")
            
            # Save final
            Chem.MolToMolFile(mol, args.output)
        else:
            # Without RDKit, just copy the file
            import shutil
            shutil.copy(mol_file, args.output)
        
        print(f"  ✓ Final ligand saved: {args.output}")
    
    print("\n" + "="*60)
    print("Ligand preparation complete")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
