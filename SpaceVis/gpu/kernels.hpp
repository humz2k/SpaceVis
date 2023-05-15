
#define FPC_TARGET_METAL
#include "fpc_port.hpp"
#include <stdlib.h>
#include <stdio.h>

void FPC_init(){
FPC::lib.load_library("/Users/humzaqureshi/GitHub/SpaceVis/SpaceVis/gpu/kernels.metallib");
FPC::lib.load_kernel("render");
}
void GPU_render(const int (&num_blocks)[1], const int (&block_size)[1], 
                    FPC::Buffer particles, FPC::Buffer out,
                    float cam_x, float cam_y, float cam_z,
                    float rot_x, float rot_y, float rot_z,
                    float e_x, float e_y, float e_z,
                    int im_x, int im_y,
                    int interp_radius,
                    float box_size)
{
MTL::Size m_grid_size = MTL::Size(block_size[0] * num_blocks[0], 1, 1);
MTL::Size m_thread_group_size = MTL::Size(block_size[0], 1, 1);
FPC::lib.dispatch_function("render",m_grid_size,m_thread_group_size,particles,out,
                cam_x,cam_y,cam_z,
                rot_x,rot_y,rot_z,
                e_x,e_y,e_z,
                im_x,im_y,
                interp_radius,box_size);
}

void FPC_clean(){
    FPC::lib.cleanup();
}