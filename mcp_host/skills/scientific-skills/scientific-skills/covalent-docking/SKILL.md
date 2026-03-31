---
name: covalent-docking
description: Covalent molecular docking for irreversible inhibitor design. Dock ligands with warheads to protein reactive residues (Cys, SeCys, Lys, Ser, Tyr). Multi-seed reproducibility assessment, contact analysis, de novo design workflows.
license: MIT license
metadata:
    skill-author: HolobiomicsLab
---

# Covalent Docking: Design of Irreversible Inhibitors

## Overview

Covalent docking predicts the binding poses of irreversible inhibitors that form covalent bonds with protein nucleophiles. Unlike non-covalent docking, it requires modeling the covalent attachment chemistry, bond geometry validation, and specialized scoring considerations.

**Core Capabilities:**
- Prepare ligands with covalent warheads (alkyne, acrylamide, epoxide, haloacetamide)
- Dock to reactive residues (Cys, SeCys, Lys, Ser, Tyr)
- Validate covalent bond geometry (bond lengths, angles)
- Analyze protein-ligand contacts (hydrophobic, H-bond, ionic)
- Assess docking reproducibility with multi-seed analysis
- Generate analogs via rule-based mutations and genetic algorithms

**Key Distinction:** Covalent docking predicts **covalent complex structures** with **bond formation**, NOT just binding poses. Requires validation of chemical feasibility alongside structural complementarity.

## When to Use This Skill

This skill should be used when:

- "Design covalent inhibitors" or "irreversible inhibitors"
- "Dock alkyne/acrylamide warhead to cysteine"
- Targeting specific reactive residues in kinases, proteases, or other enzymes
- Optimizing covalent ligands for affinity and selectivity
- "Generate analogs of covalent inhibitor" or "SAR exploration"
- Analyzing protein-ligand contacts for covalent complexes
- Tasks involving PDB files + SMILES with warhead functional groups

**Not for:** Non-covalent docking (use DiffDock or GNINA standard mode), reversible covalent inhibitors (requires different approach), metalloprotein covalent docking.

## Prerequisites

### Required Software

```bash
# GNINA (covalent docking support)
gnina --version  # Requires covalent docking build

# XTB (geometry optimization)
xtb --version

# RDKit (ligand preparation)
python -c "import rdkit; print(rdkit.__version__)"

# OpenFF (force field parameterization)
python -c "import openff; print(openff.__version__)"
```

### Receptor Preparation

Prepare receptor with reactive residue properly labeled:

```bash
# For selenocysteine (SeCys) - use SEG as residue name
# PDB format: HETATM records with Se instead of S

# Example reactive atom specification:
# Chain A, Residue 46, Atom SEG → "A:46:SEG"
```

## Core Workflows

### Workflow 1: Single Covalent Docking (8-Step Protocol)

**Standard workflow for docking one ligand to one receptor:**

```python
import subprocess
import json

# Step 1: Prepare ligand (SMILES → 3D → optimized → final-form)
subprocess.run([
    "python", "scripts/prepare_ligand.py",
    "--smiles", "CC#CCOc1ccc(C(=O)NCC(N)=O)nn1",  # Full molecule with leaving group
    "--warhead", "alkyne_se",
    "--output", "ligand_prepared.sdf"
])

# Step 2: Identify reactive residue
# Manual or automated detection of Cys/SeCys/Lys/Ser/Tyr
receptor_atom = "A:46:SEG"  # Format: chain:resnum:atom_name

# Step 3: Define attachment SMARTS
# For terminal alkyne: [CD1] (terminal carbon)
# For acrylamide: [C;$(C=C-C(=O)N)] (beta carbon)
attachment_smarts = "[CD1]"

# Step 4: Run covalent docking with multi-seed reproducibility
subprocess.run([
    "gnina",
    "--receptor", "protein.pdb",
    "--ligand", "ligand_prepared.sdf",
    "--covalent", receptor_atom,
    "--cov_atom", attachment_smarts,
    "--covalent_optimize",
    "--seed", "0", "--seed", "42", "--seed", "123",  # Multi-seed
    "--num_modes", "5",
    "--out", "docked_poses.sdf"
])

# Step 5: Validate covalent bond geometry
subprocess.run([
    "python", "scripts/validate_geometry.py",
    "--docked", "docked_poses.sdf",
    "--receptor", "protein.pdb",
    "--receptor_atom", receptor_atom,
    "--bond_type", "C-Se",  # or C-S, C-N, C-O
    "--tolerance", "0.1"
])

# Step 6: Analyze contacts
subprocess.run([
    "python", "scripts/analyze_contacts.py",
    "--docked", "docked_poses.sdf",
    "--receptor", "protein.pdb",
    "--cutoff", "5.0"
])

# Step 7: Assess reproducibility across seeds
subprocess.run([
    "python", "scripts/analyze_reproducibility.py",
    "--docking_results", "docked_poses.sdf",
    "--seeds", "0,42,123"
])

# Step 8: Generate PyMOL visualization
subprocess.run([
    "python", "scripts/generate_pymol_script.py",
    "--docked", "docked_poses.sdf",
    "--receptor", "protein.pdb",
    "--receptor_atom", receptor_atom,
    "--output", "visualize.pml"
])
```

### Workflow 2: SAR Exploration and Analog Generation

**Generate and dock analogs to explore SAR:**

```python
# Step 1: Generate analogs from parent molecule
subprocess.run([
    "python", "scripts/generate_analogs.py",
    "--parent_smiles", "CC#CCOc1ccc(C(=O)NCC(N)=O)nn1",
    "--num_designs", "20",
    "--mutation_rules", "extend_chain,add_branch,swap_functional_group",
    "--scaffold_preservation", "True",
    "--output", "analogs.csv"
])

# Step 2: Batch prepare all analogs
import pandas as pd
df = pd.read_csv("analogs.csv")
for idx, row in df.iterrows():
    subprocess.run([
        "python", "scripts/prepare_ligand.py",
        "--smiles", row['smiles'],
        "--ligand_id", f"analog_{idx}",
        "--output", f"analogs_prepared/analog_{idx}.sdf"
    ])

# Step 3: Batch dock all analogs
subprocess.run([
    "python", "scripts/batch_dock.py",
    "--ligands", "analogs_prepared/*.sdf",
    "--receptor", "protein.pdb",
    "--receptor_atom", "A:46:SEG",
    "--attachment_smarts", "[CD1]",
    "--output", "batch_results.json"
])

# Step 4: Rank by affinity and analyze contacts
subprocess.run([
    "python", "scripts/rank_analogs.py",
    "--results", "batch_results.json",
    "--sort_by", "affinity",
    "--output", "ranked_analogs.csv"
])
```

### Workflow 3: Genetic Algorithm Optimization

**Iterative optimization using genetic algorithm:**

```python
# Run GA optimization starting from champion
subprocess.run([
    "python", "scripts/genetic_algorithm.py",
    "--champion_smiles", "CC#CCOc1ccc(C(=O)NCC(N)=O)nn1",
    "--generations", "5",
    "--population_size", "20",
    "--receptor", "protein.pdb",
    "--receptor_atom", "A:46:SEG",
    "--output", "ga_results/"
])

# Analyze GA trajectory
subprocess.run([
    "python", "scripts/analyze_ga_trajectory.py",
    "--ga_dir", "ga_results/",
    "--plot", "affinity_vs_generation.png"
])
```

## Warhead Types and Chemistry

### Supported Warheads

| Warhead | Reactive Group | Typical Target | Bond Formed | Notes |
|---------|---------------|----------------|-------------|-------|
| **Alkyne** | Terminal alkyne | SeCys, Cys | C≡C → C-Se/C-S | Click chemistry, irreversible |
| **Acrylamide** | α,β-unsaturated amide | Cys | Michael addition | Most common in drugs (ibrutinib) |
| **Epoxide** | Three-membered ring | Cys, Asp, Glu | Ring opening | Less common, reversible possible |
| **Haloacetamide** | Chloroacetamide | Cys | SN2 displacement | Fast kinetics |
| **Vinyl sulfone** | -SO2-CH=CH2 | Cys | Michael addition | Irreversible |

### Attachment SMARTS Patterns

```python
# Alkyne terminal carbon (for Se-C bond formation)
"[CD1]"  # Terminal alkyne carbon

# Acrylamide beta carbon (Michael acceptor)
"[C;$(C=C-C(=O)N)]"  # Beta carbon of acrylamide

# Epoxide ring carbon
"[C;R1]"  # Ring carbon in 3-membered ring

# Haloacetamide alpha carbon
"[C;$(C-[Cl,Br,I])]"  # Carbon attached to halogen
```

## Validation Criteria

### Covalent Bond Geometry

| Bond Type | Expected Length (Å) | Tolerance | Assessment |
|-----------|---------------------|-----------|------------|
| C-Se | 1.85 - 2.05 | ±0.1 | Optimal covalent bond |
| C-S | 1.75 - 1.95 | ±0.1 | Optimal covalent bond |
| C-N | 1.40 - 1.55 | ±0.1 | Optimal covalent bond |
| C-O | 1.40 - 1.50 | ±0.1 | Optimal covalent bond |

### Docking Quality Metrics

**Reproducibility (Multi-seed):**
- **Excellent**: σ < 0.5 kcal/mol across seeds
- **Good**: σ < 1.0 kcal/mol
- **Poor**: σ > 1.5 kcal/mol (high variance, uncertain prediction)

**Contact Analysis:**
- Hydrophobic contacts: >10 optimal
- H-bonds: 2-5 (not too many - desolvation penalty)
- Aromatic interactions: Valuable for specificity

**Affinity Benchmarks:**
- -3 to -5 kcal/mol: Weak binder
- -5 to -7 kcal/mol: Moderate binder
- -7+ kcal/mol: Strong binder

## Advanced Techniques

### Multi-Seed Reproducibility Assessment

Run docking with multiple random seeds to assess pose stability:

```bash
# Run with 3+ seeds
for seed in 0 42 123 456 789; do
    gnina --receptor protein.pdb --ligand ligand.sdf \
          --covalent A:46:SEG --cov_atom "[CD1]" \
          --seed $seed --out docked_seed_${seed}.sdf
done

# Compare poses across seeds
python scripts/compare_seeds.py --pattern "docked_seed_*.sdf"
```

### Contact-Driven Design

Analyze contacts to guide analog design:

```python
# Key insight from 6ELW-Se campaign:
# TRP 136 forms 24 hydrophobic contacts in best binder
# → Design branched alkyl to fill this pocket

# If contacts show H-bond donors near ligand:
# → Add carbonyl or ether to accept H-bonds

# If contacts show charged residues:
# → Avoid charged groups (desolvation penalty)
```

### Custom Warhead Definition

Define new warhead types via configuration:

```json
{
  "warhead_name": "cyanoacrylamide",
  "leaving_group_smarts": "[N;$(NC=O)]",
  "attachment_smarts": "[C;$(C=C(C#N))]",
  "bond_formed": "C-S",
  "expected_bond_length": [1.75, 1.95]
}
```

## Limitations and Scope

**This Skill IS Designed For:**
- Irreversible covalent inhibitors
- Well-defined reactive residues (Cys, SeCys, Lys, Ser, Tyr)
- Standard warhead chemistries (alkyne, acrylamide, epoxide, haloacetamide)
- Medium-sized ligands (100-600 Da)
- Single reactive site per ligand

**This Skill IS NOT Designed For:**
- Reversible covalent inhibitors (boronic acids, etc.)
- Multi-site covalent attachment
- Metalloprotein covalent docking
- Covalent protein-protein interactions
- Very large ligands (PROTACs, peptides >20 residues)
- Membrane proteins (insufficient validation)

## Troubleshooting

### Common Issues

**Issue: No poses generated**
- Check receptor atom specification format (chain:resnum:atom_name)
- Verify warhead SMARTS matches ligand structure
- Ensure reactive residue is properly labeled in PDB

**Issue: Poor geometry (bond length outside range)**
- Try different attachment SMARTS
- Increase `--covalent_optimize` iterations
- Check if warhead is compatible with target residue

**Issue: High reproducibility variance (σ > 1.5)**
- Indicates flexible pocket or poor convergence
- Increase `--num_modes`
- Try ensemble docking with multiple receptor conformations

**Issue: All analogs have similar (poor) affinity**
- Scaffold may be suboptimal
- Try scaffold hopping using `scripts/scaffold_hop.py`
- Check if contacts with key residues are formed

### Best Practices from Real Campaigns

**From 6ELW-Se Campaign (-5.62 kcal/mol champion):**
1. **Hydrophobic contacts matter most** - 48 optimal > 204 suboptimal
2. **Branched alkyl wins** - isopropyl > ethyl > methyl for TRP 136 pocket
3. **Ether beats alcohol** - O-CH3 better than OH (H-bond acceptor + lipophilic)
4. **Avoid over-functionalization** - Two CONH2 optimal, third causes clash
5. **Reproducibility precedes affinity** - Ensure σ < 1.0 before trusting rank

## Resources

### Reference Documentation

**`references/workflow_guide.md`**: Complete 8-step workflow with detailed commands, parameter explanations, and decision trees for each step.

**`references/alkyne_se_case_study.md`**: Full case study from 6ELW-Se campaign including SAR learning, GA optimization, and design rules validation.

**`references/warhead_chemistry.md`**: Comprehensive guide to warhead types, chemistry mechanisms, SMARTS patterns, and target residue compatibility.

**`references/validation_criteria.md`**: Detailed validation metrics including bond geometry ranges, contact analysis methods, and reproducibility assessment.

**`references/de_novo_strategies.md`**: Strategies for analog generation, genetic algorithms, Bayesian optimization, and scaffold hopping.

### Helper Scripts (`scripts/`)

**`prepare_ligand.py`**: Complete ligand preparation pipeline (SMILES → 3D → xtb opt → tail removal)

**`batch_dock.py`**: Parallel batch docking with progress tracking

**`generate_analogs.py`**: Rule-based analog generation with configurable mutations

**`genetic_algorithm.py`**: Full GA implementation for ligand optimization

**`validate_geometry.py`**: Covalent bond geometry validation

**`analyze_contacts.py`**: Contact analysis (hydrophobic, H-bond, ionic, aromatic)

**`analyze_reproducibility.py`**: Multi-seed reproducibility assessment

**`generate_pymol_script.py`**: PyMOL visualization generation

## Example: Complete Campaign Workflow

```bash
# 1. Setup
mkdir campaign && cd campaign
ln -s /path/to/6ELW-Se.pdb receptor.pdb

# 2. Initial docking of scaffold
python scripts/prepare_ligand.py --smiles "CC#CCOc1ccc(C(=O)NN)nn1" --output scaffold.sdf
python scripts/dock_and_validate.py --ligand scaffold.sdf --receptor receptor.pdb \
    --receptor_atom "A:46:SEG" --attachment "[CD1]"

# 3. Generate analogs
python scripts/generate_analogs.py --parent scaffold.sdf --num 50 --output analogs/

# 4. Batch dock
python scripts/batch_dock.py --ligands "analogs/*.sdf" --receptor receptor.pdb \
    --config batch_config.json --output results/

# 5. Analyze and select champion
python scripts/rank_by_affinity_and_contacts.py --results results/ --output champions.csv

# 6. GA optimization of champion
python scripts/genetic_algorithm.py --champion $(head -1 champions.csv) \
    --generations 5 --output ga_results/

# 7. Final validation
python scripts/validate_champion.py --ga_dir ga_results/ --receptor receptor.pdb
```

## Citations

When using covalent docking in publications:

**GNINA Covalent Docking:**
```
McNutt et al. (2021) "GNINA 1.0: Molecular docking with deep learning"
Journal of Cheminformatics 13, 43
```

**XTB Geometry Optimization:**
```
Grimme et al. (2017) "A robust and accurate tight-binding quantum chemical 
method for structures, vibrational frequencies, and noncovalent interactions 
of large molecular systems"
J. Chem. Theory Comput. 13, 1989-2009
```

**OpenFF Force Field:**
```
Eastman et al. (2023) "Open Force Field BespokeFit"
J. Chem. Theory Comput. 19, 4524-4535
```

---

**Next Steps:** Read `references/workflow_guide.md` for the complete 8-step protocol, or `references/alkyne_se_case_study.md` for the validated case study.
