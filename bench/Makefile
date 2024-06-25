### bench makefile ###

FC:=gfortran
CC:=gcc
CXX:=g++
FFLAGS = -cpp -O3 #-Wall -Wextra 

ifndef ALLOC_MODE
export ALLOC_MODE=NONE
endif

ifndef SIZE_MODE
export SIZE_MODE=NONE
endif

all: main
run: run_main
pre:preprocessing
preprocessing:
	cd preprocess;python3 test_codegen.py all;./run_bench_tree.sh


# Here is the selector for which main to compile
SUFFIX.:=
SUFFIX.NONE := _defaultalloc
SUFFIX.ALLOC := _alloc
SUFFIX.STATIC := _static

SUFFIX.${ALLOC_MODE}. :=						${SUFFIX.${ALLOC_MODE}}
SUFFIX.${ALLOC_MODE}.NONE :=					${SUFFIX.${ALLOC_MODE}}_defaultsize
SUFFIX.${ALLOC_MODE}.SMALLER_THAN_L3 :=			${SUFFIX.${ALLOC_MODE}}_smallerl3
SUFFIX.${ALLOC_MODE}.SLIGHTLY_SMALLER_THAN_L3 :=${SUFFIX.${ALLOC_MODE}}_ssmallerl3
SUFFIX.${ALLOC_MODE}.SLIGHTLY_BIGGER_THAN_L3 :=	${SUFFIX.${ALLOC_MODE}}_sbiggerl3
SUFFIX.${ALLOC_MODE}.BIGGER_THAN_L3 :=			${SUFFIX.${ALLOC_MODE}}_biggerl3

MAIN:= bench${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}}

# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif



####################### compilation flags ########################
BIN_DIR := bin
BUILD_DIR := build
LIB_DIR   := lib

BENCH_LIB := -L$(LIB_DIR) -l:library.a
# TODO : try .so library - you must also modify the Makefile in src
# BENCH_LIB := -L$(LIB_DIR) -l:library.so
# TODO : try not using .a or .so
# BENCH_LIB := -L$(LIB_DIR)

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to 
PERF_REGIONS_FOLDER:=../perf_regions

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(BUILD_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}

####################### main compilation #######################
main : $(BIN_DIR)/$(MAIN)
	@export |grep ALLOC_MODE
	@export |grep SIZE_MODE
$(BIN_DIR)/$(MAIN) : main.f90 $(PERF_REGIONS_FOLDER)/build/libperf_regions.so $(LIB_DIR)/library.a | $(BIN_DIR)
	@./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -g -o $(BIN_DIR)/$(MAIN) main.f90 -D${ALLOC_MODE} -D${SIZE_MODE} ${CFLAGS} ${BENCH_LIB} ${PERFREGION_LINKFLAGS}

run_main : $(BIN_DIR)/$(MAIN)
	./run_benches.sh


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean:
	rm *.exe
	rm *.o
else
clean:
	./perf_regions_instrumentation.py cleanup
	-@rm -f main main.o output.txt
	-@rm -f perf_region_list.txt
	-@rm build/*
	-@rm bin/*
	-@rm lib/*
endif


# DIRECTORIES
$(BIN_DIR) :
	-@mkdir $@
$(LIB_DIR)/library.a :
	make -C src library
$(PERF_REGIONS_FOLDER)/build/libperf_regions.so :
	make -C $(PERFREGION_SRC)
#--silent