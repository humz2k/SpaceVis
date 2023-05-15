import ctypes
import pathlib
import numpy as np
import pandas as pd
import time
from math import ceil
import os

package_directory = os.path.dirname(os.path.abspath(__file__))

gpu_renderer_lib = package_directory + "/renderer_gpu.dll"
gpu_renderer = ctypes.CDLL(gpu_renderer_lib)

def GPU_init():
    gpu_renderer.init_gpu()

def GPU_close():
    gpu_renderer.fin_gpu()

def GPU_loadpoints(coords):
    n_coords = ctypes.c_int(len(coords))
    coords_ptr = coords.astype(np.float32).flatten().ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    gpu_renderer.load_points(coords_ptr,n_coords)

def draw_frame_GPU(cam_pos,cam_rot,e,im_x,im_y,coords,interp_radius,box_size,x_reps=2,y_reps=2,z_reps=2):
    n_coords = ctypes.c_int(len(coords))
    x_reps = ctypes.c_int(int(x_reps))
    y_reps = ctypes.c_int(int(y_reps))
    z_reps = ctypes.c_int(int(z_reps))

    interp_radius = ctypes.c_int(int(interp_radius))
    box_size = ctypes.c_float(float(box_size))

    cam_pos = cam_pos.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    cam_rot = cam_rot.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    e = e.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    out = np.zeros((im_x,im_y),dtype=np.float32).flatten()

    cim_x = ctypes.c_int(im_x)
    cim_y = ctypes.c_int(im_y)

    out_ptr = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    gpu_renderer.draw_frame(out_ptr,cam_pos,cam_rot,e,cim_x,cim_y,interp_radius,n_coords,box_size,x_reps,y_reps,z_reps)
    return out.reshape((im_x,im_y))