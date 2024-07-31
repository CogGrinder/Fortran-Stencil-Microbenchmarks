cd ~/Fortran-Stencil-Microbenchmarks/bench/postprocess
folder_name=all_benchmarks_07_31
mkdir -p $folder_name
make -C .. clean --silent
cd ../preprocess
# TODO: --module True set because non-module not yet implemented and graphing can break
python3 codegen.py --size-range 2048 1024 512 128 -c -nv #--module True #--size-range 128 4096 1024 # --hardware CPU --allocation STATIC
./run_bench_tree.sh #-vcompile #-vout #-vompgpu
cd ../postprocess
./collect_data_csv.sh -nv
python3 generate_graph.py -D $folder_name/gpu_cpu_$(printf $size)Mb -sp -G hardware -sG all