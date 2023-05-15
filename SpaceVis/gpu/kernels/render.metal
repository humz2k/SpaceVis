#include <metal_stdlib>

using namespace metal;

kernel void add2D(device float* in, uint mtl_thread [[thread_position_in_grid]])
{

    in[mtl_thread] = 10;

}