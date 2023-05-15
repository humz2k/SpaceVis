#include "matrix.hpp"
#include "math.h"

Matrix RotX(float rx){

    float sx = sinf(rx);
    float cx = cosf(rx);

    Matrix out(3,3);

    out(0,0) = 1;
    out(0,1) = 0;
    out(0,2) = 0;
    out(1,0) = 0;
    out(1,1) = cx;
    out(1,2) = sx;
    out(2,0) = 0;
    out(2,1) = -sx;
    out(2,2) = cx;

    return out;
}


Matrix RotY(float ry){

    float sy = sinf(ry);
    float cy = cosf(ry);

    Matrix out(3,3);

    out(0,0) = cy;
    out(0,1) = 0;
    out(0,2) = -sy;
    out(1,0) = 0;
    out(1,1) = 1;
    out(1,2) = 0;
    out(2,0) = sy;
    out(2,1) = 0;
    out(2,2) = cy;

    return out;

}

Matrix RotZ(float rz){

    float sz = sinf(rz);
    float cz = cosf(rz);

    Matrix out(3,3);

    out(0,0) = cz;
    out(0,1) = sz;
    out(0,2) = 0;
    out(1,0) = -sz;
    out(1,1) = cz;
    out(1,2) = 0;
    out(2,0) = 0;
    out(2,1) = 0;
    out(2,2) = 1;

    return out;

}

Matrix RotMat(float rx, float ry, float rz){
    return RotX(rx)*RotY(ry)*RotZ(rz);
}

std::vector<float>& camTransform(Vector cam_pos, Vector cam_rot, std::vector<float> points){
    return RotMat(cam_rot(0),cam_rot(1),cam_rot(2)) * (points - cam_pos);
}

Vector camTransform(Vector cam_pos, Vector cam_rot, Vector point){
    return RotMat(cam_rot(0),cam_rot(1),cam_rot(2)) * point;
}

template<typename T>
std::vector<T> ptr2vec(T* raw, int n){
    std::vector<T> out;
    out.resize(n);
    for (int i = 0; i < n; i++){
        out[i] = raw[i];
    }
    return out;
}