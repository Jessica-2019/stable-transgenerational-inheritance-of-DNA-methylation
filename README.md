**For additional information, including a tutorial and sample data for the epigenotyping procedure, check out the [updated documentation](https://schmitzlab.github.io/stable-transgenerational-inheritance-of-DNA-methylation/).**

# Stable inheritance of DNA methylation allows creation of epigenotype maps and the study of epiallele inheritance patterns in the absence of genetic variation

[![DOI](https://zenodo.org/badge/80533401.svg)](https://zenodo.org/badge/latestdoi/80533401)

## Set up

* All python scripts are meant for Python 3.4+
* All scripts import sys, math, glob, multiprocessing, subprocess, os, bisect, and random (all/most come up python)
* Many scripts import pandas, numpy, scipy, and/or sklearn
* To avoid package dependencies, use install [anaconda](https://www.continuum.io/downloads)

* Most R packages can be downloaded through CRAN.

## Program versions
Listed below are program versions used for analysis.
* Python: 3.5.2
* Anaconda: 4.1.6
	- Numpy: 1.11.0
	- Scipy: 0.17.1
	- Scikit: 0.17.1
	- Pandas: 0.17.0
* R: 3.2.4
	- ggplot2: 2.2.1
	- reshape2: 1.4.2
	- ply: 1.8.4
	- dplyr: 0.5.0
	- userfriendlyscience: 0.5-2
	- RVAideMemoire: 0.9-62
	- grid 3.2.4
	- gridExtra 2.2.1

## Utility Scripts
### bioFiles.py
* for handling common file types
* needs to be on the python path or in the same directory as other scripts for all/most other scripts to run correctly

### bth_util.py
* extra utility functions
* needs to be on the python path or in the same directory as other scripts for all/most other scripts to run correctly

### combine_allc_pe.py
Combine multiple allC files at basepair level into one allC file

```
Usage: python combine_allc_pe.py [-f] [-p=num_proc] [-o=out_id] [-c=chrm_list | -cf=fasta_index]
<allc_path> <sample_name> [sample_name]*

Required:
allc_path      path to allC files
sample_name    name of sample; used to find allC files
               when "-f" flag set, file with sample names listed one per line
Optional:
-f             sample names are in file
-p=num_proc    number of processors to use [default 1]
-o=out_id      output file identifier [default "combined"]
-c=chrm_list   comma-separated list of chrms to use
-cf=fasta_index    fasta index file with chrms to use
```

### filter_allc_coverage_pe.py
Creates new allc files for all input samples that only includes information about positions which have at least minCov reads for each sample

expects all chromosomes in one allC file

```
Usage: python filter_allc_coverage.py [-v=min_cov] <allc_path> <sample1> [sampleN]*

Required:
allc_path     path to allC files
sampleN       name of sample; used to find allC files

Optional:
-v=min_cov    min coverage for positions to include [default 3]
-p=num_proc   number of processors to use [default 1]
```

### unmethylate_allc_pe.py
Creates pseudo-allC file where all positions are unmethylated

Output file has same name as input file with "-unmethylated" appended

```
Usage: python unmethylate_allc_pe.py [-f] [-p=num_proc] [-v=NA] <allc_file> [allc_file]*

Required:
allc_file      allC file to unmethylated
               when "-f" set, file with list of allC files
Optional:
-f             allC files names listed in the file
-p=num_proc    number of processors to use [default 1]
-v=coverage    coverage for each position [default as-is in input]
```

## Transgenerational MA lines

### dmr_gen_counts.py
Used for between-generation computations of methylation

expects all chromosomes in one allC file and when minCov is set, minCov is output from `filter_allc_coverage.py`

```
Usage: python dmr_gen_counts.py [-o=outID] [-m=methType] [-p=numProc] [-v=min_cov]
 <dmrFile> <allcPath> <sample1> <sample2> [sampleN]*

Required:
dmrFile     tab-delimited file (BED format) with DMRs to investigate
allcPath    Path to allC files; all chrms together for each sample
sample      sample names as part of the allC file

Optional:
-o=outID       identifier for output file [default "out"]
-m=methType    methylation type [default C]
-p=numProc     num. of processors to use [default 1]
-v=minCov      min. coverage used as part of allC file name [default None]
```

### dmr_gen_switches.py
Identifies significant methylation changes between generations using Fisher's exact test and minimum change in methylation

Input file is output from `compare_dmrs_gens_pe.py`

```
Usage: python dmr_gen_switches.py [-wm] [-n=num_c_thresh] [-m=meth_thresh] [-d=length_thresh]
[-f=fdr] [-o=outID] <in_file>

Required:
in_file	           tab-delimited file of DMRs and read counts

Optional:
-wm                methylation threshold is for raw methyl difference 
                   not percent difference
-n=num_c_thresh    min number of cytosines in region to be considered for 
                   analysis [default 10]
-d=lenth_thresh    min length of dmr in bp [default 40]
-m=meth_thresh     min methylation change btwn generations to be considered a 
                   switch [default 0.3]
-f=fdr             FDR value for significant switches [default 0.05]
-o=out_id          identifier for output files [default uses input file name]
```

### dmr_file_to_bed.py
Converts the switches output of `dmr_gen_switches.py` to BED file

```
Usage: python dmr_file_to_bed.py [-v=score_thresh] [-p=name_prefix] [-o=outID] <in_file>

Required:
in_file            input file of DMRs

Optional:
-v=score_thresh    min score to include in output [default -1, no threshold]
-p=name_prefix     prefix for naming features [default None]
-o=outID           identifier for output file [default uses input file name]
```

### dmr_counts_pe.py
Computes weighted methylation over regions

```
Usage: python dmr_counts_pe.py [-o=outID] [-m=methTypes] [-p=numProc] [-v=minCov] <dmrFile>
<allcPath>  <sample1> <sample2> [sampleN]*

Required:
dmrFile        tab-delimited file (BED format) with DMRs to investigate
allcPath       Path to allC files; all chrms together for each sample
sample         sample names as part of the allC file

Optional:
-o=outID       identifier for output file [default "out"]
-m=methType    methylation context to include [default C]
-p=numProc     number of processors [default 1]
-v=minCov      min. coverage used as part of allC file name [default None]
```

## Epigenotyping

### find_all_mpos_dif_pe.py
get individual positions that differ based on binomial test

Uses allC files specific to each chromosome

```
Usage: python find_all_mpos_dif_pe.py [-v=min_cov] [-c=chrm_list] [-o=out_id] [-p=num_proc]
[-m=meth_types] <allc_path> <sample1_name> <sample2_name>

Required:
allc_path      path to allc files
sample_name    names of samples to compare

Optional
-v=min_cov     min coverage to include a position [default 3]
-o=out_id      string for output file name [default "out"]
-c=chrm_list   comma-separated list of chrms [default arabidopsis]
-p=num_proc    num processors to use [default 1]
-m=meth_types  comma-separated list of "CG", "CHG", and/or "CHH" [default all]
```

### filter_pos_gene_gbm.py
Filter a list of positions by gene-body methylation and/or CDS

```
Usage: python filter_pos_gene_gbm.py [-cds] [-v] <pos_file> <gbm_file> <gff_file>

Required:
pos_file    position file, tab-delimited BED format, to be filtered
gbm_file    file with list of gbM genes, one gene per line
            use "none" or "na" to use all genes
gff_file    GFF formatted file with genes

Optional:
-cds        use CDS annotation not gene
-v          include coordinates opposite of what is specified
```

### weighted_meth_by_pos.py
Compute weighted methylation at each position specified, eliminating positions not covered by minCov reads in all samples

Position list is from `find_all_mpos_dif_pe.py` or `filter_pos_gene_gbm.py`

```
Usage: python weighted_meth_by_pos_pe.py [-o=out_id] [-v=min_cov] [-p=num_proc] <pos_list>
<allc_path> <sample_name> [sample_name]*

Required:
pos_list       tab-delimited list with chrm and bp position
allc_path      path to allc files
sample_name    names of samples to include

Optional:
-v=min_cov     min coverage to include a position [default 3]
-o=out_id      string for output file name [default "out"]
-p=num_proc    num processors to use [default 1]
```

### decodingpath.py
Utility script used by `epigenotyping_pe_combbin_fb-vit_cent.py`; includes code for forward-backward decoding and Viterbi decoding

### transitions.py
Utility script used by `epigenotyping_pe_combbin_fb-vit_cent.py`; computes the transition matrix

### epigenotyping_pe_v1.7.3.py
Major script which generates epigenotype map of samples based on *mother* and *father* methylomes

Input file is output of `weighted_meth_by_pos_pe.py`

```
Usage:  python epigenotyping_pe_v1.7.3.py [-q] [-n-mpv] [-t-out] [-g=generation]
        [-c=bin_thresh] [-d=decoding_type] [-p=num_proc] [-o=out_id] [-m=mother_
        samples][-f=father_samples] [-b=bin_size] [-t=centromere] <input_file>

Requried:
input_file	tab-delimited file of of weighted methylation by position for samples

Optional:
-q                quiet; do not print progress
-h                print help and exit
-n-mpv            do not check for systematic mid-parent bias
-t-out            write transition matrix to file
-g=generation     generation of self-crossing; used to determine classification
                  probabilities; use 0 for uniform weight [default 2]
-d=decode_type    decoding type to use (capitlization ignored) [default B]
                  Viterbi="v" or "viterbi"
                  Forward-Backward="forwardbackward", "f" or "fb"
                  All (FB and Vit independently)="all" or "a"
                  Both (FB then Vit)="both" or "b"
                  Off="false", "none", or "n"
-o=out_id         identifier for output file [default "out" or variation of
                  input file name]
-p=num_proc       number of processors [default 1
-c=bin_thresh     minimum number of features per bin to be classified
                  groups bins to reach this number [default 3
-m=mother_label   comma-separated sample name(s) of mother
                  [default mother]
-f=father_label   comma-separated sample name(s) of father
                  [default father]
-b=bin_size       size of bins in bp [default 100kbp]
-t=centromere     centromere coordinates as "start,end"; can include multipe
                  centromeres as "start1,end1,start2,end2..." [default None]
```

### simulation_accuracy.py
Compute various accuracy scores comparing the assigned epigenotype and predicted epigenotype

Input file is created from R script, columns bin, sample, prediction, test, expected

```
Usage: python simulation_accuracy.py [-q] [-o=out_id] <input_file>
Required:
input_file    csv file with expected and predicted epigenotype
Optional:
-o=out_id     output identifier
-q            quiet; don't print progress
```
### find_crossovers.py
Identify crossovers from an epigenotype map

Input file is output of `epigenotyping_pe_combbin.py`

```
Usage: python find_crossovers.py [-c=prediction_column] [-o=out_id] <input_file>

Required:
input_file    tab delimited file with samples epigenotype per bin

Optional:
-o=out_id             output identifier [default variation of
                      input file name
-c=prediction_column  label of column to use as final epigenotype
                      [default "vit.prediction"]
```

## Epigenotyping compared to SNPs


### decode_pileup_pe.py
Decodes and combines input pileup files into easier to read format

Assumes all input pileup files contain the same positions

In the output file, [A,C,G,T] indicate forward-strand read and [a,c,g,t] indicate reverse-strand read

```
Usage: python decode_pileup_pe.py [-o=out_id] [-p=num_proc] <pileup_file> [pileup_file]*
Required:
pileup_file    pileup file for a sample; output from samtools pileup

Optional:
-o=out_id         identifier for output file [default "out"]
-p=num_proc       number of processors [default 1]
```

### pileup_genotype_pe.py
Based on the unique nt at each position between mother and father samples, guesses the genotype of the samples. Positions not distinguishable between parents are eliminated.

Input file is output of `decode_pileup_pe.py`

```
Usage: python pileup_genotype_pe.py [-o=out_id] [-p=num_proc] [-m=mother_label] [-f=father_label] [-v-min_cov] <decoded_pileup_file>

Required
decode_pileup_file    tab-delimited input file; output of decode_pileup_pe.py

Optional:
-o=out_id         identifier for output file [default variation of
                  input file name]
-v=min_cov        min number of reads needed to support genotype [default 1]
-p=num_proc       number of processors [default 1]
-m=mother_label   sample name of mother [default mother]
-f=father_label   sample name of father [default father]
```
