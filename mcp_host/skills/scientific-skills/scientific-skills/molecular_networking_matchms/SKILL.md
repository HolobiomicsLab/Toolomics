---
name: Molecular Networking with matchms
description: Comprehensive guide to molecular networking analysis using the matchms Python library for mass spectrometry data
version: 1.0
license: MIT
tags:
  - mass-spectrometry
  - metabolomics
  - molecular-networking
  - bioinformatics
  - cheminformatics
---

# Molecular Networking with matchms

## Overview

Molecular networking is a computational approach for organizing and visualizing mass spectrometry (MS/MS) data by connecting similar spectra in a network graph. This visualization helps researchers:

- **Identify** families of structurally related molecules
- **Discover** new analogs of known compounds
- **Perform dereplication** (identify known compounds)
- **Guide** isolation and characterization of unknowns
- **Explore** chemical diversity in complex samples

**matchms** is a Python library designed for importing, processing, and analyzing MS/MS data to create molecular networks.

### Key Features

- Multiple file format support (MGF, mzML, mzXML, MSP, JSON)
- Flexible spectrum processing pipelines
- Various similarity algorithms (cosine-based, fingerprint-based)
- Network creation and export capabilities
- Integration with GNPS and Cytoscape
- Extensible through companion packages

## Installation

### Prerequisites

- Python 3.10, 3.11, 3.12, or 3.13
- Operating Systems: Linux, macOS, Windows
- Memory: 4-8GB RAM recommended

### Installation Methods

**Conda (Recommended):**

**pip:**

**Development:**

### Related Packages

### Verification

## Quick Start

## Core Concepts

### Spectral Similarity

- **Cosine Similarity**: Compares spectra as vectors in m/z-intensity space
- **Modified Cosine**: Accounts for precursor mass differences (finds analogs)
- **Fingerprint Similarity**: Compares molecular fingerprints

### Network Structure

- **Nodes**: Individual mass spectra (compounds/features)
- **Edges**: Connections with similarity above threshold
- **Clusters**: Groups of related compounds (molecular families)

### Key Principles

1. Similar structures produce similar fragmentation patterns
2. Network topology reveals chemical families
3. Known compounds help annotate unknowns
4. Metadata enhances analysis

## Complete Workflow

### Step 1: Load Spectra

### Step 2: Process Spectra

**Using SpectrumProcessor (Recommended):**

**Using Individual Filters:**

### Step 3: Calculate Similarities

**CosineGreedy (Fast):**

**ModifiedCosine (For Analogs):**

**Parallel Processing:**

### Step 4: Create Network

### Step 5: Export Results

## Code Templates

### Template 1: Basic Workflow

### Template 2: Analog Discovery

### Template 3: Dereplication

### Template 4: Batch Processing

### Template 5: GNPS Preparation

## Parameter Optimization

### Similarity Parameters

**tolerance**: m/z matching tolerance
- High-res MS: 0.005 - 0.05 Da
- Low-res MS: 0.1 - 0.5 Da
- Recommended: 0.02 Da (high-res), 0.1 Da (low-res)

**mz_power**: m/z weighting
- 0.0 (default): No weighting
- 0.5-2.0: Emphasize high m/z peaks

**intensity_power**: intensity weighting
- 0.5: Reduce noise
- 1.0 (default): Linear
- 2.0: Emphasize high peaks

### Network Parameters

**score_cutoff**: similarity threshold
- CosineGreedy: 0.7 - 0.8
- ModifiedCosine: 0.65 - 0.75
- Higher: Sparser networks
- Lower: Denser networks

**max_links**: edges per node
- 5: Very sparse
- 10: Balanced (typical)
- 20: Dense

**top_n**: candidates to consider
- Should be ≥ max_links
- Typical: 1.5-2x max_links

**link_method**:
- 'single': More connections (exploratory)
- 'mutual': Stricter (cleaner networks)

### Filter Parameters

**n_required**: minimum peaks
- 5-10: Typical quality control
- Higher: Better reliability, less data

**n_max**: maximum peaks
- 100 (recommended): Good balance
- Lower: Faster computation

**mz_from/mz_to**: m/z range
- 10/1000: Small molecules
- 50/2000: Larger compounds

## Integration

### GNPS

### Cytoscape

### spec2vec

## Troubleshooting

### No peaks left after filtering

**Cause**: Too aggressive filtering

**Solutions**:
- Reduce `n_required`
- Increase `mz_to`
- Check input data quality

### Empty network

**Cause**: `score_cutoff` too high

**Solutions**:
- Lower cutoff (try 0.6-0.65)
- Increase `max_links`
- Verify spectra are comparable

### ModifiedCosine not working

**Cause**: Missing `precursor_mz`

**Solution**:

### Memory errors

**Solutions**:
- Process in chunks
- Use CosineGreedy (not CosineHungarian)
- Reduce peaks: `reduce_to_number_of_peaks(s, n_max=50)`
- Filter before similarity calculation

### Slow performance

**Solutions**:
- Use CosineGreedy (fastest)
- Reduce peaks early
- Use parallel processing
- Filter dataset first

## Best Practices

### Data Quality
- Validate input data
- Remove low-quality spectra
- Normalize intensities
- Check metadata consistency

### Processing
- Start with default pipelines
- Document all parameters
- Save intermediate results
- Use version control

### Networking
- Test different parameters
- Compare algorithms
- Validate with known compounds
- Use metadata

### Performance
- Batch process large datasets
- Use parallel computation
- Reduce peaks early
- Choose appropriate algorithms

### Reproducibility
- Save all parameters
- Export processed data
- Track library versions
- Share complete workflows

## Data Format: MGF

### Essential Metadata

- `precursor_mz`: Precursor m/z
- `spectrum_id`: Unique identifier
- `charge`: Ion charge state
- `retention_time`: Retention time
- `compound_name`: Compound name
- `smiles`: SMILES string
- `inchi`: InChI string

## Additional Resources

- Documentation: https://matchms.readthedocs.io/
- GitHub: https://github.com/matchms/matchms
- GNPS: https://gnps.ucsd.edu/
- Cytoscape: https://cytoscape.org/

## Summary

matchms provides:

✓ Multiple file formats
✓ Flexible processing
✓ Various similarity algorithms
✓ Network creation and export
✓ Tool integration
✓ Extensible design

This skill covers installation, workflows, API reference, templates, optimization, integration, troubleshooting, and best practices for molecular networking with matchms.
