cd ~/Fortran-Stencil-Microbenchmarks/bench/postprocess
folder_name=all_benchmarks_07_31
mkdir -p $folder_name
make -C .. clean --silent
cd ../preprocess
# TODO: --module True set because non-module not yet implemented and graphing can break
python3 codegen.py -c -nv --module True --size 1 -A 1 --compile-size False --compile-loop-bound True --hardware CPU
./run_bench_tree.sh #-vcompile #-vout #-vompgpu
cd ../postprocess
./collect_data_csv.sh -nv
python3 generate_graph.py -sp -D test_compile_loop_bound_3 -G compile_size -sG hardware -B compile_loop_bound:False