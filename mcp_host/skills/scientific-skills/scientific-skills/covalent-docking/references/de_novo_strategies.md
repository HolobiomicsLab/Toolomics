# De Novo Design Strategies for Covalent Docking

## Overview

This document describes strategies for generating and optimizing covalent ligands de novo, including rule-based mutation, genetic algorithms, and other computational design approaches.

---

## 1. Rule-Based Analog Generation

### Mutation Rules

```python
MUTATION_RULES = {
    "extend_chain": {
        "description": "Add CH2 to extend carbon chain",
        "smarts": "[*]~[*]>>[*]~[C]~[*]",
        "probability": 0.3,
        "applies_to": ["alkyl_chains"]
    },
    "add_branch": {
        "description": "Add methyl branch",
        "smarts": "[CH2]>>[C](C)",
        "probability": 0.25,
        "applies_to": ["terminal_alkyl"]
    },
    "add_ether": {
        "description": "Convert CH2 to ether oxygen",
        "smarts": "[CH2]~[CH2]>>[CH2]~[O]~[CH2]",
        "probability": 0.2,
        "applies_to": ["alkyl_linkers"]
    },
    "swap_functional_group": {
        "description": "Replace functional group",
        "transformations": {
            "OH": "OCH3",      # Alcohol to ether
            "CH3": "CH2OH",    # Methyl to hydroxymethyl
            "NH2": "CONH2",    # Amine to amide
            "F": "Cl",         # Halogen swap
        },
        "probability": 0.15
    },
    "add_hbond_group": {
        "description": "Add H-bond donor/acceptor",
        "additions": ["OH", "NH2", "C(=O)", "O"],
        "probability": 0.1,
        "constraints": "not_too_many_hba"
    }
}
```

### Implementation

```python
def generate_analogs_rule_based(
    parent_smiles: str,
    num_designs: int = 10,
    mutation_rules: list = None,
    scaffold_preservation: bool = True
) -> list:
    """
    Generate analogs using rule-based mutations.
    
    Args:
        parent_smiles: Starting molecule
        num_designs: Number of designs to generate
        mutation_rules: List of rule names to apply
        scaffold_preservation: Keep core scaffold intact
    
    Returns:
        List of dicts with smiles and mutation info
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem
    
    parent = Chem.MolFromSmiles(parent_smiles)
    designs = []
    
    for i in range(num_designs):
        # Select mutation rule
        rule = select_weighted_rule(mutation_rules or list(MUTATION_RULES.keys()))
        
        # Apply mutation
        mutated = apply_mutation(parent, rule, scaffold_preservation)
        
        if mutated and is_valid_molecule(mutated):
            designs.append({
                "smiles": Chem.MolToSmiles(mutated),
                "parent": parent_smiles,
                "mutation_type": rule,
                "generation": 0
            })
    
    return designs
```

### SMARTS-Based Transformations

```python
# Predefined transformations
TRANSFORMATIONS = {
    "methyl_to_ethyl": {
        "pattern": Chem.MolFromSmarts("[CH3]"),
        "replacement": Chem.MolFromSmiles("CC")
    },
    "add_methoxy": {
        "pattern": Chem.MolFromSmarts("[OH]"),
        "replacement": Chem.MolFromSmiles("OC")
    },
    "chain_extension": {
        "pattern": Chem.MolFromSmarts("[CH2]~[*]"),
        "replacement": Chem.MolFromSmiles("CC")
    }
}

def apply_transformation(mol, transformation_name: str):
    """Apply a predefined transformation to molecule."""
    trans = TRANSFORMATIONS[transformation_name]
    
    # Find matches
    matches = mol.GetSubstructMatches(trans["pattern"])
    
    if not matches:
        return None
    
    # Apply to first match (or random)
    # RDKit EditMolecule operations...
    
    return modified_mol
```

---

## 2. Genetic Algorithm (GA)

### Algorithm Overview

```
Generation 0: Initial population (random or from champion)
    ↓
Evaluate: Dock all members, calculate fitness
    ↓
Selection: Choose parents based on fitness
    ↓
Crossover: Combine parent features
    ↓
Mutation: Random modifications
    ↓
Generation N+1: New population
    ↓
Repeat until convergence or max generations
```

### Implementation

```python
class GeneticAlgorithm:
    def __init__(
        self,
        population_size: int = 20,
        generations: int = 5,
        mutation_rate: float = 0.3,
        crossover_rate: float = 0.5,
        elitism: int = 2
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
    
    def run(
        self,
        champion_smiles: str,
        receptor_pdb: str,
        receptor_atom: str,
        attachment_smarts: str
    ) -> dict:
        """
        Run GA optimization.
        
        Returns trajectory and final champion.
        """
        # Initialize population
        population = self.initialize_population(champion_smiles)
        
        trajectory = []
        
        for gen in range(self.generations):
            print(f"Generation {gen + 1}/{self.generations}")
            
            # Evaluate fitness (docking)
            fitness_scores = self.evaluate_population(
                population, receptor_pdb, receptor_atom, attachment_smarts
            )
            
            # Record statistics
            best_idx = np.argmin(fitness_scores)
            trajectory.append({
                "generation": gen,
                "best_affinity": fitness_scores[best_idx],
                "best_smiles": population[best_idx],
                "mean_affinity": np.mean(fitness_scores),
                "std_affinity": np.std(fitness_scores)
            })
            
            # Selection
            parents = self.select_parents(population, fitness_scores)
            
            # Crossover and mutation
            offspring = self.create_offspring(parents)
            
            # Elitism - keep best from current generation
            new_population = [population[best_idx]] * self.elitism
            new_population.extend(offspring[:self.population_size - self.elitism])
            
            population = new_population
        
        return {
            "champion": population[0],
            "trajectory": trajectory,
            "generations": self.generations
        }
    
    def evaluate_population(
        self,
        population: list,
        receptor_pdb: str,
        receptor_atom: str,
        attachment_smarts: str
    ) -> list:
        """Dock all population members and return affinities."""
        affinities = []
        
        for smiles in population:
            # Dock molecule
            affinity = dock_and_score(
                smiles, receptor_pdb, receptor_atom, attachment_smarts
            )
            affinities.append(affinity)
        
        return affinities
    
    def select_parents(self, population: list, fitness_scores: list) -> list:
        """Tournament selection."""
        parents = []
        
        for _ in range(len(population)):
            # Tournament
            contestants = random.sample(range(len(population)), 3)
            winner = min(contestants, key=lambda i: fitness_scores[i])
            parents.append(population[winner])
        
        return parents
    
    def create_offspring(self, parents: list) -> list:
        """Crossover and mutation."""
        offspring = []
        
        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[i+1] if i+1 < len(parents) else parents[0]
            
            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self.crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutation
            if random.random() < self.mutation_rate:
                child1 = self.mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self.mutate(child2)
            
            offspring.extend([child1, child2])
        
        return offspring
    
    def crossover(self, parent1: str, parent2: str) -> tuple:
        """
        Molecular crossover - exchange fragments.
        
        Strategy: Identify common scaffold, exchange substituents.
        """
        mol1 = Chem.MolFromSmiles(parent1)
        mol2 = Chem.MolFromSmiles(parent2)
        
        # Find common core
        core = find_common_scaffold([mol1, mol2])
        
        # Exchange R-groups
        child1 = replace_r_groups(mol1, mol2, core)
        child2 = replace_r_groups(mol2, mol1, core)
        
        return (
            Chem.MolToSmiles(child1) if child1 else parent1,
            Chem.MolToSmiles(child2) if child2 else parent2
        )
    
    def mutate(self, smiles: str) -> str:
        """Apply random mutation."""
        mol = Chem.MolFromSmiles(smiles)
        
        # Select random mutation
        mutation = random.choice(list(MUTATION_RULES.keys()))
        
        # Apply
        mutated = apply_mutation(mol, mutation)
        
        return Chem.MolToSmiles(mutated) if mutated else smiles
```

### GA Parameters from 6ELW-Se Campaign

```python
# Optimal parameters found during campaign
OPTIMAL_GA_PARAMS = {
    "population_size": 20,      # Balance diversity vs computation
    "generations": 5,           # Diminishing returns after 5
    "mutation_rate": 0.3,       # 30% mutation rate
    "crossover_rate": 0.5,      # 50% crossover
    "elitism": 2,               # Keep top 2 from each generation
    "early_stopping": {
        "enabled": True,
        "patience": 2,          # Stop if no improvement for 2 gens
        "min_improvement": 0.2  # kcal/mol
    }
}
```

---

## 3. Scaffold Hopping

### Purpose

Replace core scaffold while preserving key interactions.

### Implementation

```python
def scaffold_hop(
    original_smiles: str,
    scaffold_smarts: str,
    replacement_scaffolds: list,
    preserve_warhead: bool = True
) -> list:
    """
    Perform scaffold hopping.
    
    Args:
        original_smiles: Starting molecule
        scaffold_smarts: SMARTS of scaffold to replace
        replacement_scaffolds: List of replacement scaffold SMILES
        preserve_warhead: Keep warhead group intact
    
    Returns:
        List of scaffold-hopped molecules
    """
    from rdkit import Chem
    
    original = Chem.MolFromSmiles(original_smiles)
    scaffold = Chem.MolFromSmarts(scaffold_smarts)
    
    # Identify R-groups attached to scaffold
    r_groups = extract_r_groups(original, scaffold)
    
    # If preserving warhead, identify it
    if preserve_warhead:
        warhead = extract_warhead(original)
    
    results = []
    for replacement_smiles in replacement_scaffolds:
        replacement = Chem.MolFromSmiles(replacement_smiles)
        
        # Attach R-groups to new scaffold
        new_mol = attach_r_groups(replacement, r_groups)
        
        # Re-attach warhead if needed
        if preserve_warhead:
            new_mol = attach_warhead(new_mol, warhead)
        
        if new_mol and is_valid_molecule(new_mol):
            results.append({
                "smiles": Chem.MolToSmiles(new_mol),
                "original_scaffold": scaffold_smarts,
                "new_scaffold": replacement_smiles
            })
    
    return results

# Example replacement scaffolds for triazole
TRIAZOLE_REPLACEMENTS = [
    "c1ccncc1",      # Pyridine
    "c1cccnc1",      # Pyrimidine
    "c1cc[nH]c1",    # Pyrrole
    "c1cocn1",       # Oxazole
    "c1cscn1",       # Thiazole
    "c1ccc2[nH]ccc2c1"  # Indole
]
```

---

## 4. Contact-Driven Design

### Strategy

Design ligands to maximize contacts with key residues.

```python
def contact_driven_design(
    parent_smiles: str,
    target_residue: str,
    current_contacts: int,
    target_contacts: int = 20
) -> list:
    """
    Generate designs to improve contacts with specific residue.
    
    Args:
        parent_smiles: Starting molecule
        target_residue: Residue to target (e.g., "TRP 136")
        current_contacts: Current contact count
        target_contacts: Desired contact count
    
    Returns:
        List of design suggestions
    """
    from rdkit import Chem
    
    mol = Chem.MolFromSmiles(parent_smiles)
    
    gap = target_contacts - current_contacts
    
    designs = []
    
    if gap > 10:
        # Need significant extension
        designs.extend([
            {"type": "extend_chain", "addition": "CH2CH2"},
            {"type": "add_branch", "addition": "isopropyl"},
            {"type": "add_aromatic", "addition": "phenyl"}
        ])
    elif gap > 5:
        # Moderate extension
        designs.extend([
            {"type": "extend_chain", "addition": "CH2"},
            {"type": "add_branch", "addition": "methyl"}
        ])
    else:
        # Fine-tuning
        designs.extend([
            {"type": "adjust_position", "strategy": "optimize_torsion"},
            {"type": "add_methyl", "position": "terminal"}
        ])
    
    return designs

# Residue-specific design rules
RESIDUE_DESIGN_RULES = {
    "TRP": {
        "preferred_groups": ["isopropyl", "tert-butyl", "phenyl"],
        "avoid": ["charged", "very_polar"],
        "strategy": "fill_hydrophobic_pocket"
    },
    "PHE": {
        "preferred_groups": ["phenyl", "cyclohexyl"],
        "avoid": ["large_branched"],
        "strategy": "pi_stacking"
    },
    "ASP": {
        "preferred_groups": ["NH2", "guanidinium"],
        "avoid": ["negative"],
        "strategy": "salt_bridge"
    },
    "HIS": {
        "preferred_groups": ["OH", "C=O", "NH"],
        "avoid": ["very_large"],
        "strategy": "h_bond"
    }
}
```

---

## 5. Property-Based Filtering

### Drug-Likeness Filters

```python
PROPERTY_RANGES = {
    "molecular_weight": (200, 600),
    "logp": (-1, 5),
    "hbd": (0, 5),
    "hba": (1, 10),
    "rotatable_bonds": (0, 10),
    "tpsa": (40, 140),
    "formal_charge": (-1, 1)
}

def filter_by_properties(molecules: list) -> tuple:
    """
    Filter molecules by drug-like properties.
    
    Returns (passed, failed) lists.
    """
    from rdkit.Chem import Descriptors
    
    passed = []
    failed = []
    
    for mol_data in molecules:
        mol = Chem.MolFromSmiles(mol_data["smiles"])
        
        violations = []
        
        mw = Descriptors.MolWt(mol)
        if not (PROPERTY_RANGES["molecular_weight"][0] <= mw <= PROPERTY_RANGES["molecular_weight"][1]):
            violations.append(f"MW: {mw:.1f}")
        
        logp = Descriptors.MolLogP(mol)
        if not (PROPERTY_RANGES["logp"][0] <= logp <= PROPERTY_RANGES["logp"][1]):
            violations.append(f"LogP: {logp:.2f}")
        
        hbd = Descriptors.NumHDonors(mol)
        if not (PROPERTY_RANGES["hbd"][0] <= hbd <= PROPERTY_RANGES["hbd"][1]):
            violations.append(f"HBD: {hbd}")
        
        # ... more properties
        
        if violations:
            mol_data["violations"] = violations
            failed.append(mol_data)
        else:
            passed.append(mol_data)
    
    return passed, failed
```

### Reactive Group Filters

```python
REACTIVE_PATTERNS = {
    "迈克尔受体": "C=CC(=O)",  # Michael acceptor
    "epoxide": "C1OC1",
    "acyl_halide": "C(=O)[Cl,Br,I]",
    "sulfonyl_halide": "S(=O)(=O)[Cl,Br]"
}

def filter_reactive_groups(molecules: list, allowed_warhead: str) -> list:
    """
    Filter out molecules with unwanted reactive groups.
    
    Keeps only the intended warhead chemistry.
    """
    filtered = []
    
    for mol_data in molecules:
        mol = Chem.MolFromSmiles(mol_data["smiles"])
        
        has_unwanted = False
        for name, smarts in REACTIVE_PATTERNS.items():
            if name != allowed_warhead:
                pattern = Chem.MolFromSmarts(smarts)
                if mol.HasSubstructMatch(pattern):
                    has_unwanted = True
                    break
        
        if not has_unwanted:
            filtered.append(mol_data)
    
    return filtered
```

---

## 6. Ensemble Strategy

### Combining Multiple Methods

```python
def ensemble_design(
    champion_smiles: str,
    receptor_pdb: str,
    receptor_atom: str,
    num_designs_per_method: int = 10
) -> dict:
    """
    Run multiple de novo methods and combine results.
    """
    all_designs = []
    
    # Method 1: Rule-based generation
    print("Running rule-based generation...")
    rule_based = generate_analogs_rule_based(
        champion_smiles,
        num_designs=num_designs_per_method
    )
    all_designs.extend(rule_based)
    
    # Method 2: Genetic algorithm
    print("Running genetic algorithm...")
    ga = GeneticAlgorithm(population_size=20, generations=5)
    ga_results = ga.run(champion_smiles, receptor_pdb, receptor_atom, "[CD1]")
    all_designs.extend(ga_results["population"])
    
    # Method 3: Scaffold hopping (if appropriate)
    print("Running scaffold hopping...")
    scaffolds = scaffold_hop(
        champion_smiles,
        "c1n[nH]c(C)n1",  # Triazole
        TRIAZOLE_REPLACEMENTS
    )
    all_designs.extend(scaffolds)
    
    # Remove duplicates
    unique_designs = deduplicate_by_smiles(all_designs)
    
    # Filter by properties
    passed, failed = filter_by_properties(unique_designs)
    
    # Dock and rank
    print(f"Docking {len(passed)} unique designs...")
    ranked = batch_dock_and_rank(passed, receptor_pdb, receptor_atom)
    
    return {
        "designs": ranked[:20],  # Top 20
        "statistics": {
            "total_generated": len(all_designs),
            "unique": len(unique_designs),
            "property_pass": len(passed),
            "top_affinity": ranked[0]["affinity"] if ranked else None
        }
    }
```

---

## 7. Campaign Workflow Integration

### Complete Design-Dock-Analyze Loop

```python
def iterative_optimization_campaign(
    initial_smiles: str,
    receptor_pdb: str,
    receptor_atom: str,
    max_iterations: int = 5,
    convergence_threshold: float = 0.1
):
    """
    Run complete iterative optimization campaign.
    """
    current_champion = initial_smiles
    current_affinity = dock_and_score(initial_smiles, receptor_pdb, receptor_atom)
    
    history = [{
        "iteration": 0,
        "smiles": initial_smiles,
        "affinity": current_affinity
    }]
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*60}")
        print(f"Iteration {iteration}/{max_iterations}")
        print(f"Current champion: {current_affinity:.2f} kcal/mol")
        print(f"{'='*60}")
        
        # Generate designs
        designs = ensemble_design(
            current_champion,
            receptor_pdb,
            receptor_atom
        )
        
        # Find best
        best_design = designs["designs"][0]
        best_affinity = best_design["affinity"]
        
        print(f"Best new design: {best_affinity:.2f} kcal/mol")
        
        # Check improvement
        improvement = current_affinity - best_affinity
        
        if improvement > convergence_threshold:
            print(f"Improvement: {improvement:.2f} kcal/mol ✓")
            current_champion = best_design["smiles"]
            current_affinity = best_affinity
        else:
            print(f"Improvement: {improvement:.2f} kcal/mol (below threshold)")
            print("Convergence reached.")
            break
        
        history.append({
            "iteration": iteration,
            "smiles": current_champion,
            "affinity": current_affinity
        })
    
    return {
        "final_champion": current_champion,
        "final_affinity": current_affinity,
        "iterations": len(history) - 1,
        "history": history
    }
```

---

## Summary

| Strategy | Best For | Computation | Success Rate |
|----------|----------|-------------|--------------|
| **Rule-based** | Quick exploration, SAR validation | Low | Moderate |
| **Genetic Algorithm** | Deep optimization, novel structures | Medium-High | Good |
| **Scaffold Hopping** | Escape patents, new IP | Medium | Variable |
| **Contact-driven** | Specific residue targeting | Medium | Good |
| **Ensemble** | Comprehensive exploration | High | Best |

**Recommendation:** Start with rule-based, progress to GA, use ensemble for final optimization.
