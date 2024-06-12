### bench makefile ###

FC:=gfortran
CC:=gcc
CXX:=g++
FFLAGS = -cpp -Wall -Wextra -O3

all:
	make -C $(PERFREGION_SRC) --silent
	make bench_library
	make $(MAIN)

run: run_main

MAIN:= main

# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif


### compilation flags ###
BUILD_DIR := build
BENCH_LIB_DIR   := lib

BENCH_LIB := -L$(BENCH_LIB_DIR) -l:library.a
# TODO : try .so library - you must also modify the Makefile in src
# BENCH_LIB := -L$(BENCH_LIB_DIR) -l:library.so
# TODO : try not using .a or .so
# BENCH_LIB := -L$(BENCH_LIB_DIR)

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to 
PERF_REGIONS_FOLDER:=../perf_regions
ifdef PERF_REGIONS
	PERF_REGIONS_FOLDER = $(PERF_REGIONS)
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(BUILD_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}


bench_library : 
	make -C src
	make $(BUILD_DIR)/benchmark_implementations.o
	make -C src library
	@touch $(BENCH_LIB_DIR)/library.a
$(BUILD_DIR)/benchmark_implementations.o : $(BUILD_DIR)/benchmark_implementations.mod
	@echo
$(BUILD_DIR)/benchmark_implementations.mod : src/benchmark_implementations.f90
	./perf_regions_instrumentation.py cleanup
	${FC} -c src/benchmark_implementations.f90 -o $(BUILD_DIR)/benchmark_implementations.o -cpp ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(BENCH_LIB_DIR) -J$(BUILD_DIR)
# -cpp option does preprocessing

$(MAIN) : main.f90
	./perf_regions_instrumentation.py cleanup
	${FC} -g -o $(MAIN) main.f90 -cpp ${CFLAGS} ${BENCH_LIB} ${PERFREGION_LINKFLAGS}
# -cpp option does preprocessing

run_main : all
# TODO : fix environment variable passing to script
# export BENCH_EXECUTABLE='$(MAIN)'
# export PERF_REGIONS='$(PERF_REGIONS_FOLDER)'
	./run_benches.sh

#main.o:
#	${FC} -c main.F90 ${CFLAGS} ${PERFREGION_LINKFLAGS}


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean:
	rm *.exe
	rm *.o
else
clean:
	./perf_regions_instrumentation.py cleanup
	-rm -f main main.o benchmark_implementations.o output.txt
	-rm -f perf_region_list.txt
	-rm build/*
	-rm src/*.o src/*.mod
	-rm lib/library.a
endif