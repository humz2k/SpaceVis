#include <metal_stdlib>

using namespace metal;

kernel void add2D(device float* in, uint threadID [[thread_position_in_grid]])
{

    in[threadID] = 10;

}