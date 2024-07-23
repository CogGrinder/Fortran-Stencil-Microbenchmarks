### bench makefile ###

# use F90 flag for Fortran compiler
F90?=gfortran
CC:=gcc
CXX:=g++
FFLAGS = -cpp -O3 #-Wall -Wextra 

### nvfortran exports - used by all nvfortran compilations
NVARCH=Linux_x86_64#`Linux_x86_64 -s`_`Linux_x86_64 -m`
export NVARCH
NVCOMPILERS=/opt/nvidia/hpc_sdk
export NVCOMPILERS
export MANPATH:=$(MANPATH):$(NVCOMPILERS)/$(NVARCH)/24.5/compilers/man
export PATH:=$(NVCOMPILERS)/$(NVARCH)/24.5/compilers/bin:$(PATH)
export PATH:=/usr/local/cuda-12:/usr/local/cuda-12/bin:$(PATH)
export LD_LIBRARY_PATH:=/usr/local/cuda-12:/usr/local/cuda-12/lib:$(LD_LIBRARY_PATH)

# default value variables - managed with export to avoid explicit passing to recursive make
# for details on alternatives:
# see https://www.gnu.org/software/make/manual/html_node/Setting.html

####################### defaults ########################

ifndef DIM
export DIM=2
endif

ifndef ALLOC_MODE
export ALLOC_MODE=DEFAULT_ALLOC
endif

ifndef MODULE_MODE
export MODULE_MODE=0
endif

ifndef SIZE_MODE
export SIZE_MODE=NONE
endif

ifndef SIZE_AT_COMPILATION
export SIZE_AT_COMPILATION=0
endif

ifndef KERNEL_MODE
export KERNEL_MODE=DEFAULT_KERNEL
endif

# used in codegen for scaling number of iterations
SPEED?=1

####################### .PHONY targets ########################

all: main
run: run_main
.PHONY: preprocess postprocess
pre:preprocess
preprocessing:preprocess
preprocess:
	cd preprocess;python3 codegen.py -M all -A=${SPEED} --v;./run_bench_tree.sh

pre_old:preprocess_old
preprocess_old:
	cd preprocess;python3 codegen.py -M all_old -A=${SPEED};./run_bench_tree.sh

post:postprocess
postprocessing:postprocess
postprocess:
	cd postprocess;./collect_data_csv.sh;python3 generate_graph.py
clean_pre:
	cd preprocess;python3 codegen.py -M clean

####################### mainfile selector ########################

# use MAIN variable from export as filename
ifndef MAIN
MAIN:=bench_default
endif
# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif

####################### compilation flags ########################
BIN_DIR := bin
BUILD_DIR := build
SRC_DIR := src
LIB_DIR   := lib

BENCH_LIB := -L$(LIB_DIR) -lbench
# TODO : try .so library - you must also modify the Makefile in src
# BENCH_LIB := -L$(LIB_DIR) -l:library.so
# TODO : try not using .a or .so
# BENCH_LIB := -L$(LIB_DIR)

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in a subfolder of src
ifdef _PERF_REGIONS_FOLDER
PERF_REGIONS_FOLDER:=$(_PERF_REGIONS_FOLDER)
else
PERF_REGIONS_FOLDER:=src/perf_regions
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CPPMACROS:=-DDIM=${DIM} -DALLOC_MODE=${ALLOC_MODE} -DMODULE_MODE=${MODULE_MODE} -DSIZE_MODE=${SIZE_MODE} -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNI=${NI} -DNJ=${NJ}
CFLAGS:= $(CPPMACROS) -I$(BUILD_DIR) -I$(SRC_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}
####################### main compilation #######################
print_main:
	echo from make:___$(BIN_DIR)/$(MAIN)
main : $(BIN_DIR)/$(MAIN)
# use of | https://stackoverflow.com/questions/64036620/what-is-the-use-of-or-operator-in-dependency-list
$(BIN_DIR)/$(MAIN) : main.F90 $(PERF_REGIONS_FOLDER)/build/libperf_regions.so $(LIB_DIR)/libbench.a | $(BIN_DIR)
	@export |grep ALLOC_MODE
	@export |grep SIZE_MODE
	@export |grep SIZE_AT_COMPILATION
	@export |grep KERNEL_MODE
	${F90} ${FFLAGS} -g -o $(BIN_DIR)/$(MAIN) main.F90 ${CFLAGS} ${BENCH_LIB} ${PERFREGION_LINKFLAGS}
	@touch $(BIN_DIR)/$(MAIN)

run_main : $(BIN_DIR)/$(MAIN)
	./run_default.sh


clean:
	make -C src/perf_regions clean
	rm -f tmp.txt out.csv
	rm -f build/*
	rm -f bin/*
	rm -f lib/*

####################### dependency rules #######################

# MODULE TARGETS
MODULE_F90 := $(wildcard $(SRC_DIR)/*.F90)
MODULE_O := $(patsubst $(SRC_DIR)/%.F90,$(BUILD_DIR)/%.o, $(MODULE_F90))
$(LIB_DIR)/libbench.a : $(MODULE_O)
	make -C src ../$(LIB_DIR)/libbench.a
	@touch $(LIB_DIR)/libbench.a
$(BUILD_DIR)/%.o : $(SRC_DIR)/%.F90
	make -C src

# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) $(BIN_DIR) :
	-@mkdir $@

# PERF_REGIONS
# add MODE=debug as a trailing option for debugging
# -$(MAKE) -C $(PERF_REGIONS_FOLDER) MODE=debug
$(PERF_REGIONS_FOLDER)/build/libperf_regions.so :
	make -C $(PERFREGION_SRC)