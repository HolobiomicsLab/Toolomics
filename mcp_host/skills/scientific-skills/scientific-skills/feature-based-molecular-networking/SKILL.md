# Feature-Based Molecular Networking (FBMN) - Agent Skills

## Domain Overview

FBMN connects LC-MS/MS metabolomics data with bioactivity assays to identify bioactive compounds in complex mixtures (e.g., natural products, botanical extracts).

**Core Principle**: Compounds with similar MS/MS fragmentation patterns are structurally related. If one is bioactive, its neighbors in the network may also be bioactive.

## Standard Workflow

### Stage 1: Data Preprocessing
1. **Input Requirements**:
   - Raw MS data (.mzXML/.mzML) - centroided, centroid mode
   - Feature quantification table (from MZmine/Optimus)
   - Bioactivity data (EC50, CC50, % inhibition, etc.)

2. **Feature Table Format**:
   - Rows: Features (compounds)
   - Columns: Sample intensities
   - Metadata: m/z, RT, optional compound IDs
   - Bioactivity row: Often embedded as first/last row

3. **Concrete Data Format Examples**:

   **MZmine Feature Quantification Table** (CSV):
   ```
   row ID,row m/z,row retention time,Extract.mzXML Peak area,F_5.mzXML Peak area,F_6.mzXML Peak area,...
   BioactivityCHIKV,,,68,1,4,...
   1,270.279,1698,5690330.648,246596025.8,186949611.9,...
   2,271.283,1699,569378.051,40396489.5,30710029.19,...
   ```
   - First three columns are always: `row ID`, `row m/z`, `row retention time`
   - Sample columns follow the pattern: `<sample_name>.mzXML Peak area`
   - The bioactivity row has an identifier (e.g., `BioactivityCHIKV`) in `row ID`, empty m/z and RT, and activity values in sample columns
   - Intensity values are peak areas (continuous, non-negative, can be zero)
   - Retention time is in seconds

   **MGF Spectral File** (MS/MS spectra):
   ```
   BEGIN IONS
   FEATURE_ID=9
   PEPMASS=270.279162444
   RTINSECONDS=1697.6755
   SCANS=1
   MSLEVEL=2
   CHARGE=1+
   88.075294 60009.355469
   102.091164 493287.875000
   116.106377 447821.937500
   130.122665 232475.390625
   144.137909 127955.078125
   END IONS
   ```
   - Each spectrum is delimited by `BEGIN IONS` / `END IONS`
   - Header fields: `FEATURE_ID` (links to feature table `row ID`), `PEPMASS` (precursor m/z), `RTINSECONDS` (retention time)
   - Body: pairs of `m/z intensity` values (fragment peaks), one per line
   - `PEPMASS` is the parent ion mass — this is the intact molecule's m/z
   - Fragment peaks are the pieces produced when the parent ion breaks apart

   **Metadata File** (CSV, maps samples to bioactivity):
   ```
   sample_id,filename,activity
   Extract,Extract.mzXML Peak area,68.0
   F_5,F_5.mzXML Peak area,1.0
   F_6,F_6.mzXML Peak area,4.0
   ```
   - `filename` must exactly match column headers in the feature table

### Stage 2: Molecular Networking
**Goal**: Connect structurally similar compounds via MS/MS spectral similarity.

**Key Parameters**:
| Parameter | Typical Range | Guidance |
|-----------|---------------|----------|
| Cosine tolerance | 0.02-0.1 Da | Lower = stricter matching |
| Min matched peaks | 4-18 | More peaks = higher confidence |
| Min cosine score | 0.3-0.7 | Higher = fewer but better edges |
| TopK | 10-50 | Keep only best N edges per node |
| Parent mass tolerance | 0.02-0.1 Da or None | Use to limit comparisons |

**GNPS Defaults** (safe starting point):
- Cosine tolerance: 0.05 Da
- Min matched peaks: 6
- Min cosine score: 0.3
- TopK: 10

**Strict Settings** (publication quality):
- Cosine tolerance: 0.02 Da
- Min matched peaks: 18
- Min cosine score: 0.7
- TopK: 10

#### How Cosine Similarity Works (Algorithm)

Two MS/MS spectra are compared by treating their fragment peaks as vectors and computing cosine similarity on the matched peaks:

1. **Peak Matching**: For each peak in spectrum A, find the closest peak in spectrum B within `cosine_tolerance` (in Da). A peak can only be matched once (greedy assignment, best-first).

2. **Score Calculation**: Given N matched peak pairs with intensities (a₁,b₁), (a₂,b₂), ..., (aₙ,bₙ):
   ```
   cosine = Σ(aᵢ × bᵢ) / (√Σ(aᵢ²) × √Σ(bᵢ²))
   ```
   The result ranges from 0 (no similarity) to 1 (identical fragmentation).

3. **Matched Peaks Count**: Reported alongside the score. Both the score AND the count must exceed thresholds (`min_cosine_score`, `min_matched_peaks`) for an edge to be created.

4. **Intensity Weighting**: Peaks can be weighted by m/z^a × intensity^b. Common settings: `mz_power=0, intensity_power=1` (weight by intensity only, ignore m/z magnitude).

**Modified Cosine** (for analog search): Before matching, shift all fragment peaks of one spectrum by the precursor mass difference (Δm/z = precursor_A − precursor_B). This detects structurally related compounds that differ by a modification (e.g., a hydroxylation adds 16 Da to the precursor, shifting all fragments that retain that moiety). Standard cosine is sufficient when comparing compounds with near-identical precursor masses.

**Spectrum Preprocessing** (apply before comparison):
- Normalize intensities to 0–1 range (divide by max intensity)
- Remove peaks below a relative intensity threshold (e.g., 1%)
- Keep only peaks within a useful m/z range (e.g., 50–2000 Da)
- Require a minimum number of peaks per spectrum (e.g., 5)

#### How to Build the Network from Similarities

1. **Compute all-vs-all pairwise similarities**: For N spectra, compute the N×N similarity matrix. Each cell (i,j) contains the cosine score between spectrum i and j. This is symmetric and has 1.0 on the diagonal.

2. **Optional: Parent mass filtering**: If `parent_mass_tolerance` is set, skip comparison for pairs where |precursor_mz_i − precursor_mz_j| > tolerance. This reduces computation and removes spurious matches between unrelated mass ranges.

3. **TopK filtering**: For each node, sort its neighbors by similarity score (descending). Keep only the top K edges. This prevents hub nodes (common scaffolds) from dominating the network.

4. **Score threshold**: Among the TopK edges, discard any with score < `min_cosine_score`.

5. **Matched peaks threshold**: Also discard edges where the number of matched peaks < `min_matched_peaks`.

6. **Build undirected graph**: An edge between nodes A and B exists if A has B in its filtered TopK OR B has A in its filtered TopK (symmetric union). Edge weight = cosine score.

7. **Node attributes**: Each node stores `precursor_mz` and `retention_time` from the spectrum metadata. These are used later for bioactivity mapping and visualization.

The resulting graph is typically stored as GraphML (Cytoscape-compatible) or as a NetworkX object for further analysis.

### Stage 3: Bioactivity Correlation
**Goal**: Find features whose intensity correlates with bioactivity.

**Statistical Approach** (from Nothias et al. 2018):

The goal is to test, for each of the M features, whether its intensity across samples correlates with bioactivity. The procedure, step by step:

1. **Assemble vectors**: For each feature f, extract its intensity vector **x_f** = [intensity in sample 1, intensity in sample 2, ..., intensity in sample S] across all S samples. Separately, assemble the bioactivity vector **y** = [activity of sample 1, activity of sample 2, ..., activity of sample S]. Both vectors must be in the same sample order.

2. **Z-score normalization** (scaling): For each feature vector **x_f**, compute z-scores independently:
   ```
   x_scaled = (x - mean(x)) / std(x)
   ```
   Do the same for the bioactivity vector **y**. This is equivalent to R's `scale()` function. Each vector is normalized independently (use its own mean and std). Scaling ensures that correlation reflects pattern similarity, not magnitude.

3. **Pearson correlation**: For each feature, compute Pearson r between the scaled intensity vector and the scaled bioactivity vector:
   ```
   r = Σ(x_scaled_i × y_scaled_i) / (n - 1)
   ```
   (After z-score normalization, Pearson r simplifies to this.) The p-value tests H₀: r = 0. Since both vectors are already z-scored, this is equivalent to computing Pearson on the original data — scaling does not change the correlation coefficient, but it is conventional in this workflow and matters if combining with other methods.

4. **Multiple testing correction**: You have M p-values (one per feature). Apply correction across all M tests:
   - **Bonferroni**: p_corrected = p_raw × M. Very conservative — controls family-wise error rate. Use when you need high confidence (few false positives).
   - **FDR (Benjamini-Hochberg)**: Controls false discovery rate. Less conservative — allows more discoveries at the cost of some false positives. Use for exploratory analysis.

5. **Significance threshold**: Mark features with corrected p < 0.05 as significant. These are the candidate bioactive compounds.

**Order of operations matters**: Scale first, then correlate, then correct. Do NOT correct before correlating, and do NOT scale the bioactivity vector using the intensity statistics (each vector uses its own mean/std).

**Alternative Methods**:
- Spearman (rank-based, robust to outliers — use when bioactivity has extreme values or non-linear relationships)
- Random Forest feature importance (captures non-linear relationships, but requires more samples)
- Kendall tau (another rank-based method, more robust with small sample sizes)

**Critical Step**: Match features to network nodes correctly!
- Don't match by ID (feature_120 ≠ spec_119)
- Match by m/z AND retention time
- Use nearest neighbor with tolerance (m/z within 0.01 Da)

### Stage 4: Visualization
**Goal**: Show network with bioactivity overlay.

**Essential Elements**:
1. **Node Size**: Bioactivity correlation strength (|r|)
2. **Node Color**: Retention time or Selectivity Index (SI)
3. **Labels**: m/z values for identification
4. **Interactivity**: Click to highlight connected nodes
5. **Edge Transparency**: Show similarity scores

**Common Visualization Issues**:

#### Issue: Auto-coloring overrides explicit colors
**Symptom**: Nodes appear yellow or wrong colors
**Root Cause**: vis.js uses `group` property to determine color
**Fix**: Remove `group` from node data, use only for color lookup:
```javascript
// WRONG - group property overrides color
{ id: 1, group: 2, color: {background: 'blue'} }

// CORRECT - no group property
{ id: 1, color: {background: 'blue', border: 'darkblue', 
                 highlight: {...}, hover: {...}} }
```

#### Issue: Bioactivity not showing
**Symptom**: All nodes have r = 0 or wrong values
**Root Cause**: Feature-to-node mapping mismatch
**Fix**: Match by nearest m/z + RT, not by ID

## Validation Checklist

### Data Integrity
- [ ] Feature table contains bioactivity row
- [ ] Samples in feature table match MS filenames
- [ ] m/z and RT values present for all features

### Network Quality
- [ ] Expected number of nodes (should match features)
- [ ] Edge count reasonable (10-100 edges/node typical)
- [ ] Similarity scores distributed (not all 0 or all 1)

### Bioactivity Mapping
- [ ] High r values (>0.8) for known bioactive compounds
- [ ] Check specific paper compounds if known
- [ ] Significant p-values after correction

### Visualization
- [ ] No default colors (yellow/orange) appearing
- [ ] Node sizes proportional to |r|
- [ ] Click-to-highlight works
- [ ] Connected nodes show in sidebar

## Parameter Selection Guide

### Choosing Cosine Tolerance
- **0.02 Da**: High-res MS (Orbitrap, Q-TOF) - strict
- **0.05 Da**: Standard resolution - balanced
- **0.1 Da**: Low-res MS - permissive

### Choosing Min Matched Peaks
- **4-6**: Exploratory, complex mixtures
- **10-12**: Balanced
- **18+**: High confidence, clean spectra

### Choosing Min Cosine Score
- **0.1-0.3**: Exploratory, find analogs
- **0.5-0.7**: Publication quality
- **0.8-0.9**: Very high confidence only

### Parent Mass Tolerance
- **Use when**: Want to prevent comparing compounds with very different masses
- **Don't use when**: Looking for analogs with different modifications
- **Typical**: 0.02-0.05 Da or None (compare all)

## Common Bioactivity Assays

| Assay | Readout | Typical Format |
|-------|---------|----------------|
| CHIKV | % inhibition | Row in feature table |
| DENV | EC50/CC50 | Separate metadata file |
| Cytotoxicity | CC50 | Separate metadata file |
| MIC | μg/mL | Row in feature table |

## Expected Outputs

### From Networking
- GraphML file (Cytoscape-compatible)
- Edge list with similarity scores
- Node attributes (m/z, RT)

### From Statistics
- Correlation table (feature, r, p-value, significant)
- Random Forest importance (optional)
- PCoA/HCA plots (optional)

### From Visualization
- Interactive HTML
- PNG/SVG static images

## Paper-Specific Adaptations

When reproducing a specific paper:

1. **Identify their parameters**: Check methods section for cosine tolerance, min peaks
2. **Match their bioactivity assay**: Same cell line, same readout
3. **Use their known compounds**: Validate by finding same m/z values
4. **Replicate their figures**: Same network layout, same color scheme

## Troubleshooting Framework

### Problem: Too few edges
- Lower `min_cosine_score`
- Decrease `min_matched_peaks`
- Increase `cosine_tolerance`

### Problem: Too many edges
- Raise `min_cosine_score`
- Increase `min_matched_peaks`
- Enable `parent_mass_tolerance`

### Problem: No significant correlations
- Check metadata mapping (samples match?)
- Try FDR instead of Bonferroni
- Check bioactivity values (not all same?)
- Try Spearman instead of Pearson

### Problem: Colors wrong in visualization
- Remove `group` property from node data
- Set explicit colors with all states (background, border, highlight, hover)
- Disable vis.js `groups` option

## Key Literature

**Original FBMN Paper**:
Nothias et al. (2018) "Bioactivity-Based Molecular Networking for the Discovery of Drug Leads in Natural Product Bioassay-Guided Fractionation" J. Nat. Prod.

**Key Concepts**:
- Molecular networking (Watrous et al. 2012)
- Feature-based MN (Nothias et al. 2018)
- GNPS platform (Wang et al. 2016)

## Implementation Notes

**Language**: Python (most tools), R (optional stats), JavaScript (visualization)

**Key Libraries**:
- matchms (networking)
- networkx (graph operations)
- scipy.stats (correlations)
- statsmodels (p-value correction)
- vis.js (visualization)

**Data Formats**:
- Input: .mzXML/.mzML, .csv
- Network: .graphml, .gml
- Output: .csv, .html, .png

## Agent Decision Protocol

### When to Ask User

**Always ask before proceeding if:**

1. **Bioactivity assay unclear**
   - No mention of cell line, virus strain, or readout method
   - Bioactivity values don't match typical formats (not % inhibition, not EC50, not MIC)
   - Multiple bioactivity columns with no description

2. **No positive controls available**
   - Paper mentions known bioactive compounds but no m/z values given
   - Cannot validate network without reference compounds
   - Unclear what "active" means (no threshold specified)

3. **Data format unusual**
   - Feature table not from MZmine/Optimus/OpenMS
   - MS data not in .mzXML/.mzML format
   - Missing required columns (m/z, RT, sample intensities)

4. **Parameters far outside typical ranges**
   - Cosine tolerance > 0.5 Da (extremely unusual)
   - Min matched peaks > 50 (likely wrong)
   - Network has < 10 edges or > 10,000 edges per node

5. **Multiple valid approaches possible**
   - Paper mentions both Pearson and Spearman without stating which was used
   - Both FDR and Bonferroni mentioned
   - Analog search vs. standard search unclear

### When to Proceed Autonomously

**Safe to proceed without asking if:**

1. **Standard MZmine output detected**
   - Columns: "row ID", "row m/z", "row retention time", "*.mzXML Peak area"
   - Bioactivity row present ("BioactivityCHIKV", "Activity", etc.)

2. **Common bioactivity assay**
   - CHIKV/DENV/Zika (antiviral)
   - Cytotoxicity (CC50)
   - Antibacterial (MIC)
   - Standard cancer cell lines

3. **Parameters within typical ranges**
   - Cosine tolerance: 0.02-0.1 Da
   - Min matched peaks: 4-18
   - Min cosine: 0.1-0.7
   - TopK: 10-50

4. **Known validation compounds**
   - Paper lists specific m/z values for bioactives
   - Reference standards mentioned
   - Can verify mapping is correct

### Self-Correction Triggers

**Detect these issues → Apply fix automatically:**

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| All nodes yellow/orange | `group` property overriding colors | Remove `group` from node data, keep only for lookup |
| Bioactivity r=0 for all nodes | Feature-to-node mapping failed | Switch from ID matching to m/z+RT matching |
| Zero significant features | P-value correction too strict | Try FDR instead of Bonferroni |
| Too few edges (< 100 total) | Parameters too strict | Lower min_cosine_score, decrease min_matched_peaks |
| Too many edges (> 50,000) | Parameters too loose | Raise min_cosine_score, enable parent_mass_tolerance |
| Known compound not found | m/z tolerance too strict | Increase to 0.01-0.02 Da matching window |
| All similarities = 0 | Cosine tolerance wrong | Check MS resolution, adjust tolerance |
| Node labels not visible | Font size too small or color wrong | Increase to 14-16px, ensure contrast |

### Confidence Score System

**High Confidence** (proceed autonomously):
- Standard formats detected ✓
- Parameters in normal ranges ✓
- Validation compounds match ✓
- Network metrics reasonable ✓

**Medium Confidence** (proceed with logging):
- Unusual but valid parameter combination
- One validation compound mismatch
- Bioactivity format needs parsing

**Low Confidence** (ask user):
- Multiple validation failures
- Unknown data format
- Contradictory parameters
- Missing critical metadata

### Recovery Strategies

**If pipeline fails at Stage 2 (Networking):**
1. Check spectra loaded correctly (not empty)
2. Try lower cosine tolerance (0.05 → 0.02)
3. Disable parent_mass_tolerance if enabled
4. Check min_matched_peaks not > actual peaks per spectrum

**If pipeline fails at Stage 3 (Statistics):**
1. Verify metadata samples match feature table columns
2. Try without scaling (if bioactivity already normalized)
3. Switch correlation method (Pearson ↔ Spearman)
4. Disable p-value correction (for exploratory)

**If visualization is wrong:**
1. Colors wrong → Remove `group` property
2. No bioactivity → Check mapping function
3. Wrong values → Verify nearest-neighbor tolerance
4. Layout messy → Adjust physics parameters

## Learning

When this workflow fails on a new paper:
1. Check if they used classical MN (Dereplicator) vs FBMN (MZmine)
2. Check if they used analog search (allows mass differences)
3. Check their specific bioactivity normalization method
4. Check if they used retention time alignment
5. Check instrument parameters (resolution affects cosine tolerance)

**Build pattern library:**
- Track which parameters work for which instrument types
- Note common bioactivity formats by research field
- Record typical network sizes for different sample types
- Maintain mapping of known compound m/z values by species