#!/usr/bin/env Rscript

# Load required packages
if (!requireNamespace(xcms, quietly = TRUE)) {
    install.packages(xcms, repos=http://cran.r-project.org)
}
if (!requireNamespace(CAMERA, quietly = TRUE)) {
    install.packages(CAMERA, repos=http://cran.r-project.org)
}
library(xcms)
library(CAMERA)

# Read mzML file
raw_data <- xcmsRaw(storage/QC_0.mzML)

# Detect adducts
xset <- xcmsSet(storage/QC_0.mzML)
xsa <- xsAnnotate(xset)
xsa <- groupFWHM(xsa)
xsa <- findIsotopes(xsa)
xsa <- findAdducts(xsa, polarity=positive) # Assuming positive mode

# Extract results
adducts <- getPeaklist(xsa)
results <- data.frame(
    mz = adducts,
    intensity = adducts,
    adduct = adducts
)

# Write results
write.csv(results, file=adducts.csv, row.names=FALSE)

print(Adduct detection completed successfully)
