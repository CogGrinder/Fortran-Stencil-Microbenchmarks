
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
	-cd $(PERF_REGIONS_FOLDER) && $(MAKE)
	-cd $(BENCH) && $(MAKE) PERF_REGIONS=../$(PERF_REGIONS_FOLDER)
	-cd $(TUTO) && $(MAKE)

run:
	-cd $(TUTO) && $(MAKE) run
	-cd $(BENCH) && $(MAKE) run
run_bench:
	cd $(BENCH) && $(MAKE) run
run_tuto:
	cd $(TUTO) && $(MAKE) run

clean:
	-cd $(BENCH) && $(MAKE) clean
	-cd $(TUTO) && $(MAKE) clean
