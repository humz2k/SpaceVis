#include <stdlib.h>
#include <stdio.h>

#include "kernels.hpp"

extern "C"{
    void init_gpu(){
        FPC_init();
    }
}

extern "C"{
    void free_gpu(){
        FPC_clean();
    }
}

extern "C"{
    void draw_frame(float* h_out, 
                        float cam_x, float cam_y, float cam_z,
                        float rot_x, float rot_y, float rot_z,
                        float e_x, float e_y, float e_z,
                        int im_x, int im_y,
                        float box_size, int pixels_per_particle,
                        float* h_particles, int n_particles)
    {
        FPC::Buffer d_particles;
        d_particles.allocate<float>(n_particles*3);
        d_particles.set(h_particles);

        FPC::Buffer d_out;
        d_out.allocate<float>(im_x*im_y);
    }
}