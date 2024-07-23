
# thank you to https://makefiletutorial.com/
# debug timestamps with
# make | ts '[%Y-%m-%d %H:%M:%.S]'
# ls -t -l --time-style=full-iso

# set PerfRegions folder (https://github.com/schreiberx/perf_regions) - relative to main folder
## make option PERF_REGIONS ##
ifdef _PERF_REGIONS_FOLDER
	PERF_REGIONS_FOLDER = bench/$(_PERF_REGIONS_FOLDER)
else
PERF_REGIONS_FOLDER:=bench/src/perf_regions
endif

# set bench folder
BENCH := bench

# set tutorial folder
TUTO := tuto

# note : $(MAKE) variable is broken on Windows, use make instead
ifeq ($(OS),Windows_NT)
MAKE = make
endif

.PHONY : tuto perf_regions

all:
	@echo make: $(MAKE)
	-$(MAKE) -C $(BENCH)

run: run_bench
run_bench:
	$(MAKE) -C $(BENCH) run

pre:preprocess
preprocessing:preprocess
preprocess:
	$(MAKE) -C $(BENCH) preprocess

post:postprocess
postprocessing:postprocess
postprocess:
	$(MAKE) -C $(BENCH) postprocess


tuto:
	$(MAKE) -C $(TUTO)
run_tuto:
	$(MAKE) -C $(TUTO) run

clean_all: clean clean_pre
clean: clean_bench
clean_bench:
	-$(MAKE) -C $(BENCH) clean
clean_perf_regions:
	-$(MAKE) -C $(PERF_REGIONS_FOLDER) clean

clean_tuto:
	-$(MAKE) -C $(TUTO) clean

clean_pre:clean_preprocess
clean_preprocess:
	-$(MAKE) -C $(BENCH) clean_pre

### nvfortran exports
NVARCH=Linux_x86_64#`Linux_x86_64 -s`_`Linux_x86_64 -m`
export NVARCH
NVCOMPILERS=/opt/nvidia/hpc_sdk
export NVCOMPILERS
export MANPATH:=$(MANPATH):$(NVCOMPILERS)/$(NVARCH)/24.5/compilers/man
export PATH:=$(NVCOMPILERS)/$(NVARCH)/24.5/compilers/bin:$(PATH)
export PATH:=/usr/local/cuda-12:/usr/local/cuda-12/bin:$(PATH)
export LD_LIBRARY_PATH:=/usr/local/cuda-12:/usr/local/cuda-12/lib:$(LD_LIBRARY_PATH)

perf_regions:
### nvfortran exports
	-$(MAKE) -C $(PERF_REGIONS_FOLDER)/src