#include <metal_stdlib>

using namespace metal;

kernel void render(device float* particles, 
                    device atomic_int* out, 
                    float& cam_x, float& cam_y, float& cam_z,
                    float& rot_x, float& rot_y, float& rot_z,
                    float& e_x, float& e_y, float& e_z,
                    int& im_x, int& im_y,
                    int& interp_radius,
                    float& box_size,
                    uint threadID [[thread_position_in_grid]])
{

    //in[threadID] = 10;

}