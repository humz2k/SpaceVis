#include <stdlib.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include "camera_utils.hpp"
#include <math.h>
#include <time.h>

inline float project(float z, float xy, float e_z, float e_xy, float im_size, float box_size){
    return (((((e_z/z)*xy + e_xy))/box_size) + 0.5)*(im_size - 1.f);
}

inline void draw_point(float in_x, float in_y, float in_z, float* cam_pos, float* cam_rot, float* e, int im_x, int im_y, int interp_radius, float box_size, Matrix rmat, float* out){
    //Vector point = rmat * Vector(in_x,in_y,in_z);
    float x = rmat(0,0) * in_x + rmat(0,1) * in_y + rmat(0,2) * in_z;
    float y = rmat(1,0) * in_x + rmat(1,1) * in_y + rmat(1,2) * in_z;
    float z = rmat(2,0) * in_x + rmat(2,1) * in_y + rmat(2,2) * in_z;
    if (z >= 0){
        float f_im_x = (float)im_x;
        float f_im_y = (float)im_y;
        float f_interp_radius = (float)interp_radius;
        float bx = project(z,x,e[2],e[0],f_im_x,box_size);//((((e[2]/z)*x + e[0]) + 16)/32.f)*((float)im_x - 1.f);
        float by = project(z,y,e[2],e[1],f_im_y,box_size);//((((e[2]/z)*y + e[1]) + 16)/32.f)*((float)im_y - 1.f);

        if (((bx >= 0) && (bx < f_im_x)) && ((by >= 0) && (by < f_im_y))){
            
            float dist2 = ((x*x) + (y*y) + (z*z));
            float weight = 1/(dist2);
            int local_interp = (int)roundf(f_interp_radius * (1/z)*2);
            for (int dx = -local_interp; dx < (local_interp+1); dx++){
                for (int dy = -local_interp; dy < (local_interp+1); dy++){
                    
                    float pixel_weight = (1.f/((float)(dx*dx + dy*dy + 1)));
                    int coord_x = (int)roundf((float)dx + bx);
                    int coord_y = (int)roundf((float)dy + by);
                    if (((coord_x >= 0) && (coord_x < im_x)) && ((coord_y >= 0) && (coord_y < im_y))){
                        out[coord_x * im_y + coord_y] = out[coord_x * im_y + coord_y] + weight * pixel_weight;
                    }

                }   

            }
            

        }

    }

}

extern "C"{
    void draw_frame(float* out, float* cam_pos, float* cam_rot, float* e, int im_x, int im_y, int interp_radius, float* raw_points, int n_points, float box_size, int x_reps, int y_reps, int z_reps){//float* raw_points, int n_points, int interp_radius, float* out){
        //std::vector<float> points = ptr2vec(raw_points,n_points*3);
        //points = camTransform(Vector(cam_pos[0],cam_pos[1],cam_pos[2]),Vector(cam_rot[0],cam_rot[1],cam_rot[2]),points);

        long start = clock();

        float f_im_x = (float)im_x;
        float f_im_y = (float)im_y;
        float f_interp_radius = (float)interp_radius;

        int hxreps = x_reps/2;
        int hyreps = y_reps/2;
        int hzreps = z_reps/2;

        Matrix rmat = RotMat(cam_rot[0],cam_rot[1],cam_rot[2]);
        int last = -1;

        long init_done = clock();

        for (int i = 0; i < n_points; i++){
            
            float x = raw_points[i*3] - cam_pos[0];
            float y = raw_points[i*3+1] - cam_pos[1];
            float z = raw_points[i*3+2] - cam_pos[2];

            while (z > box_size){
                z = z - box_size;
            }
            while (z < 0){
                z = z + box_size;
            }

            while (y > box_size){
                y = y - box_size;
            }
            while (y < 0){
                y = y + box_size;
            }

            while (x > box_size){
                x = x - box_size;
            }
            while (y < 0){
                x = x + box_size;
            }

            for (int x_mul = -hxreps; x_mul < (hxreps+1); x_mul++){
                for (int y_mul = -hyreps; y_mul < (hyreps+1); y_mul++){
                    for (int z_mul = -hzreps; z_mul < (hzreps+1); z_mul++){
            //int x_mul = 0;
            //int y_mul = 0;
            //int z_mul = 0;
            draw_point(x + ((float)x_mul)*box_size, y + ((float)y_mul)*box_size, z + ((float)z_mul)*box_size, cam_pos,cam_rot,e,im_x,im_y,interp_radius,box_size,rmat,out);
                        
                    }
                }
            }
        }

        rmat.free_ptr();
        long all_done = clock();

        double init_time = ((double)(init_done-start))/((double)CLOCKS_PER_SEC);
        double loop_time = ((double)(all_done-init_done))/((double)CLOCKS_PER_SEC);

        printf("INIT_TIME %f\nLOOP_TIME %f\n",init_time,loop_time);
    }
}

extern "C"{
    void test(float* out){
        out[0] = 100;
    }
}
/*
int main(){

    int n_points = 1;

    //sttd::vector<float> points;
    //points.resize(n_points*3);

    float* raw_points = (float*)malloc(sizeof(float)*n_points*3);

    raw_points[0] = 1;
    raw_points[1] = 0;
    raw_points[2] = 0;

    std::vector<float> points = ptr2vec(raw_points,n_points*3);

    points = camTransform(Vector(0,0,0),Vector(0,0,0),points);

    for (int i = 0; i < n_points; i++){
        printf("(%5.2f %5.2f %5.2f)\n",points[i*3],points[i*3+1],points[i*3+2]);
    }

    return 0;
}*/