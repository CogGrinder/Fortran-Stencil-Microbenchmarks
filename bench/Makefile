### bench makefile ###

FC:=gfortran
FFLAGS = -cpp -Wall -Wextra -O3

all: build_bench
run: run_main
clean: clean_bench

MAIN:= main

# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif


### compilation flags ###
BENCH_LIB_DIR   := lib
BENCH_LIB := -Lbuild -L$(BENCH_LIB_DIR) -l:library.a -Ibuild

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to 
PERF_REGIONS_FOLDER:=../perf_regions
ifdef PERF_REGIONS
	PERF_REGIONS_FOLDER = $(PERF_REGIONS)
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(PERFREGION_SRC) -O0 -g
LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}


build_bench:
	make -C $(PERFREGION_SRC)
	make -C src
	make -C src library
# make benchmark_implementations
	make $(MAIN)


# BUILD_DIR := build
# benchmark_implementations : benchmark_implementations.o
# @echo
# benchmark_implementations.o : $(BUILD_DIR)/benchmark_implementations.mod
# $(BUILD_DIR)/benchmark_implementations.mod : benchmark_implementations.f90
# make -C src
# ./perf_regions_instrumentation.py cleanup
# ${FC} ${FFLAGS} -c benchmark_implementations.f90 -J$(BUILD_DIR) -I$(BUILD_DIR) ${CFLAGS} ${LINKFLAGS}
# -cpp option does preprocessing

$(MAIN) : main.f90
	./perf_regions_instrumentation.py cleanup
	${FC} -g -o $(MAIN) main.f90 -cpp ${CFLAGS} ${BENCH_LIB} ${LINKFLAGS}
# -cpp option does preprocessing

run_main : build_bench
# TODO : fix environment variable passing to script
# export BENCH_EXECUTABLE='$(MAIN)'
# export PERF_REGIONS='$(PERF_REGIONS_FOLDER)'
	./run_benches.sh

#main.o:
#	${FC} -c main.F90 ${CFLAGS_PERFREGION} ${LINKFLAGS_PERFREGION}


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean_bench:
	rm *.exe
	rm *.o
else
clean_bench:
	./perf_regions_instrumentation.py cleanup
	-rm -f main main_perf_region main.o file.csv
	-rm -f perf_region_list.txt
	-rm build/*.mod
	-rm src/*.o src/*.mod
	-rm lib/library.a
endif