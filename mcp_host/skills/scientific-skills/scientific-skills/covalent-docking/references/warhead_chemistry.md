# Warhead Chemistry Guide

## Overview

Covalent warheads are electrophilic functional groups that form covalent bonds with nucleophilic residues in proteins. This guide covers chemistry, SMARTS patterns, and compatibility for common warhead types.

---

## Warhead Types

### 1. Alkyne (Terminal Alkyne)

**Chemistry:**
- Forms C≡C → C-S or C≡C → C-Se bond
- Click chemistry with thiols/selenols
- Irreversible attachment

**SMARTS Patterns:**
```
Attachment: [CD1]                    # Terminal alkyne carbon
Full warhead: [C;$(C#C)]             # Any alkyne carbon
Terminal: [C;$(C#C-H)]               # Terminal alkyne
```

**Target Residues:**
- Cys (SG) - Thiol
- SeCys (SEG) - Selenol (preferred, more nucleophilic)

**Bond Formation:**
```
R-C≡C-H + R'-Se-H → R-C≡C-Se-R' + H₂
Expected bond length: C-Se 1.85-2.05 Å, C-S 1.75-1.95 Å
```

**Pros:**
- Stable covalent bond
- Clean reaction (no byproducts)
- Allows rotation around bond

**Cons:**
- Requires terminal alkyne (synthetic complexity)
- Slower kinetics than some warheads

**Example Ligands:**
- CC#CCOc1ccc(C(=O)NCC(N)=O)nn1 (6ELW-Se campaign)

---

### 2. Acrylamide (Michael Acceptor)

**Chemistry:**
- Michael addition to β-carbon
- Forms C=C-C(=O)N → C-S-C-C(=O)N
- Most common in approved drugs

**SMARTS Patterns:**
```
Attachment (β-carbon): [C;$(C=C-C(=O)N)]
Full warhead: C=CC(=O)N              # Acrylamide
Substituted: C=C(C)C(=O)N            # Crotonamide
Cyano: C=C(C#N)C(=O)N               # Cyanoacrylamide (faster)
```

**Target Residues:**
- Cys (SG) - Primary target
- Lys (NZ) - Possible but slower

**Bond Formation:**
```
R-CH=CH-C(=O)-NH-R' + R''-S-H → R-CH(S-R'')-CH₂-C(=O)-NH-R'
Expected bond length: C-S 1.75-1.95 Å
```

**Pros:**
- Well-established in drugs (ibrutinib, osimertinib)
- Tunable reactivity (substituents on double bond)
- Good synthetic accessibility

**Cons:**
- Can react with off-target thiols
- Stability concerns (hydrolysis)

**Reactivity Tuning:**
| Substituent | Reactivity | Stability |
|-------------|------------|-----------|
| -H (acrylamide) | Moderate | Good |
| -CH₃ (crotonamide) | Low | Excellent |
| -CN (cyanoacrylamide) | High | Fair |

---

### 3. Epoxide

**Chemistry:**
- Ring opening by nucleophilic attack
- Forms 3-membered ring → open chain
- Can be reversible depending on conditions

**SMARTS Patterns:**
```
Attachment: [C;R1]                   # Ring carbon in 3-membered ring
Full warhead: C1OC1                  # Epoxide ring
Substituted: C1OC1C                  # Substituted epoxide
```

**Target Residues:**
- Cys (SG) - Thiol (primary)
- Asp (OD) - Carboxylate
- Glu (OE) - Carboxylate
- Lys (NZ) - Amine (slower)

**Bond Formation:**
```
    O                         OH
    |                         |
R - C - C-R' + R''-S-H → R - C - C-R'
    \ /                       |
     C                       S-R''

Expected bond length: C-S 1.75-1.95 Å, C-O 1.40-1.50 Å
```

**Pros:**
- High reactivity
- Stereochemistry important (can be selective)
- Natural product-derived

**Cons:**
- Potential off-target reactivity
- Stability issues in plasma
- Synthetic complexity

---

### 4. Haloacetamide

**Chemistry:**
- SN2 displacement of halide
- Forms R-C(=O)-NH-CH₂-X → R-C(=O)-NH-CH₂-S-R'
- Fast kinetics

**SMARTS Patterns:**
```
Attachment: [C;$(C-[Cl,Br,I])]       # Carbon attached to halogen
Full warhead: NC(=O)C[Cl,Br,I]      # Haloacetamide
Chloro: NC(=O)CCl                   # Chloroacetamide
Bromo: NC(=O)CBr                    # Bromoacetamide (more reactive)
Iodo: NC(=O)CI                      # Iodoacetamide (most reactive)
```

**Target Residues:**
- Cys (SG) - Primary and fastest
- Lys (NZ) - Secondary target
- His (NE/ND) - Possible

**Bond Formation:**
```
R-C(=O)-NH-CH₂-Cl + R'-S-H → R-C(=O)-NH-CH₂-S-R' + HCl
Expected bond length: C-S 1.75-1.95 Å
```

**Reactivity Order:**
Iodo > Bromo > Chloro >> Fluoro (fluoro unreactive)

**Pros:**
- Very fast reaction kinetics
- Highly selective for thiols at neutral pH
- Well-characterized chemistry

**Cons:**
- Can react with multiple Cys (selectivity concerns)
- Potential immunogenicity
- Irreversible (may not be desired)

---

### 5. Vinyl Sulfone

**Chemistry:**
- Michael addition to β-carbon
- Forms R-SO₂-CH=CH₂ → R-SO₂-CH₂-CH₂-S-R'
- Highly irreversible

**SMARTS Patterns:**
```
Attachment: [C;$(C=C-S(=O)(=O))]     # Beta carbon of vinyl sulfone
Full warhead: C=CS(=O)(=O)R          # Vinyl sulfone
Methyl: C=CS(=O)(=O)C               # Methyl vinyl sulfone
```

**Target Residues:**
- Cys (SG) - Primary
- Lys (NZ) - Secondary

**Bond Formation:**
```
R-SO₂-CH=CH₂ + R'-S-H → R-SO₂-CH₂-CH₂-S-R'
Expected bond length: C-S 1.75-1.95 Å
```

**Pros:**
- Highly stable covalent bond
- Good selectivity for Cys over Lys
- Tunable with sulfone substituents

**Cons:**
- Very irreversible (concerns for drug development)
- Synthetic complexity
- Larger size than acrylamide

---

## Warhead Selection Guide

### By Target Residue

| Warhead | Cys | SeCys | Lys | Ser | Tyr | Asp/Glu |
|---------|-----|-------|-----|-----|-----|---------|
| Alkyne | ★★★ | ★★★ | ★☆☆ | ☆☆☆ | ☆☆☆ | ☆☆☆ |
| Acrylamide | ★★★ | ★★☆ | ★★☆ | ★☆☆ | ★☆☆ | ☆☆☆ |
| Epoxide | ★★★ | ★★☆ | ★★☆ | ★★☆ | ★☆☆ | ★★☆ |
| Haloacetamide | ★★★ | ★★★ | ★★☆ | ★☆☆ | ★☆☆ | ☆☆☆ |
| Vinyl Sulfone | ★★★ | ★★☆ | ★★☆ | ☆☆☆ | ☆☆☆ | ☆☆☆ |

★★★ = Excellent, ★★☆ = Good, ★☆☆ = Fair, ☆☆☆ = Poor

### By Application

| Goal | Recommended Warhead |
|------|---------------------|
| Drug development | Acrylamide (proven track record) |
| Fast kinetics | Haloacetamide, Cyanoacrylamide |
| High stability | Alkyne, Vinyl Sulfone |
| Reversible potential | Epoxide (some conditions) |
| Selectivity for Cys | Acrylamide, Haloacetamide |
| SeCys targeting | Alkyne (preferred), Haloacetamide |

---

## SMARTS Pattern Library

### Attachment Atoms by Warhead

```python
WARHEAD_SMARTS = {
    # Alkyne
    "alkyne_terminal": "[CD1]",
    "alkyne_internal": "[C;$(C#C)]",
    
    # Acrylamide variants
    "acrylamide_beta": "[C;$(C=C-C(=O)N)]",
    "acrylamide_alpha": "[C;$(C=C-C(=O)N)]",  # Same as beta (both carbons reactive)
    "cyanoacrylamide_beta": "[C;$(C=C(C#N))]",
    "crotonamide_beta": "[C;$(C=C(C))]",
    
    # Epoxide
    "epoxide_carbon": "[C;R1]",
    
    # Haloacetamide
    "chloroacetamide": "[C;$(C-[Cl])]",
    "bromoacetamide": "[C;$(C-[Br])]",
    "iodoacetamide": "[C;$(C-[I])]",
    "haloacetamide_any": "[C;$(C-[Cl,Br,I])]",
    
    # Vinyl sulfone
    "vinyl_sulfone_beta": "[C;$(C=C-S(=O)(=O))]",
    
    # Less common
    "aziridine": "[C;R1;$(C-N)]",  # 3-membered ring with N
    "nitrile": "[C;$(C#N)]",        # For reversible covalent
}
```

### Leaving Groups

```python
LEAVING_GROUP_SMARTS = {
    "alkyne_se": "[N;$(NC=O)]",           # Amide leaving group
    "alkyne_generic": "[*]",              # Generic leaving group
    "acrylamide": "[N;$(NC(=O)C=C)]",    # Part of acrylamide
    "epoxide": "[O;R1]",                  # Epoxide oxygen
    "chloroacetamide": "[Cl]",            # Chloride
    "bromoacetamide": "[Br]",             # Bromide
    "iodoacetamide": "[I]",               # Iodide
}
```

---

## Chemical Feasibility Checks

### Warhead Stability

```python
def check_warhead_stability(mol, warhead_type: str) -> dict:
    """
    Check chemical stability of warhead in molecule.
    
    Returns stability concerns and recommendations.
    """
    concerns = []
    
    if warhead_type == "acrylamide":
        # Check for hydrolysis-prone positions
        if has_adjacent_hydroxyl(mol):
            concerns.append("Adjacent OH may accelerate hydrolysis")
        
    elif warhead_type == "epoxide":
        # Epoxides are generally reactive
        concerns.append("High reactivity - monitor stability")
        
    elif warhead_type in ["chloroacetamide", "bromoacetamide"]:
        # Check for elimination possibilities
        if has_beta_hydrogen(mol):
            concerns.append("β-hydrogen present - elimination possible")
    
    return {
        "warhead": warhead_type,
        "stability_concerns": concerns,
        "recommendation": "Consider stability assessment" if concerns else "Likely stable"
    }
```

### Synthetic Accessibility

```python
def assess_synthetic_accessibility(warhead_type: str, scaffold_complexity: int) -> str:
    """
    Estimate synthetic difficulty.
    
    Returns: "easy", "moderate", or "difficult"
    """
    base_scores = {
        "acrylamide": 2,      # Easy (amide formation)
        "alkyne": 3,          # Moderate (requires Sonogashira or similar)
        "epoxide": 4,         # Moderate-Difficult (stereochemistry)
        "chloroacetamide": 2, # Easy (chloroacetylation)
        "bromoacetamide": 2,  # Easy (bromoacetylation)
        "vinyl_sulfone": 4    # Moderate-Difficult
    }
    
    total_score = base_scores.get(warhead_type, 3) + scaffold_complexity
    
    if total_score <= 3:
        return "easy"
    elif total_score <= 6:
        return "moderate"
    else:
        return "difficult"
```

---

## Custom Warhead Definition

### Adding New Warheads

To add a custom warhead, create a configuration file:

```json
{
  "warhead_name": "my_custom_warhead",
  "chemistry": {
    "type": "michael_addition",
    "target_residues": ["CYS", "LYS"],
    "bond_formed": "C-S",
    "expected_bond_length": [1.75, 1.95]
  },
  "smarts": {
    "attachment": "[C;$(C=C-C(=O))]",
    "leaving_group": null,
    "full_warhead": "C=CC(=O)N"
  },
  "properties": {
    "reversible": false,
    "reactivity": "high",
    "stability": "moderate",
    "synthetic_difficulty": "moderate"
  }
}
```

---

## Summary Table

| Warhead | Target | Bond | Length (Å) | Reversibility | Drug Examples |
|---------|--------|------|------------|---------------|---------------|
| Alkyne | Cys/SeCys | C-S/Se | 1.75-2.05 | Irreversible | None yet |
| Acrylamide | Cys | C-S | 1.75-1.95 | Irreversible | Ibrutinib, Osimertinib |
| Epoxide | Cys/Asp/Glu | C-S/O | 1.75-1.95 | Cond. reversible | E-64 (inhibitor) |
| Haloacetamide | Cys/Lys | C-S/N | 1.75-1.95 | Irreversible | Research tools |
| Vinyl Sulfone | Cys/Lys | C-S | 1.75-1.95 | Irreversible | Research tools |

---

## References

1. Singh J, et al. (2011) "Emerging Role of Covalent Drugs" Nature Reviews Drug Discovery
2. London N, et al. (2014) "Covalent Ligand Discovery" Drug Discovery Today
3. Gehringer M, et al. (2016) "Emerging Covalent Warheads" J. Med. Chem.
4. Kaplan JB, et al. (2023) "Targeted Covalent Inhibitors" ACS Medicinal Chemistry Letters
