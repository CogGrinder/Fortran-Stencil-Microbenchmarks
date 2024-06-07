### tutorial makefile ###

all: tuto
run: run_tuto
clean: clean_tuto

ECHO:= echo
OMP := omp
# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
ECHO:= $(ECHO).exe
OMP := $(OMP).exe
endif

TUTO_EXEC := $(ECHO) $(OMP)

tuto: $(TUTO_EXEC)

$(ECHO) : hello_world_echo.f90
	gfortran hello_world_echo.f90 -o $(ECHO)

# cannot group compilations because hello_world_omp.f90 uses openmp
# old path change :
# export PATH:=/usr/local/cuda:/usr/local/cuda/bin:$(PATH)
# new path change :
# export PATH:=/usr/lib/nvidia-cuda-toolkit:/usr/lib/nvidia-cuda-toolkit/bin:$(PATH)
# note : to change CUDA version simlink, use
# sudo update-alternatives --display cuda
# sudo update-alternatives --config cuda
# export PATH:=/usr/local/cuda-11:/usr/local/cuda-11/bin:$(PATH)
export PATH:=/usr/local/cuda-12:/usr/local/cuda-12/bin:$(PATH)
# export LD_LIBRARY_PATH:=/usr/local/cuda-11:/usr/local/cuda-11/lib:$(LD_LIBRARY_PATH)
export LD_LIBRARY_PATH:=/usr/local/cuda-12:/usr/local/cuda-12/lib:$(LD_LIBRARY_PATH)
$(OMP) : hello_world_omp.f90
	@echo $(PATH)
	gfortran -cpp -fopenmp -foffload=nvptx-none -fno-stack-protector hello_world_omp.f90 -o $(OMP)
# --ptxas-options -gpu-name=sm_75
# note : can use -foffload=-lgfortran
# gfortran -cpp -fopenmp -foffload=nvptx-none -fno-stack-protector -lgcc -L/usr/local/cuda/lib64/ -lcuda -lcudart hello_world_omp.f90 -o $(OMP)

run_tuto: run_omp
run_echo : $(ECHO)
	-./$(ECHO) 0 1 2 gotchu
run_omp : $(OMP)
	OMP_TARGET_OFFLOAD=mandatory ./$(OMP)
# nvprof ./$(OMP)


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean_tuto:
	rm *.exe
else
clean_tuto:
# grep version
# note 1 : grep -v "\." removes from ls all files containing a dot
#          indeed, "." is a metacharacter ie regex for one character
# note 2 : xargs removes each file
#          if doing to subdirectory, use $$ xargs -I file rm $(SUBDIR)/file
	ls | grep -v "\." | grep -v Makefile | xargs rm
endif