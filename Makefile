
# thank you to https://makefiletutorial.com/

# set PerfRegions folder (https://github.com/schreiberx/perf_regions)
PERF_REGIONS := perf_regions

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
	-cd $(PERF_REGIONS) && $(MAKE)
	-cd $(BENCH) && $(MAKE)
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
