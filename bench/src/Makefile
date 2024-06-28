#thank you https://aoterodelaroza.github.io/devnotes/modern-fortran-makefiles/
.SUFFIXES: #disable automatic rules (avoid .mod being interpreted as modula-2 source files)
FC = gfortran
FFLAGS = -cpp -O3 # -Wall -Wextra


BIN_DIR := ../bin
BUILD_DIR := ../build
LIB_DIR   := ../lib
SRC_DIR   := .
VPATH = $(BUILD_DIR)

MODULE_f90 := $(wildcard $(SRC_DIR)/*.f90)
# see https://www.gnu.org/software/make/manual/html_node/Text-Functions.html
MODULE_O := $(patsubst $(SRC_DIR)/%.f90,$(BUILD_DIR)/%.o, $(MODULE_f90))


all: $(MODULE_O)
library: $(LIB_DIR)/library.a

# default rule
$(BUILD_DIR)/%.o $(BUILD_DIR)/%.mod : $(SRC_DIR)/%.f90 | $(BUILD_DIR)
	@echo .f90 files newer than .o files :
	@echo $?
	$(FC) $(FFLAGS) -c $< -o $(BUILD_DIR)/$(basename $<).o -J$(BUILD_DIR)
	@touch $@

# according to https://www1.udel.edu/topics_css/software/special/language/fortran/fortran-docs/fortran-libraries1.html
# need this to override default modula2 compiling

####################### compilation flags ########################
BENCH_LIB := -L$(LIB_DIR) -l:library.a
# TODO : try .so library - you must also modify the Makefile in src
# BENCH_LIB := -L$(LIB_DIR) -l:library.so
# TODO : try not using .a or .so
# BENCH_LIB := -L$(LIB_DIR)

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to bench
PERF_REGIONS_FOLDER:=../../perf_regions

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(BUILD_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}

# Additional rules :
$(BUILD_DIR)/benchmark_2D_CPU.o : $(BUILD_DIR)/tools.mod
$(BUILD_DIR)/benchmark_2D_GPU.o : $(BUILD_DIR)/tools.mod

$(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : $(SRC_DIR)/benchmark_implementations.f90 | $(BUILD_DIR)
# ./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_implementations.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)
	@touch $@

$(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : $(SRC_DIR)/benchmark_2D_CPU.f90 | $(BUILD_DIR)
# ./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2D_CPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)
	@touch $@

$(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : $(SRC_DIR)/benchmark_2D_GPU.f90 | $(BUILD_DIR)
# ./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2D_GPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)
	@touch $@




# $(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : benchmark_implementations.f90
# 	make -C .. build/benchmark_implementations.o
# $(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : benchmark_2D_CPU.f90
# 	make -C .. build/benchmark_2D_CPU.o
# $(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : benchmark_2D_GPU.f90
# 	make -C .. build/benchmark_2D_GPU.o

$(LIB_DIR)/library.a : $(MODULE_O) | $(LIB_DIR)
	ar crv $(LIB_DIR)/library.a $^
# @touch $(LIB_DIR)/library.a



# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) :
	-@mkdir $@