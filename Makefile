
# thank you to https://makefiletutorial.com/

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
# -cd $(PERF_REGIONS_FOLDER) && $(MAKE) MODE=debug
	-cd $(PERF_REGIONS_FOLDER) && $(MAKE)
	-cd $(BENCH) && $(MAKE) PERF_REGIONS=../$(PERF_REGIONS_FOLDER)

run: run_bench
run_bench:
	$(MAKE) -C $(BENCH) run

make_tuto:
	$(MAKE) -C $(TUTO)
run_tuto:
	cd $(TUTO) && $(MAKE) run

clean:
# -cd $(PERF_REGIONS_FOLDER) && $(MAKE) clean
	-cd $(BENCH) && $(MAKE) clean
	-cd $(TUTO) && $(MAKE) clean
