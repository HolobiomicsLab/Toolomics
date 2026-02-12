# Validation Criteria for Covalent Docking

## Overview

This document defines quantitative validation criteria for covalent docking results. Use these metrics to assess pose quality, chemical feasibility, and reproducibility.

---

## 1. Covalent Bond Geometry

### Bond Length Criteria

| Bond Type | Optimal Range (Å) | Acceptable (Å) | Poor (Å) | Assessment |
|-----------|-------------------|----------------|----------|------------|
| **C-Se** | 1.85 - 2.05 | 1.75 - 2.15 | <1.75 or >2.15 | Geometry valid? |
| **C-S** | 1.75 - 1.95 | 1.65 - 2.05 | <1.65 or >2.05 | Geometry valid? |
| **C-N** | 1.40 - 1.55 | 1.35 - 1.65 | <1.35 or >1.65 | Geometry valid? |
| **C-O** | 1.40 - 1.50 | 1.35 - 1.60 | <1.35 or >1.60 | Geometry valid? |

### Tolerance Settings

```python
BOND_LENGTH_TOLERANCE = 0.1  # Å beyond expected range

def assess_bond_length(bond_type: str, distance: float) -> dict:
    """
    Assess covalent bond length.
    
    Returns assessment and quality score.
    """
    RANGES = {
        "C-Se": (1.85, 2.05),
        "C-S": (1.75, 1.95),
        "C-N": (1.40, 1.55),
        "C-O": (1.40, 1.50)
    }
    
    opt_min, opt_max = RANGES[bond_type]
    acc_min, acc_max = opt_min - 0.1, opt_max + 0.1
    
    if opt_min <= distance <= opt_max:
        return {"assessment": "optimal", "score": 1.0}
    elif acc_min <= distance <= acc_max:
        return {"assessment": "acceptable", "score": 0.7}
    else:
        return {"assessment": "poor", "score": 0.0}
```

### Bond Angle Criteria

| Angle | Optimal | Acceptable Range | Notes |
|-------|---------|------------------|-------|
| C-Se-Cα | 96° | 90-110° | Tetrahedral geometry at Se |
| C-S-Cα | 100° | 95-115° | Tetrahedral geometry at S |
| C-N-Cα | 109° | 100-120° | Varies with hybridization |
| C-O-Cα | 110° | 100-120° | Varies with environment |

---

## 2. Docking Pose Quality

### Affinity Score Interpretation

| Affinity (kcal/mol) | Binding Strength | Action |
|---------------------|------------------|--------|
| > -3.0 | Very weak | Likely not viable |
| -3.0 to -5.0 | Weak | Marginal, needs optimization |
| -5.0 to -7.0 | Moderate | Good starting point |
| -7.0 to -9.0 | Strong | Excellent binder |
| < -9.0 | Very strong | Exceptional (verify) |

### Pose Rank Criteria

For multi-mode docking, analyze pose distribution:

```python
def assess_pose_distribution(poses: list) -> dict:
    """
    Assess quality of pose ensemble.
    
    Args:
        poses: List of pose dicts with affinity and coordinates
    """
    affinities = [p["affinity"] for p in poses]
    
    # Affinity spread
    affinity_range = max(affinities) - min(affinities)
    
    # RMSD of top poses
    top_poses = poses[:3]
    rmsds = []
    for i in range(len(top_poses)):
        for j in range(i+1, len(top_poses)):
            rmsd = calculate_rmsd(top_poses[i], top_poses[j])
            rmsds.append(rmsd)
    avg_rmsd = sum(rmsds) / len(rmsds) if rmsds else 0
    
    assessment = {
        "affinity_range": affinity_range,
        "top3_avg_rmsd": avg_rmsd,
        "diversity": "high" if avg_rmsd > 2.0 else "moderate" if avg_rmsd > 1.0 else "low"
    }
    
    # Quality indicators
    if affinity_range < 1.0 and avg_rmsd < 1.0:
        assessment["confidence"] = "high"
    elif affinity_range < 2.0 and avg_rmsd < 2.0:
        assessment["confidence"] = "moderate"
    else:
        assessment["confidence"] = "low"
    
    return assessment
```

---

## 3. Reproducibility Metrics

### Multi-Seed Variance

Run docking with 3+ seeds and analyze variance:

```python
def calculate_reproducibility_metrics(affinities: list) -> dict:
    """
    Calculate reproducibility statistics.
    
    Args:
        affinities: List of best affinity from each seed
    """
    import statistics
    
    mean = statistics.mean(affinities)
    std = statistics.stdev(affinities) if len(affinities) > 1 else 0
    
    # Coefficient of variation
    cv = abs(std / mean) if mean != 0 else 0
    
    # Range
    range_val = max(affinities) - min(affinities)
    
    return {
        "mean": mean,
        "std": std,
        "cv": cv,
        "range": range_val,
        "min": min(affinities),
        "max": max(affinities)
    }
```

### Reproducibility Grading

| σ (kcal/mol) | CV | Grade | Interpretation |
|--------------|-----|-------|----------------|
| < 0.3 | < 0.05 | A+ | Excellent, highly reliable |
| 0.3 - 0.5 | 0.05 - 0.10 | A | Very good, reliable |
| 0.5 - 1.0 | 0.10 - 0.20 | B | Good, acceptable |
| 1.0 - 1.5 | 0.20 - 0.30 | C | Moderate, caution advised |
| > 1.5 | > 0.30 | D | Poor, results uncertain |

### Decision Matrix

```python
def reproducibility_recommendation(grade: str) -> str:
    """Get recommendation based on reproducibility grade."""
    recommendations = {
        "A+": "Results highly reliable. Proceed with confidence.",
        "A": "Results reliable. Standard confidence appropriate.",
        "B": "Results acceptable. Consider additional sampling if possible.",
        "C": "Moderate reliability. Increase num_modes or investigate system.",
        "D": "Poor reliability. System may be too flexible. Check preparation."
    }
    return recommendations.get(grade, "Unknown grade")
```

---

## 4. Contact Analysis

### Contact Type Definitions

```python
CONTACT_DEFINITIONS = {
    "hydrophobic": {
        "atom_types": ["C"],
        "max_distance": 4.5,
        "description": "Carbon-carbon contact (van der Waals)"
    },
    "hbond_donor": {
        "atom_types": ["N", "O"],
        "max_distance": 3.5,
        "description": "H-bond donor to acceptor"
    },
    "hbond_acceptor": {
        "atom_types": ["N", "O"],
        "max_distance": 3.5,
        "description": "H-bond acceptor to donor"
    },
    "aromatic": {
        "atom_types": [" aromatic_C "],
        "max_distance": 5.0,
        "centroid": True,
        "description": "Aromatic ring interaction"
    },
    "ionic": {
        "atom_types": ["N+", "O-"],
        "max_distance": 4.0,
        "description": "Salt bridge or ionic interaction"
    },
    "repulsive": {
        "atom_types": ["any"],
        "max_distance": 2.5,
        "description": "Too close - potential clash"
    }
}
```

### Contact Quality Metrics

| Contact Type | Optimal Count | Acceptable Range | Too Many | Notes |
|--------------|---------------|------------------|----------|-------|
| Hydrophobic | 15-30 | 10-40 | >50 | Quality > quantity |
| H-bonds | 2-5 | 1-7 | >10 | Too many = desolvation penalty |
| Aromatic | 1-3 | 0-5 | >8 | Specific interactions valuable |
| Ionic | 0-2 | 0-3 | >5 | Charge complementarity |
| Repulsive | 0 | 0 | >0 | Indicates clashes |

### Key Residue Contacts

From 6ELW-Se campaign, monitor these residue types:

| Residue Type | Role | Optimal Contacts | Action if Missing |
|--------------|------|------------------|-------------------|
| TRP | Hydrophobic anchor | ≥15 | Extend tail to fill pocket |
| PHE/TYR | π-stacking | 2-5 | Add aromatic rings |
| HIS | H-bond partner | 1-2 | Add H-bond donors/acceptors |
| ASP/GLU | Salt bridge | 0-1 | Consider charged groups |
| SER/THR | H-bond network | 1-3 | Add OH groups carefully |

### Contact Score

```python
def calculate_contact_score(contacts: dict) -> float:
    """
    Calculate overall contact quality score.
    
    Returns score 0-1 based on contact quality and distribution.
    """
    scores = {
        "hydrophobic": min(len(contacts["hydrophobic"]) / 20, 1.0),
        "hbond": min(len(contacts["hydrogen_bonds"]) / 4, 1.0),
        "aromatic": min(len(contacts["aromatic"]) / 2, 1.0),
        "no_clash": 0.0 if contacts["repulsive"] else 1.0
    }
    
    # Weighted average
    weights = {"hydrophobic": 0.4, "hbond": 0.3, "aromatic": 0.2, "no_clash": 0.1}
    
    total = sum(scores[k] * weights[k] for k in scores)
    return total
```

---

## 5. Composite Quality Score

### Overall Docking Quality

Combine all metrics into single quality score:

```python
def calculate_overall_quality(docking_result: dict) -> dict:
    """
    Calculate composite quality score.
    
    Combines geometry, affinity, reproducibility, and contacts.
    """
    # Individual scores (0-1)
    geometry_score = docking_result["geometry_validation"]["score"]
    affinity_score = min(abs(docking_result["affinity"]) / 7.0, 1.0)
    repro_score = 1.0 - min(docking_result["reproducibility"]["std"] / 2.0, 1.0)
    contact_score = calculate_contact_score(docking_result["contacts"])
    
    # Weights
    weights = {
        "geometry": 0.25,      # Must have valid geometry
        "affinity": 0.25,      # Affinity matters
        "reproducibility": 0.25,  # Pose stability
        "contacts": 0.25       # Interaction quality
    }
    
    overall = (
        geometry_score * weights["geometry"] +
        affinity_score * weights["affinity"] +
        repro_score * weights["reproducibility"] +
        contact_score * weights["contacts"]
    )
    
    return {
        "overall_score": overall,
        "component_scores": {
            "geometry": geometry_score,
            "affinity": affinity_score,
            "reproducibility": repro_score,
            "contacts": contact_score
        },
        "grade": score_to_grade(overall)
    }

def score_to_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 0.9: return "A+"
    if score >= 0.8: return "A"
    if score >= 0.7: return "B"
    if score >= 0.6: return "C"
    return "D"
```

### Quality Grade Interpretation

| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| A+ | 0.90 - 1.00 | Exceptional - publishable quality |
| A | 0.80 - 0.89 | Excellent - reliable for design |
| B | 0.70 - 0.79 | Good - viable with minor issues |
| C | 0.60 - 0.69 | Fair - significant concerns |
| D | < 0.60 | Poor - not suitable |

---

## 6. Pass/Fail Checklist

### Minimum Criteria

For a docking result to be considered valid, it MUST pass:

- [ ] **Geometry**: Bond length within acceptable range for bond type
- [ ] **No Clashes**: No repulsive contacts (< 2.5 Å)
- [ ] **Reproducibility**: σ < 1.5 kcal/mol across seeds
- [ ] **Affinity**: Better than -3.0 kcal/mol

### Recommended Criteria

For a high-quality result, SHOULD meet:

- [ ] **Geometry**: Bond length in optimal range
- [ ] **Contacts**: ≥10 hydrophobic + ≥1 H-bond
- [ ] **Reproducibility**: σ < 0.5 kcal/mol
- [ ] **Affinity**: Better than -5.0 kcal/mol
- [ ] **Key Residue**: Contacts with target pocket residue

---

## 7. Comparison Metrics

### Comparative Analysis

When comparing multiple ligands:

```python
def compare_ligands(ligand_results: list) -> dict:
    """
    Compare multiple ligand docking results.
    
    Returns ranking with statistical significance.
    """
    # Sort by affinity
    sorted_ligands = sorted(ligand_results, 
                           key=lambda x: x["affinity"])
    
    # Calculate statistical differences
    comparisons = []
    for i in range(len(sorted_ligands)):
        for j in range(i+1, len(sorted_ligands)):
            l1, l2 = sorted_ligands[i], sorted_ligands[j]
            
            # Check if difference is significant (>1 kcal/mol)
            diff = abs(l1["affinity"] - l2["affinity"])
            significant = diff > 1.0
            
            comparisons.append({
                "better": l1["name"],
                "worse": l2["name"],
                "difference": diff,
                "significant": significant
            })
    
    return {
        "ranking": [l["name"] for l in sorted_ligands],
        "comparisons": comparisons,
        "champion": sorted_ligands[0]["name"]
    }
```

### Significance Thresholds

| ΔAffinity (kcal/mol) | Significance | Action |
|----------------------|--------------|--------|
| < 0.5 | Not significant | Consider equivalent |
| 0.5 - 1.0 | Marginally significant | Prefer higher affinity |
| > 1.0 | Significant | Clear winner |
| > 2.0 | Highly significant | Strong preference |

---

## 8. Validation Report Template

```yaml
docking_validation_report:
  ligand: "compound_name"
  receptor: "6ELW-Se"
  receptor_atom: "A:46:SEG"
  
  geometry:
    bond_type: "C-Se"
    measured_distance: 1.94
    expected_range: [1.85, 2.05]
    assessment: "optimal"
    score: 1.0
  
  affinity:
    best_score: -5.62
    units: "kcal/mol"
    interpretation: "strong_binder"
  
  reproducibility:
    seeds: [0, 42, 123]
    affinities: [-5.55, -5.62, -5.58]
    mean: -5.58
    std: 0.035
    grade: "A+"
  
  contacts:
    hydrophobic: 24
    hydrogen_bonds: 3
    aromatic: 2
    repulsive: 0
    key_residues:
      TRP_136: 24
      PHE_140: 3
      HIS_143: 2
  
  overall:
    composite_score: 0.94
    grade: "A+"
    recommendation: "Proceed with design"
```

---

## Summary

Use these validation criteria to:

1. **Filter** poor docking results automatically
2. **Rank** compounds by quality, not just affinity
3. **Compare** results across different ligands
4. **Report** confidence levels for predictions

Remember: **No single metric tells the whole story.** Always consider geometry, affinity, reproducibility, and contacts together.
