see https://tex.stackexchange.com/questions/452552/algorithm-pseudocode-in-markdown for pseudocode in pandoc

## Qualities of proposed benchmark suite
### Relevance
### Flexibility
- Configurability
- Example of use
- Based around dictionaries and independent code (modularity)
- Dictionaries
  - -> easy renaming of variables for .csv data and .json metadata for compatibility graphing
  - -> easy to add measurements thanks to configuration of PerfRegions and graphing
### Robustness

## Features
### Summary in UML
### Pseudocode
Draft:
- main function - execution params : iters, array dims if no preprocess
  - warmup bench loop
    - -> see select function
  - bench loop - passed iters
    - select function - preprocessed loop bound, array size and allocation
      - same file
      - module
        - GPU offload
        - CPU
      - in each function: measure performance metrics
  - output summary of performance metrics of selected benchmark
- Then used in postprocess
### Graphing
### Relevant code details
- Codegen
- Job tree
- Scripts (do not modify)
- Libraries

## Further developments
Will be extracted from current [todolist](04_todolist_dev.md)

## (Remove this)
### (For devs)
- (for devs: ``' '`` in output used for ignoring - Fortran already adds spaces everywhere in standard output)