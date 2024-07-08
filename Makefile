
# thank you to https://makefiletutorial.com/
# debug timestamps with
# make | ts '[%Y-%m-%d %H:%M:%.S]'
# ls -t -l --time-style=full-iso

# set PerfRegions folder (https://github.com/schreiberx/perf_regions) - relative to main folder
PERF_REGIONS_FOLDER:=perf_regions
## make option PERF_REGIONS ##
ifdef PERF_REGIONS
	PERF_REGIONS_FOLDER = $(PERF_REGIONS)
endif

# set bench folder
BENCH := bench

# set tutorial folder
TUTO := tuto

# note : $(MAKE) variable is broken on Windows, use make instead
ifeq ($(OS),Windows_NT)
MAKE = make
endif

all:
	@echo make: $(MAKE)
# add MODE=debug as a trailing option for debugging
# -$(MAKE) -C $(PERF_REGIONS_FOLDER) MODE=debug
	-$(MAKE) -C $(PERF_REGIONS_FOLDER) --silent
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


make_tuto:
	$(MAKE) -C $(TUTO)
run_tuto:
	$(MAKE) -C $(TUTO) run

clean_all: clean clean_perf_regions clean_tuto
clean:
	-$(MAKE) -C $(BENCH) clean

clean_perf_regions:
	-$(MAKE) -C $(PERF_REGIONS_FOLDER) clean

clean_tuto:
	-$(MAKE) -C $(TUTO) clean

clean_pre:clean_preprocess
clean_preprocess:
	cd bench/preprocess;python3 ./test_codegen.py clean