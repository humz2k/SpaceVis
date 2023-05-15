#include <vector>
#include <stdio.h>
#include <iostream>
#include <stdexcept>


class Vector{
    private:
        float* raw;
        int init;
    
    public:
        int x;

        Vector(){
            init = 0;
        }

        Vector(int X){
            init = 1;
            x = X;
            raw = (float*)malloc(sizeof(float)*X);
        }

        Vector(float X, float Y, float Z){
            init = 1;
            raw = (float*)malloc(sizeof(float)*3);
            raw[0] = X;
            raw[1] = Y;
            raw[2] = Z;
            x = 3;
        }

        float& operator ()(int X){
            return raw[X];
        }

        void print(){
            printf("(");
            for (int i = 0; i < x-1;i++){
                printf("%5.2f ",raw[i]);
            }
            printf("%5.2f)\n",raw[x-1]);
        }

        float* get_raw(){
            return raw;
        }

        ~Vector(){
            if (init){
                init = 0;
                free(raw);
            }
        }
};

class Matrix{
    private:
        float* raw;
    
    public:
        int x;
        int y;
        Matrix(){
        }

        ~Matrix(){
        }

        Matrix(int X, int Y){
            x = X;
            y = Y;
            raw = (float*)malloc(sizeof(float)*X*Y);
        }

        float& operator ()(int X, int Y){
            return raw[X*y + Y];
        }

        void print(){
            printf("(");
            for (int i = 0; i < x; i++){
                if (i > 0){
                    printf(" ");
                }
                printf("(");
                for (int j = 0; j < y; j++){
                    printf("%5.2f",raw[i*y + j]);
                    if (j != (y-1)){
                        printf(" ");
                    }
                }
                if (i == (x-1)){
                    printf(")");
                }
                printf(")\n");
            }
        }

        Matrix mul(Matrix other){
            if (y != other.x){
                throw std::invalid_argument("Invalid Matrix Dims");
            }
            Matrix out(x,other.y);
            for (int i = 0; i < x; i++){
                for (int j = 0; j < other.y; j++){
                    float sum = 0;
                    for (int k = 0; k < y; k++){
                        sum += raw[i*y + k] * other(k,j);
                    }
                    out(i,j) = sum;
                }
            }
            return out;
        }

        Vector mul(Vector other){
            if (y != other.x){
                throw std::invalid_argument("Invalid Matrix Dims");
            }
            Vector out(x);
            for (int i = 0; i < x; i++){
                float sum = 0;
                for (int k = 0; k < y; k++){
                    sum += raw[i*y + k] * other(k);
                }
                out(i) = sum;
            }
            return out;
        }

        void mul(std::vector<float> &points){
            if ((points.size() % y) != 0){
                throw std::invalid_argument("Invalid Matrix Dims");
            }
            std::vector<float> temp;
            temp.resize(y);
            int n = points.size() / y;
            for (int point = 0; point < n; point++){
                for (int i = 0; i < x; i++){
                    float sum = 0;
                    for (int k = 0; k < y; k++){
                        sum += raw[i*y + k] * points[point*y + k];
                    }
                    temp[i] = sum;
                }
                for (int i = 0; i < y; i++){
                    points[point*y + i] = temp[i];
                }
            }
        }

        float* get_raw(){
            return raw;
        }

        void free_ptr(){
            free(raw);
        }
};

Matrix operator *(Matrix left, Matrix right){
    return left.mul(right);
}

Vector operator *(Matrix left, Vector right){
    return left.mul(right);
}

Vector operator -(Vector left, Vector right){
    return Vector(left(0)-right(0),left(1)-right(1),left(2)-right(2));
}

std::vector<float>& operator *(Matrix left, std::vector<float>& right){
    left.mul(right);
    return right;
}

std::vector<float>& operator -(std::vector<float>& left, Vector right){
    if ((left.size() % right.x) != 0){
        throw std::invalid_argument("Invalid Vector Dims");
    }
    int n = left.size() / right.x;
    for (int i = 0; i < n; i++){
        for (int j = 0; j < right.x; j++){
            left[i*right.x + j] -= right(j);
        }
    }
    return left;
}

