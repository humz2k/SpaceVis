
#define FPC_TARGET_METAL
#include "fpc_port.hpp"
#include <stdlib.h>
#include <stdio.h>

void FPC_init(){
FPC::lib.load_library("/Users/humzaqureshi/GitHub/SpaceVis/SpaceVis/gpu/kernels.metallib");
FPC::lib.load_kernel("render");
}
void GPU_render(const int (&num_blocks)[1], const int (&block_size)[1], FPC::Buffer particles)
{
MTL::Size m_grid_size = MTL::Size(block_size[0] * num_blocks[0], 1, 1);
MTL::Size m_thread_group_size = MTL::Size(block_size[0], 1, 1);
FPC::lib.dispatch_function("render",m_grid_size,m_thread_group_size,particles);
}

void FPC_clean(){
    FPC::lib.cleanup();
}