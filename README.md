# SpaceVis
 
* You need to build renderer.cpp before running `main.py`. 
  * There is a makefile in SpaceVis/renderer that works for me, but you might need to change it.
  * You don't need to build with openmp, but it makes it significantly faster
* You need to install opencv-python and perlin-noise (`pip install opencv-python`, and `pip install perlin-noise`) or use the requirements.txt file.
* When running `main.py`, you might need to change `n_threads`. 
  * It is set to 5 currently. 
  * Because renderer.cpp uses openmp, I wouldn't set `n_threads` to all threads, i.e. make sure each thread has at least one other free.
* Running `main.py` will make a folder called `temp`, and then fills that with each frame (as a `.png`), then uses opencv to stitch those into a `.mp4`.
* Each thread uses something like 215mb of memory (minimum), so be careful about running on a lot of threads.
* It takes a **long** time to run the whole thing, if you just want to render a subset of frames, in `draw_parallel`, change:
```
if __name__ == '__main__':
    start = time.perf_counter()
    with Pool(n_threads) as p:
        p.map(__draw, map_inputs)
    end = time.perf_counter()
    print("Executed in: " + str(end - start))
```
to
```
if __name__ == '__main__':
    start = time.perf_counter()
    with Pool(n_threads) as p:
        p.map(__draw, map_inputs[start_frame:end_frame])
    end = time.perf_counter()
    print("Executed in: " + str(end - start))
```