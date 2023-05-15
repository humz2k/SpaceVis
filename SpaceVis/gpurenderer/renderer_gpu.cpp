#include <stdlib.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include "camera_utils.hpp"
#include <math.h>
#include "/Users/humzaqureshi/GitHub/FPC/include/fpc_headers.hpp"

//#define TIMER

device kernel calc_points[i](float* points, float* rmat, float* cam_pos, float* e, float im_x, float im_y, int interp_radius, int each, float* out){
    float in_x = points[thread.i*3] - cam_pos[0];
    float in_y = points[thread.i*3+1] - cam_pos[1];
    float in_z = points[thread.i*3+2] - cam_pos[2];

    if (in_z < 0f){
        in_z += 32f;
    }

    float x = rmat[0*3 + 0] * in_x + rmat[0*3 + 1] * in_y + rmat[0*3 + 2] * in_z;
    float y = rmat[1*3 + 0] * in_x + rmat[1*3 + 1] * in_y + rmat[1*3 + 2] * in_z;
    float z = rmat[2*3 + 0] * in_x + rmat[2*3 + 1] * in_y + rmat[2*3 + 2] * in_z;

    for (int i = 0; i < each; i++){
        out[((thread.i*each)+i)*3] = 0f-1f;
        out[((thread.i*each)+i)*3+1] = 0f-1f;
        out[((thread.i*each)+i)*3+2] = 0f-1f;
    }

    if (z < 0f){
        return;
    }

    float bx = ((((e[2]/z)*x + e[0])/32f) + 0.5f) * (im_x - 1.f);
    float by = ((((e[2]/z)*y + e[1])/32f) + 0.5f) * (im_y - 1.f);
    float dist2 = (x*x) + (y*y) + (z*z);
    float weight = 1f/dist2;

    //int local_interp = (int)(((float)interp_radius) * (1.f/(z+1.f)));
    //if (local_interp > (interp_radius*2)){
    //    local_interp = interp_radius*2;
    //}
    int counter = 0;
    for (int dx = (0-interp_radius); dx < (interp_radius+1); dx++){
        for (int dy = (0-interp_radius); dy < (interp_radius+1); dy++){
            float pixel_weight = (1.f/((float)(dx*dx + dy*dy + 1)));
            out[((thread.i*each)+counter)*3] = bx + ((float)dx);
            out[((thread.i*each)+counter)*3+1] = by + ((float)dy);
            out[((thread.i*each)+counter)*3+2] = weight * pixel_weight;
            counter++;
        }
    }

}

/*device kernel draw_points[i](const float* calculated, int n_points, float* out, int im_x, int im_y){
    for (int i = 0; i < n_points; i++){
        float fx = calculated[i*3];
        float fy = calculated[i*3+1];
        float weight = calculated[i*3+2];
        int x = (int)fx;
        int y = (int)fy;
        if (((x >= 0) && (x < im_x)) && ((y >= 0) && (y < im_y))){
            out[x * im_y + y] = out[x * im_y + y] + weight;
        }
    }
}*/

FPC::Buffer points_buffer;

extern "C"{
    void load_points(float* raw_points, int n_points){
        points_buffer.allocate<float>(n_points*3);
        points_buffer.set(raw_points);
    }
}

extern "C"{
    void draw_frame(float* out, float* cam_pos, float* cam_rot, float* e, int im_x, int im_y, int interp_radius, int n_points, float box_size, int x_reps, int y_reps, int z_reps){//float* raw_points, int n_points, int interp_radius, float* out){
        long first,second;
        double time;

        long BIG_FIRST = clock();

        first = clock();
        
        float f_im_x = (float)im_x;
        float f_im_y = (float)im_y;

        int each = (interp_radius * 2)*(interp_radius * 2) + 1;

        //printf("EACH %d\n",each);

        Matrix rmat = RotMat(cam_rot[0],cam_rot[1],cam_rot[2]);

        //std::vector<float> h_out;
        //h_out.resize(n_points*3);

        float* h_out = (float*)malloc(sizeof(float)*n_points*each*3);

        FPC::Buffer rmat_buffer;
        rmat_buffer.allocate<float>(3*3);
        rmat_buffer.set(rmat.get_raw());

        FPC::Buffer cam_pos_buffer;
        cam_pos_buffer.allocate<float>(3);
        cam_pos_buffer.set(cam_pos);

        FPC::Buffer e_buffer;
        e_buffer.allocate<float>(3);
        e_buffer.set(e);

        FPC::Buffer out_buffer;
        out_buffer.allocate<float>(n_points*each*3);

        FPC::Buffer pixel_buffer;
        pixel_buffer.allocate<float>(im_x*im_y);

        first = clock();

        calc_points({n_points/512},{512},points_buffer,rmat_buffer,cam_pos_buffer,e_buffer,f_im_x,f_im_y,interp_radius,each,out_buffer);

        second = clock();

        time = ((double)(second-first))/((double)CLOCKS_PER_SEC);

        #ifdef TIMER
        printf("GPU_TIME %f\n",time);
        #endif
        
        first = clock();

        out_buffer.get(h_out);

        double first1 = clock();

        for (int i = 0; i < n_points*each; i++){
            int x = (int)h_out[i*3];
            int y = (int)h_out[i*3+1];
            float weight = h_out[i*3+2];
            if (((x >= 0) && (x < im_x)) && ((y >= 0) && (y < im_y))){
                out[x * im_y + y] = out[x * im_y + y] + weight;
            }
        }

        double second1 = clock();

        
        #ifdef TIMER
        time = ((double)(first1-first))/((double)CLOCKS_PER_SEC);
        printf("READ_TIME %f\n",time);
        time = ((double)(second1-first1))/((double)CLOCKS_PER_SEC);
        printf("CPU_TIME %f\n",time);
        #endif

        free(h_out);

        rmat.free_ptr();

        long BIG_SECOND = clock();

        time = ((double)(BIG_SECOND-BIG_FIRST))/((double)CLOCKS_PER_SEC);
        //printf("ALL_TIME %f\n",time);

    }
}

extern "C"{
    void init_gpu(){
        FPC_init();
    }
}
