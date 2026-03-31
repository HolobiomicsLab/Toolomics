# Covalent Docking 8-Step Workflow Guide

This document provides the complete 8-step protocol for covalent docking campaigns.

## Overview

The 8-step workflow ensures reproducible, validated covalent docking results:

1. **Ligand Preparation** - SMILES → 3D → optimized → final-form
2. **Reactive Residue Identification** - Locate target nucleophile
3. **Attachment Point Definition** - Define warhead attachment SMARTS
4. **Covalent Docking** - Run GNINA with multi-seed
5. **Geometry Validation** - Verify covalent bond feasibility
6. **Contact Analysis** - Map protein-ligand interactions
7. **Reproducibility Assessment** - Evaluate pose stability
8. **Visualization** - Generate PyMOL scripts

---

## Step 1: Ligand Preparation

### Purpose
Convert SMILES to dockable 3D structure with proper warhead geometry.

### Process

```python
# Full workflow: SMILES → 3D conformer → xtb optimization → tail removal → validation

import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

def prepare_ligand(smiles: str, warhead_type: str, output: str):
    """
    Prepare ligand for covalent docking.
    
    Args:
        smiles: SMILES of full molecule (including leaving group)
        warhead_type: Type of covalent warhead
        output: Output SDF file path
    """
    # 1. Generate 3D conformer
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    AllChem.MMFFOptimizeMolecule(mol)
    
    # 2. XTB geometry optimization
    Chem.MolToMolFile(mol, "temp_3d.mol")
    subprocess.run(["xtb", "temp_3d.mol", "--opt", "--o", "xtb_output"])
    
    # 3. Remove leaving group (based on warhead type)
    final_mol = remove_leaving_group(mol, warhead_type)
    
    # 4. Validate attachment atom
    validate_attachment_atom(final_mol, warhead_type)
    
    # 5. Save final ligand
    Chem.MolToMolFile(final_mol, output)
    
    return final_mol
```

### Warhead-Specific Tail Removal

```python
WARHEAD_CONFIG = {
    "alkyne_se": {
        "leaving_group_smarts": "[N;$(NC=O)]",  # Leaving group
        "attachment_smarts": "[CD1]",  # Terminal alkyne carbon
        "tail_replacement": "H"  # Replace with H after removal
    },
    "acrylamide_cys": {
        "leaving_group_smarts": "[N;$(NC(=O)C=C)]",
        "attachment_smarts": "[C;$(C=C-C(=O)N)]",
        "tail_replacement": "H"
    },
    "epoxide_cys": {
        "leaving_group_smarts": "[O;R1]",  # Epoxide oxygen
        "attachment_smarts": "[C;R1]",
        "tail_replacement": None  # Ring opening
    },
    "haloacetamide_cys": {
        "leaving_group_smarts": "[Cl,Br,I]",
        "attachment_smarts": "[C;$(C-[Cl,Br,I])]",
        "tail_replacement": "H"
    }
}
```

### Output Validation

- Verify attachment atom exists
- Check molecular weight (< 1000 Da preferred)
- Confirm no clashes in initial conformer

---

## Step 2: Reactive Residue Identification

### Purpose
Locate the nucleophilic residue that will form the covalent bond.

### Manual Identification

1. **Inspect PDB structure**
   ```bash
   grep -E "^ATOM|^HETATM" protein.pdb | grep -E "CYS|SEC|LYS|SER|TYR"
   ```

2. **Check for catalytic residues**
   - Look for residue in active site
   - Check B-factor (lower = more rigid)
   - Verify accessibility (not buried)

### Automated Detection

```python
def find_reactive_residues(pdb_file: str, residue_type: str = "CYS") -> list:
    """
    Find potential reactive residues.
    
    Returns list of dicts with:
        - chain: Chain ID
        - resnum: Residue number
        - atom_name: Atom name (SG for Cys, SEG for SeCys, NZ for Lys)
        - accessibility: Solvent accessibility score
    """
    from Bio.PDB import PDBParser, SASA
    
    parser = PDBParser()
    structure = parser.get_structure("protein", pdb_file)
    
    reactive = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.get_resname() == residue_type:
                    # Check accessibility
                    accessibility = calculate_sasa(residue)
                    if accessibility > 10.0:  # Accessible threshold
                        atom_name = get_reactive_atom(residue_type)
                        reactive.append({
                            "chain": chain.id,
                            "resnum": residue.get_id()[1],
                            "atom_name": atom_name,
                            "accessibility": accessibility
                        })
    
    return reactive

REACTIVE_ATOMS = {
    "CYS": "SG",    # Thiol sulfur
    "SEC": "SEG",   # Selenol selenium
    "LYS": "NZ",    # Amino nitrogen
    "SER": "OG",    # Hydroxyl oxygen
    "TYR": "OH"     # Phenolic oxygen
}
```

### Format Specification

Receptor atom format: `"chain:resnum:atom_name"`

Examples:
- `"A:46:SEG"` - Chain A, residue 46, selenium atom (SeCys)
- `"B:156:SG"` - Chain B, residue 156, sulfur atom (Cys)
- `"A:73:NZ"` - Chain A, residue 73, nitrogen atom (Lys)

---

## Step 3: Attachment Point Definition

### Purpose
Define SMARTS pattern for the ligand atom that forms the covalent bond.

### Common Attachment SMARTS

```python
ATTACHMENT_PATTERNS = {
    # Alkyne - terminal carbon
    "alkyne_terminal": "[CD1]",
    
    # Acrylamide - beta carbon (Michael acceptor)
    "acrylamide_beta": "[C;$(C=C-C(=O)N)]",
    
    # Epoxide - ring carbon
    "epoxide_carbon": "[C;R1]",
    
    # Haloacetamide - carbon attached to halogen
    "haloacetamide_alpha": "[C;$(C-[Cl,Br,I])]",
    
    # Vinyl sulfone - beta carbon
    "vinyl_sulfone_beta": "[C;$(C=C-S(=O)(=O))]",
    
    # Nitrile - carbon of nitrile group
    "nitrile_carbon": "[C;$(C#N)]"
}
```

### SMARTS Validation

```python
def validate_attachment_smarts(mol, smarts: str) -> bool:
    """Check if SMARTS pattern matches exactly one atom in molecule."""
    from rdkit import Chem
    
    pattern = Chem.MolFromSmarts(smarts)
    matches = mol.GetSubstructMatches(pattern)
    
    if len(matches) == 0:
        raise ValueError(f"SMARTS pattern '{smarts}' matches no atoms")
    elif len(matches) > 1:
        raise ValueError(f"SMARTS pattern '{smarts}' matches multiple atoms: {len(matches)}")
    
    return True
```

---

## Step 4: Covalent Docking

### Purpose
Run GNINA covalent docking with multi-seed for reproducibility.

### Basic Command

```bash
gnina \
  --receptor protein.pdb \
  --ligand ligand_prepared.sdf \
  --covalent A:46:SEG \
  --cov_atom "[CD1]" \
  --covalent_optimize \
  --out docked_poses.sdf
```

### Multi-Seed Reproducibility Script

```python
import subprocess
import json
from pathlib import Path

def dock_covalent_multi_seed(
    ligand_sdf: str,
    receptor_pdb: str,
    receptor_atom: str,
    attachment_smarts: str,
    seeds: list = [0, 42, 123],
    num_modes: int = 5,
    output_dir: str = "docking_results"
):
    """
    Run covalent docking with multiple seeds.
    
    Returns dict with results per seed and reproducibility statistics.
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    results = {
        "seeds": seeds,
        "poses_by_seed": {},
        "best_affinity_by_seed": {},
        "reproducibility_stats": {}
    }
    
    for seed in seeds:
        output_file = f"{output_dir}/seed_{seed}.sdf"
        
        cmd = [
            "gnina",
            "--receptor", receptor_pdb,
            "--ligand", ligand_sdf,
            "--covalent", receptor_atom,
            "--cov_atom", attachment_smarts,
            "--covalent_optimize",
            "--seed", str(seed),
            "--num_modes", str(num_modes),
            "--out", output_file
        ]
        
        subprocess.run(cmd, check=True)
        
        # Parse results
        poses = parse_gnina_output(output_file)
        results["poses_by_seed"][seed] = poses
        results["best_affinity_by_seed"][seed] = poses[0]["affinity"] if poses else None
    
    # Calculate reproducibility statistics
    affinities = list(results["best_affinity_by_seed"].values())
    results["reproducibility_stats"] = {
        "mean": sum(affinities) / len(affinities),
        "std": statistics.stdev(affinities),
        "min": min(affinities),
        "max": max(affinities),
        "range": max(affinities) - min(affinities)
    }
    
    return results
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--covalent` | Required | Receptor atom (chain:resnum:atom) |
| `--cov_atom` | Required | Ligand attachment SMARTS |
| `--covalent_optimize` | Off | Enable UFF optimization of covalent complex |
| `--num_modes` | 9 | Number of poses to generate |
| `--seed` | Random | Random seed for reproducibility |
| `--cnn_scoring` | none | Use "none" for covalent (CNN not trained for covalent) |

---

## Step 5: Geometry Validation

### Purpose
Verify covalent bond is chemically reasonable.

### Implementation

```python
def validate_covalent_geometry(
    docked_pdb: str,
    receptor_pdb: str,
    receptor_atom_spec: str,
    expected_bond_type: str = "C-Se",
    tolerance: float = 0.1
) -> dict:
    """
    Validate covalent bond geometry.
    
    Returns dict with:
        - distance: measured bond length
        - expected_range: (min, max) for bond type
        - is_valid: bool
        - assessment: str (optimal/acceptable/poor)
    """
    BOND_LENGTHS = {
        "C-Se": (1.85, 2.05),
        "C-S": (1.75, 1.95),
        "C-N": (1.40, 1.55),
        "C-O": (1.40, 1.50)
    }
    
    # Parse receptor atom
    chain, resnum, atom_name = receptor_atom_spec.split(":")
    resnum = int(resnum)
    
    # Load structures
    receptor_coords = parse_pdb_atom(receptor_pdb, chain, resnum, atom_name)
    ligand_coords = find_ligand_attachment_atom(docked_pdb)
    
    # Calculate distance
    distance = np.linalg.norm(receptor_coords - ligand_coords)
    
    # Validate
    expected_min, expected_max = BOND_LENGTHS[expected_bond_type]
    
    if expected_min - tolerance <= distance <= expected_max + tolerance:
        assessment = "optimal" if expected_min <= distance <= expected_max else "acceptable"
        is_valid = True
    else:
        assessment = "poor"
        is_valid = False
    
    return {
        "distance": distance,
        "expected_min": expected_min,
        "expected_max": expected_max,
        "is_valid": is_valid,
        "assessment": assessment
    }
```

### Validation Output

```json
{
  "distance": 1.94,
  "expected_min": 1.85,
  "expected_max": 2.05,
  "is_valid": true,
  "assessment": "optimal",
  "receptor_atom": {
    "chain": "A",
    "resnum": 46,
    "atom_name": "SEG",
    "coordinates": [12.34, 5.67, 8.90]
  },
  "ligand_attachment_atom": {
    "atom_name": "C1",
    "coordinates": [14.28, 5.45, 9.12]
  }
}
```

---

## Step 6: Contact Analysis

### Purpose
Map protein-ligand interactions to guide design.

### Contact Types

```python
CONTACT_CUTOFFS = {
    "hydrophobic": 4.5,    # Carbon-carbon distance
    "hbond_donor": 3.5,    # H-bond donor to acceptor
    "hbond_acceptor": 3.5, # H-bond acceptor to donor
    "aromatic": 5.0,       # Aromatic ring centroid distance
    "ionic": 4.0,          # Charged group distance
    "repulsive": 3.0       # Too close (clash)
}

def analyze_contacts(docked_pdb: str, receptor_pdb: str, cutoff: float = 5.0) -> dict:
    """
    Analyze all protein-ligand contacts.
    
    Returns dict organized by contact type and residue.
    """
    contacts = {
        "hydrophobic": [],
        "hydrogen_bonds": [],
        "aromatic": [],
        "ionic": [],
        "repulsive": []
    }
    
    # Load structures
    receptor = parse_pdb(receptor_pdb)
    ligand = parse_pdb(docked_pdb, hetatm_only=True)
    
    # Analyze each ligand atom
    for latom in ligand.atoms:
        for ratom in receptor.atoms:
            distance = np.linalg.norm(latom.coord - ratom.coord)
            
            if distance > cutoff:
                continue
            
            # Classify contact
            contact_type = classify_contact(latom, ratom, distance)
            
            if contact_type:
                contacts[contact_type].append({
                    "ligand_atom": latom.name,
                    "residue": f"{ratom.res_name} {ratom.res_num}",
                    "receptor_atom": ratom.name,
                    "distance": round(distance, 2)
                })
    
    return contacts
```

### Key Residues to Monitor

From 6ELW-Se campaign, critical residues:
- **TRP 136**: Hydrophobic pocket (24 contacts in champion)
- **PHE 140**: π-stacking opportunities
- **HIS 143**: H-bond donor/acceptor
- **ALA 145**: Hydrophobic contact

---

## Step 7: Reproducibility Assessment

### Purpose
Evaluate pose stability across random seeds.

### Statistics

```python
def analyze_reproducibility(poses_by_seed: dict) -> dict:
    """
    Analyze docking reproducibility across seeds.
    
    Returns dict with statistical analysis.
    """
    import statistics
    
    best_affinities = [poses[0]["affinity"] for poses in poses_by_seed.values()]
    
    analysis = {
        "mean_affinity": statistics.mean(best_affinities),
        "std_affinity": statistics.stdev(best_affinities),
        "min_affinity": min(best_affinities),
        "max_affinity": max(best_affinities),
        "range": max(best_affinities) - min(best_affinities),
        "best_seed": min(poses_by_seed.keys(), 
                        key=lambda s: poses_by_seed[s][0]["affinity"]),
        "recommendation": ""
    }
    
    # Generate recommendation
    std = analysis["std_affinity"]
    if std < 0.5:
        analysis["recommendation"] = "Excellent reproducibility. Results highly reliable."
        analysis["reliability"] = "high"
    elif std < 1.0:
        analysis["recommendation"] = "Good reproducibility. Results reliable."
        analysis["reliability"] = "good"
    elif std < 1.5:
        analysis["recommendation"] = "Moderate reproducibility. Consider more sampling."
        analysis["reliability"] = "moderate"
    else:
        analysis["recommendation"] = "Poor reproducibility. Results uncertain. Increase seeds or check system."
        analysis["reliability"] = "poor"
    
    return analysis
```

### Interpretation

| σ (kcal/mol) | Assessment | Action |
|--------------|------------|--------|
| < 0.5 | Excellent | Proceed with confidence |
| 0.5 - 1.0 | Good | Standard reliability |
| 1.0 - 1.5 | Moderate | Consider increasing num_modes |
| > 1.5 | Poor | System may be too flexible; check preparation |

---

## Step 8: Visualization

### Purpose
Generate PyMOL scripts for structure analysis.

### PyMOL Script Generation

```python
def generate_pymol_script(
    docked_pdb: str,
    receptor_pdb: str,
    receptor_atom_spec: str,
    output_path: str,
    ligand_name: str = "ligand"
):
    """Generate PyMOL visualization script."""
    
    chain, resnum, atom_name = receptor_atom_spec.split(":")
    
    script = f'''
# Load structures
load {receptor_pdb}, receptor
load {docked_pdb}, {ligand_name}

# Display settings
set cartoon_fancy_helices, 1
set cartoon_fancy_sheets, 1
set sphere_scale, 0.3

# Color receptor
color gray70, receptor

# Color ligand by element
color cyan, {ligand_name} and elem C
color red, {ligand_name} and elem O
color blue, {ligand_name} and elem N

# Highlight reactive residue
select reactive_res, receptor and chain {chain} and resi {resnum}
show sticks, reactive_res
color orange, reactive_res

# Show covalent bond as distance
select ligand_atom, {ligand_name} and name C1
select receptor_atom, receptor and chain {chain} and resi {resnum} and name {atom_name}
distance covalent_bond, ligand_atom, receptor_atom
set dash_color, yellow, covalent_bond
set dash_width, 3

# Show surrounding residues within 5A
select pocket, byres (receptor within 5 of {ligand_name})
show sticks, pocket
color lime, pocket and elem C

# Ligand representation
show sticks, {ligand_name}
show spheres, {ligand_name}

# Labels
label reactive_res and name CA, "%s-%s" % (resn, resi)

# Center view
zoom {ligand_name}

# Save session
save session.pse
'''
    
    with open(output_path, 'w') as f:
        f.write(script)
    
    return output_path
```

---

## Complete Example

```python
#!/usr/bin/env python3
"""Complete 8-step covalent docking workflow."""

import subprocess
import json

def main():
    # Configuration
    config = {
        "smiles": "CC#CCOc1ccc(C(=O)NCC(N)=O)nn1",
        "receptor": "6ELW-Se.pdb",
        "receptor_atom": "A:46:SEG",
        "attachment_smarts": "[CD1]",
        "warhead_type": "alkyne_se",
        "seeds": [0, 42, 123],
        "num_modes": 5
    }
    
    print("=" * 60)
    print("COVALENT DOCKING 8-STEP WORKFLOW")
    print("=" * 60)
    
    # Step 1: Ligand Preparation
    print("\n[1/8] Preparing ligand...")
    subprocess.run([
        "python", "scripts/prepare_ligand.py",
        "--smiles", config["smiles"],
        "--warhead", config["warhead_type"],
        "--output", "ligand_prepared.sdf"
    ])
    
    # Step 2-4: Docking
    print("\n[2-4/8] Running covalent docking...")
    result = dock_covalent_multi_seed(
        ligand_sdf="ligand_prepared.sdf",
        receptor_pdb=config["receptor"],
        receptor_atom=config["receptor_atom"],
        attachment_smarts=config["attachment_smarts"],
        seeds=config["seeds"],
        num_modes=config["num_modes"]
    )
    
    # Step 5: Geometry Validation
    print("\n[5/8] Validating geometry...")
    geom = validate_covalent_geometry(
        docked_pdb="docking_results/seed_0.sdf",
        receptor_pdb=config["receptor"],
        receptor_atom_spec=config["receptor_atom"],
        expected_bond_type="C-Se"
    )
    print(f"  Bond distance: {geom['distance']:.2f} Å ({geom['assessment']})")
    
    # Step 6: Contact Analysis
    print("\n[6/8] Analyzing contacts...")
    contacts = analyze_contacts(
        docked_pdb="docking_results/seed_0.sdf",
        receptor_pdb=config["receptor"]
    )
    print(f"  Hydrophobic: {len(contacts['hydrophobic'])}")
    print(f"  H-bonds: {len(contacts['hydrogen_bonds'])}")
    
    # Step 7: Reproducibility
    print("\n[7/8] Assessing reproducibility...")
    repro = analyze_reproducibility(result["poses_by_seed"])
    print(f"  σ = {repro['std_affinity']:.2f} kcal/mol ({repro['reliability']})")
    
    # Step 8: Visualization
    print("\n[8/8] Generating visualization...")
    generate_pymol_script(
        docked_pdb="docking_results/seed_0.sdf",
        receptor_pdb=config["receptor"],
        receptor_atom_spec=config["receptor_atom"],
        output_path="visualize.pml"
    )
    
    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print(f"Best affinity: {repro['min_affinity']:.2f} kcal/mol")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## Decision Tree

```
Start
  │
  ▼
Prepare Ligand
  │
  ├──► Fails? ──► Check SMILES / Warhead type
  │
  ▼
Dock (Multi-seed)
  │
  ├──► No poses? ──► Check receptor atom / SMARTS
  │
  ▼
Validate Geometry
  │
  ├──► Poor? ──► Try different attachment SMARTS
  │
  ▼
Analyze Contacts
  │
  ▼
Check Reproducibility
  │
  ├──► σ > 1.5? ──► Increase num_modes / Check system
  │
  ▼
Results Reliable?
  │
  ├──► No ──► Iterate with analogs
  │
  ▼
Yes → Generate analogs / Proceed
```
