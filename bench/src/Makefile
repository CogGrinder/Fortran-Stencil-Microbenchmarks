#to debug preprocessor, use cpp -E benchmark_2D_CPU.f90 -DSIZE_AT_COMPILATION=1 -DNI=1024 -DNJ=1024 -I../../perf_regions/src
#thank you https://aoterodelaroza.github.io/devnotes/modern-fortran-makefiles/
.SUFFIXES: #disable automatic rules to override default modula2 compiling
# (avoid .mod being interpreted as modula-2 source files)
FC = gfortran
FFLAGS = -cpp -O3 #-Wall -Wextra


BIN_DIR := ../bin
BUILD_DIR := ../build
LIB_DIR   := ../lib
SRC_DIR   := .
VPATH = $(BUILD_DIR)

MODULE_f90 := $(wildcard $(SRC_DIR)/*.f90)
# see https://www.gnu.org/software/make/manual/html_node/Text-Functions.html
MODULE_O := $(patsubst $(SRC_DIR)/%.f90,$(BUILD_DIR)/%.o, $(MODULE_f90))

####################### defaults #######################

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

####################### targets #######################

all: $(MODULE_O)
library: $(LIB_DIR)/library.a

# default rule
$(BUILD_DIR)/%.o $(BUILD_DIR)/%.mod : $(SRC_DIR)/%.f90 | $(BUILD_DIR)
	$(FC) $(FFLAGS) -c $< -o $(BUILD_DIR)/$(basename $<).o -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNI=${NI} -DNJ=${NJ} -J$(BUILD_DIR)

####################### compilation flags ########################
BENCH_LIB := -L$(LIB_DIR) -l:library.a
PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to bench
ifdef _PERF_REGIONS_FOLDER
PERF_REGIONS_FOLDER=../$(_PERF_REGIONS_FOLDER)
else
PERF_REGIONS_FOLDER:=../../perf_regions
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(BUILD_DIR) -I$(SRC_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}

####################### extra dependency rules #######################

$(BUILD_DIR)/benchmark_parameters.o : $(BUILD_DIR)/benchmark_names.mod
$(BUILD_DIR)/benchmark_implementations.o : $(BUILD_DIR)/tools.mod $(BUILD_DIR)/benchmark_names.mod
$(BUILD_DIR)/benchmark_2D_CPU.o : $(BUILD_DIR)/tools.mod $(BUILD_DIR)/benchmark_parameters.mod
$(BUILD_DIR)/benchmark_2D_GPU.o : $(BUILD_DIR)/tools.mod $(BUILD_DIR)/benchmark_parameters.mod

####################### compilation with special flags #######################

$(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : $(SRC_DIR)/benchmark_implementations.f90 | $(BUILD_DIR)
	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_implementations.o -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNI=${NI} -DNJ=${NJ} ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)

$(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : $(SRC_DIR)/benchmark_2D_CPU.f90 | $(BUILD_DIR)
	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2D_CPU.o -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNI=${NI} -DNJ=${NJ} ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)

$(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : $(SRC_DIR)/benchmark_2D_GPU.f90 | $(BUILD_DIR)
	${FC} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2D_GPU.o -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNI=${NI} -DNJ=${NJ} ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)

# please note: timestamp resolution in archives is lower according to
# documentation of make's .LOW_RESOLUTION_TIME at
# https://www.gnu.org/software/make/manual/html_node/Special-Targets.html
$(LIB_DIR)/library.a : $(MODULE_O) | $(LIB_DIR)
	ar crUu $(LIB_DIR)/library.a $^
# touch $^
# touch $(LIB_DIR)/library.a



# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) :
	-@mkdir $@