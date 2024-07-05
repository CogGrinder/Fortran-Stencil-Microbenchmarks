### bench makefile ###

FC:=gfortran
CC:=gcc
CXX:=g++
FFLAGS = -cpp -O3 #-Wall -Wextra 

# default value variables - managed with export to avoid explicit passing to recursive make
# for details on alternatives:
# see https://www.gnu.org/software/make/manual/html_node/Setting.html

ifndef ALLOC_MODE
export ALLOC_MODE=NONE
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


all: main
run: run_main
.PHONY: preprocess postprocess
pre:preprocess
preprocessing:preprocess
preprocess:
	cd preprocess;python3 test_codegen.py all ACCURACY_SCORE=${ACCURACY_SCORE} --v;./run_bench_tree.sh

pre_old:preprocess_old
preprocess_old:
	cd preprocess;python3 test_codegen.py all_old ACCURACY_SCORE=${ACCURACY_SCORE};./run_bench_tree.sh

post:postprocess
postprocessing:postprocess
postprocess:
	cd postprocess;./collect_data_csv.sh;python3 test_generate_graph.py
clean_pre:
	cd preprocess;python3 test_codegen.py clean

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

SIZE_MODE_IS_NUMBER :=$(shell echo "$(SIZE_MODE)" | grep -Eq '^[0-9]*$$' && echo "1" || echo "0")
ifeq ($(SIZE_MODE_IS_NUMBER),1)
	SUFFIX.${ALLOC_MODE}.${SIZE_MODE} := ${SUFFIX.${ALLOC_MODE}}_${shell printf "%02d" $(SIZE_MODE)}Mb
endif

SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.  := ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}}
SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.1 := ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}}_sizecompiled
SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.0 := ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}}_sizenotcompiled

SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}. 				:= ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}}_defaultkernel
SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}.X_KERNEL 		:= ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}}_xkernel
SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}.Y_KERNEL 		:= ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}}_ykernel
SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}.SIZE_5_KERNEL 	:= ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}}_size5kernel
SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}.DEFAULT_KERNEL := ${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}}_defaultkernel


# MAIN:= bench${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}}
MAIN:= bench${SUFFIX.${ALLOC_MODE}.${SIZE_MODE}.${SIZE_AT_COMPILATION}.${KERNEL_MODE}}

# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif



####################### compilation flags ########################
BIN_DIR := bin
BUILD_DIR := build
SRC_DIR := src
LIB_DIR   := lib

BENCH_LIB := -L$(LIB_DIR) -l:library.a
# TODO : try .so library - you must also modify the Makefile in src
# BENCH_LIB := -L$(LIB_DIR) -l:library.so
# TODO : try not using .a or .so
# BENCH_LIB := -L$(LIB_DIR)

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next
ifdef _PERF_REGIONS_FOLDER
PERF_REGIONS_FOLDER:=$(_PERF_REGIONS_FOLDER)
else
PERF_REGIONS_FOLDER:=../perf_regions
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(BUILD_DIR) -I$(SRC_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}

####################### main compilation #######################
print_main:
	echo from make:___$(BIN_DIR)/$(MAIN)
main : $(BIN_DIR)/$(MAIN)
$(BIN_DIR)/$(MAIN) : main.f90 $(PERF_REGIONS_FOLDER)/build/libperf_regions.so $(LIB_DIR)/library.a | $(BIN_DIR)
	@export |grep ALLOC_MODE
	@export |grep SIZE_MODE
	@export |grep SIZE_AT_COMPILATION
	@export |grep KERNEL_MODE
	${FC} ${FFLAGS} -g -o $(BIN_DIR)/$(MAIN) main.f90 -DALLOC_MODE=${ALLOC_MODE} -DSIZE_MODE=${SIZE_MODE} -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNX=${NX} -DNY=${NY} ${CFLAGS} ${BENCH_LIB} ${PERFREGION_LINKFLAGS}
	@touch $(BIN_DIR)/$(MAIN)

run_main : $(BIN_DIR)/$(MAIN)
	./run_benches.sh


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean:
	rm -f *.exe
	rm -f *.o
else
clean:
	./perf_regions_instrumentation.py cleanup
	rm -f main main.o output.txt
	rm -f perf_region_list.txt
	rm -f build/*
	rm -f bin/*
	rm -f lib/*
endif

# MODULE LIBRARY COMPILATION - # TODO : fixing make dependencies checking by using no ../
MODULE_f90 := $(wildcard $(SRC_DIR)/*.f90)
MODULE_O := $(patsubst $(SRC_DIR)/%.f90,$(BUILD_DIR)/%.o, $(MODULE_f90))
# using .SECONDARY
.SECONDARY : $(MODULE_O) 
# .LOW_RESOLUTION_TIME : $(MODULE_f90)
# see https://www.gnu.org/software/make/manual/html_node/Chained-Rules.html
$(LIB_DIR)/library.a : $(MODULE_O)
	make -C src library
	@touch $(LIB_DIR)/library.a
$(MODULE_O) : #$(MODULE_f90)
# @echo .f90 files newer than .o files :
# @echo $?
	make -C src library --silent
#$(patsubst $(BUILD_DIR)/%.o, ../$(BUILD_DIR)/%.o, $@)

# library: $(LIB_DIR)/library.a

# # default rule
# $(BUILD_DIR)/%.o $(BUILD_DIR)/%.mod : $(SRC_DIR)/%.f90 | $(BUILD_DIR)
# 	$(FC) $(FFLAGS) -c $< -o $(basename $@).o -J$(BUILD_DIR)
# 	@touch $@

# $(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : $(SRC_DIR)/benchmark_implementations.f90 | $(BUILD_DIR)
# # ./perf_regions_instrumentation.py cleanup
# 	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_implementations.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)
# 	@touch $@

# $(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : $(SRC_DIR)/benchmark_2D_CPU.f90 | $(BUILD_DIR)
# # ./perf_regions_instrumentation.py cleanup
# 	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2D_CPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)
# 	@touch $@


# $(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : $(SRC_DIR)/benchmark_2D_GPU.f90 | $(BUILD_DIR)
# # ./perf_regions_instrumentation.py cleanup
# 	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2D_GPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)
# 	@touch $@

# # Additional rules :
# $(BUILD_DIR)/benchmark_2D_CPU.o : $(BUILD_DIR)/tools.mod
# $(BUILD_DIR)/benchmark_2D_GPU.o : $(BUILD_DIR)/tools.mod


# # $(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : benchmark_implementations.f90
# # 	make -C .. build/benchmark_implementations.o
# # $(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : benchmark_2D_CPU.f90
# # 	make -C .. build/benchmark_2D_CPU.o
# # $(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : benchmark_2D_GPU.f90
# # 	make -C .. build/benchmark_2D_GPU.o

# $(LIB_DIR)/library.a : $(MODULE_O) | $(LIB_DIR)
# 	ar cr $(LIB_DIR)/library.a $(MODULE_O)
# 	@touch $(LIB_DIR)/library.a


# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) $(BIN_DIR) :
	-@mkdir $@

$(PERF_REGIONS_FOLDER)/build/libperf_regions.so :
	make -C $(PERFREGION_SRC)
#--silent