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
$(OMP) : hello_world_omp.f90
	gfortran -fopenmp hello_world_omp.f90 -o $(OMP)

run_tuto: run_echo run_omp
run_echo : $(ECHO)
	-./$(ECHO) 0 1 2 gotchu
run_omp : $(OMP)
	-./$(OMP)


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