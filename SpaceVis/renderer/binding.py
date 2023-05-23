import ctypes
#import pathlib
import numpy as np
#import pandas as pd
import time
#from math import ceil
import os
import matplotlib.pyplot as plt
#from multiprocessing import Pool

package_directory = os.path.dirname(os.path.abspath(__file__))

cpp_renderer_lib = package_directory + "/renderer.dll"
cpp_renderer = ctypes.CDLL(cpp_renderer_lib)

#gpu_renderer_lib = package_directory + "/renderer_gpu.dll"
#gpu_renderer = ctypes.CDLL(gpu_renderer_lib)

def draw_frame(cam_pos,cam_rot,e,im_x,im_y,coords,interp_radius,box_size,box_mul,x_reps=2,y_reps=2,z_reps=2,depth_bins = np.array([[0,10000]])):
    n_coords = ctypes.c_int(len(coords))
    x_reps = ctypes.c_int(int(x_reps))
    y_reps = ctypes.c_int(int(y_reps))
    z_reps = ctypes.c_int(int(z_reps))

    box_mul = ctypes.c_float(float(box_mul))

    interp_radius = ctypes.c_int(int(interp_radius))
    box_size = ctypes.c_float(float(box_size))

    cam_pos = cam_pos.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    cam_rot = cam_rot.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    e = e.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    out = np.zeros((len(depth_bins),im_x,im_y),dtype=np.float32).flatten()

    cim_x = ctypes.c_int(im_x)
    cim_y = ctypes.c_int(im_y)

    coords_ptr = coords.astype(np.float32).flatten().ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    out_ptr = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    depth_bins_ptr = depth_bins.astype(np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    cpp_renderer.draw_frame(out_ptr,cam_pos,cam_rot,e,cim_x,cim_y,interp_radius,coords_ptr,n_coords,box_size,box_mul,x_reps,y_reps,z_reps,depth_bins_ptr,ctypes.c_int(len(depth_bins)))
    return out.reshape((len(depth_bins),im_x,im_y))

def blur(layer,size,amount):
    im_x = ctypes.c_int(layer.shape[0])
    im_y = ctypes.c_int(layer.shape[1])
    out = np.zeros_like(layer)
    out_ptr = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    in_ptr = layer.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    size = ctypes.c_int(int(size))
    blur_amount = ctypes.c_float(float(amount))
    cpp_renderer.blur(out_ptr,in_ptr,blur_amount,size,im_x,im_y)
    return out

'''
def scale_data(data,scale,ng):
    return (data-(ng//2))*scale + (ng//2)

def get_blurs(focus_center,depth_bins,mul=30,sqr=2):
    blurs = np.abs(depth_bins[:,0] - focus_center)
    blurs /= np.max(depth_bins[:,0])
    blurs **= sqr
    blurs *= mul
    return blurs

def do_blurs(out,focus_center,depth_bins,mul=30,sqr=2,size=15):
    blurs = get_blurs(focus_center,depth_bins,mul,sqr)
    final = np.zeros_like(out[0])
    for i,blur in zip(out,blurs):
        if blur == 0:
            final += i
        else:
            if not (np.sum(i) == 0):
                final += blur(i,size,blur)
    return final

def draw_thread(inputs):
    folder,redshift,data,idx,cam_pos_x,cam_pos_y,cam_pos_z,cam_rot_x,cam_rot_y,cam_rot_z,e_x,e_y,e_z,im_x,im_y,scale,blur_focus,sqr,depth_bins,ng,v_max = inputs
    print("Rendering frame: " + str(idx))
    start = time.perf_counter()
    pixel_box = 50 #100
    #vmax_mul = 0.9418932243289341
    #maxs = []
    cam_pos = np.array([cam_pos_x,cam_pos_y,cam_pos_z],dtype=np.float32)
    cam_rot = np.array([cam_rot_x,cam_rot_y,cam_rot_z],dtype=np.float32)
    e = np.array([e_x,e_y,e_z],dtype=np.float32)
    out = draw_frame(cam_pos,cam_rot,e,im_x,im_y,scale_data(data,scale,ng),pixel_box,ng,ng*scale,4,4,4,depth_bins=depth_bins)
    final = do_blurs(out,blur_focus,depth_bins,sqr=sqr,mul=30)
    if v_max == 0:
        plt.imshow(final,cmap="inferno")#,vmax=v_max,vmin=0)#,vmax=0.03,vmin=0)
    else:
        plt.imshow(final,cmap="inferno",vmax=v_max,vmin=0)#,vmax=0.03,vmin=0)
    redshift = (redshift/199)*200
    redshift = str(int(200-redshift))
    plt.text(20,45,"z=" + redshift,c=(1,1,1),backgroundcolor=None)
    plt.axis('off')
    plt.savefig(folder + "/step" + str(idx) + ".jpg",bbox_inches='tight',pad_inches = 0,dpi=600)
    plt.close()
    end = time.perf_counter()
    print("Finished frame: " + str(idx) + " in",end-start)
    return


def draw_parallel(n_threads,n_frames,data,im_x,im_y,ng=32,depth_bin_end=128,depth_bin_step=5,folder="temp",**keyframes):
    cam_pos_x = keyframes["cam_pos_x"]
    cam_pos_y = keyframes["cam_pos_y"]
    cam_pos_z = keyframes["cam_pos_z"]
    cam_rot_x = keyframes["cam_rot_x"]
    cam_rot_y = keyframes["cam_rot_y"]
    cam_rot_z = keyframes["cam_rot_z"]
    e_x = keyframes["e_x"]
    e_y = keyframes["e_y"]
    e_z = keyframes["e_z"]
    scale = keyframes["scale"]
    blur_amount = keyframes["blur_focus"]
    sqr = keyframes["sqr"]
    data_frames = keyframes["data_frames"]
    v_max = keyframes["v_max"]
    starts = np.arange(0,depth_bin_end,depth_bin_step)
    ends = np.array(starts[1:].tolist() + [10000])
    depth_bins = np.column_stack((starts,ends)).astype(np.float32)
    map_inputs = []
    for i in range(n_frames):
        out = (folder,data_frames[i],data[data_frames[i]],i,
                cam_pos_x[i],cam_pos_y[i],cam_pos_z[i],
                cam_rot_x[i],cam_rot_y[i],cam_rot_z[i],
                e_x[i],e_y[i],e_z[i],
                im_x,im_y,
                scale[i],blur_amount[i],sqr[i],depth_bins,ng,v_max[i])
        map_inputs.append(out)
    return map_inputs


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
'''