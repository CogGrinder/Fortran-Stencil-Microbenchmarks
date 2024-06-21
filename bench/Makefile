### bench makefile ###

FC:=gfortran
CC:=gcc
CXX:=g++
FFLAGS = -cpp -Wall -Wextra -O3

all:
	make -C $(PERFREGION_SRC) --silent
	make bench_library
	make $(BIN_DIR)/$(MAIN)

run: run_main

MAIN:= bench

# Here is the selector for which main to compile
SUFFIX.:= 




# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif


BIN_DIR := bin
BUILD_DIR := build
BENCH_LIB_DIR   := lib



### compilation flags ###
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
	${FC} ${FFLAGS} -c src/benchmark_implementations.f90 -o $(BUILD_DIR)/benchmark_implementations.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(BENCH_LIB_DIR) -J$(BUILD_DIR)

$(BUILD_DIR)/benchmark_2D_CPU.o : $(BUILD_DIR)/benchmark_2D_CPU.mod
	@echo
$(BUILD_DIR)/benchmark_2D_CPU.mod : src/benchmark_2D_CPU.f90
	./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c src/benchmark_2D_CPU.f90 -o $(BUILD_DIR)/benchmark_2D_CPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(BENCH_LIB_DIR) -J$(BUILD_DIR)


$(BUILD_DIR)/benchmark_2D_GPU.o : $(BUILD_DIR)/benchmark_2D_GPU.mod
	@echo
$(BUILD_DIR)/benchmark_2D_GPU.mod : src/benchmark_2D_GPU.f90
	./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c src/benchmark_2D_GPU.f90 -o $(BUILD_DIR)/benchmark_2D_GPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(BENCH_LIB_DIR) -J$(BUILD_DIR)

$(BIN_DIR)/$(MAIN) : main.f90 | $(BIN_DIR)
	./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -g -o $(BIN_DIR)/$(MAIN) main.f90 ${CFLAGS} ${BENCH_LIB} ${PERFREGION_LINKFLAGS}
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
	-rm -f main main.o output.txt
	-rm -f perf_region_list.txt
	-rm build/*
	-rm bin/*
	-rm src/*.o src/*.mod
	-rm lib/library.a
endif


# DIRECTORIES
$(BIN_DIR) :
	-@mkdir $@