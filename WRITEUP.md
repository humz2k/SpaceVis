# CMSC 23700 Final Project

## Overview
* Integrating density down line of sight
* Color mapping density
* (almost) Gaussian blur
* (fake) Depth of field
* Perlin noise camera shake
* Custom (parallel) renderer
* Spline + linear interpolation for keyframes

## Integrating Density
* We are rendering a cosmology simulation, which models a continuous density distribution using discrete particles.
* To visualize it, you integrate the density distribution down a line of sight.
* In practice, this means projecting all the particles from 3D to 2D, and then for each pixel summing over all the particles that fall into it.
* I use perspective projection, and then sum over the 'brightness' $\left(\frac{1}{r^2}\right)$ for each particle in each pixel.
* 'Brightness' is in quotes, as the simulation models mass, so there is no physical meaning for 'brightness'.
* To make this look nicer, I treat each particle as if it is a ball with some radius, rather than infintesimally small.
* So, instead of each particle corresponding to one pixel, it will fall into a few pixels.
* The 'brightness' of each particle also does not have a hard cut-off at its radius, but instead falls off smoothly.
* The bounding box for each particle (that draws the ball/fall off) is scaled up/down based on its distance from the camera, to speed up the render.
* Code is in `draw_point` in `SpaceVis/renderer/renderer.cpp`.

## Color Map
* Because units are arbitrary, you have to be careful about how to map colors to the integrated density.
* Instead of choosing a single mapping from density to color, I vary it depending on the frame to make it look nicer.
* I also kind of cheat by just using a default color map in matplotlib, but making a custom color map wouldn't be too difficult.

## Gaussian Blur
* Uses a kernel to blur an image.
* The kernel is not actually a gaussian distribution, but is instead a simpler function that approximates a gaussian distribution.
* This was mainly because I am lazy.
* Code is in `blur` in `SpaceVis/renderer/renderer.cpp`.

## Depth of Field
* I approximate depth of field by:
  * Rendering layers based on the particles distance from the camera.
  * Blurring each layer based on what the camera is focusing on.
  * Combining the layers at the end.
* I initially had layers to try and parallelize the code better, but it ended up not really working, so instead I used them for depth of field.
* Code is in `do_blurs` in `main.py`.

## Camera Shake
* Simple camera shake using a Perlin Noise library I found.
* Code is in `get_camera_shake` in `SpaceVis/camera_shaker.py`.

## Projections etc.
* Code that does the projection is in `SpaceVis/renderer.cpp`.
* Code that does rotations is in `SpaceVis/Matrix.hpp` and `SpaceVis/camera_utils.hpp`.

## Parallel rendering
* Firstly, the gaussian blur function is parallelized using an openmp `parallel for`.
* Then, multiple frames are rendered in parallel using python's `multiprocessing`.
* I also experimented with writing GPU shaders, which mostly worked apart from the fact that my mac doesn't support atomic floating point types, so I would have had to do some hacky thing like storing each float in a long or something (I used my project [here](https://github.com/humz2k/FPC), which tries to make it less annoying to write general purpose Metal shaders).
* Definitely would have been better to write everything using openmp or MPI or something in C++, but I am lazy.

## Keyframes
* Keyframes using bsplines and linear interpolation, in `SpaceVis/interpolation.py`.

## Python Interface
* Uses `ctypes` to call C++ functions.

## The Animation
* Initially, the entire simulation volume is scaled down to look like a single point.
* Start out of focus, then focus on simulation volume.
* Camera zooms into the simulation volume, while the simulation progresses forward in time (by changing display surface distance).
* Camera zooms out of the simulation volume, and simulation rewinds backwards.
* Then keep camera stationary and scale up simulation very quickly (like a Big Bang).
* Camera moves/looks around in the simulation, focusing on different things (you can't really tell because everything is either small or far away anyway).

## Stuff I couldn't do
* I wanted to render a galaxy, and have that also be a part of my animation, but the simulation data I found was pretty boring to look at (just a blob of stars) so I changed my mind.
* Make GPU stuff work.
* Use a larger simulation. 
  * The simulation that is visualized here is a really small one I ran on my laptop.
  * However, the CPU renderer is too slow to visualize larger simulations in reasonable time.