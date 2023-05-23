import SpaceVis
import pygio
import numpy as np 
import matplotlib.pyplot as plt
import tqdm

#plt.rcParams['figure.figsize'] = [15, 15]
#plt.rcParams['figure.dpi'] = 100

data = pygio.read_genericio("data/hacc_128.dat", ["x", "y", "z"])

coords = np.column_stack((data["x"],data["y"],data["z"]))
#coords = coords[::50]
coords = coords/128
coords *= 32
coords -= 16

Ng = 32.0

im_x = 1080
im_y = 1080

SpaceVis.gpurenderer.GPU_loadpoints(coords)

SpaceVis.gpurenderer.GPU_init()
idx = 0
rot_z = 0
for cam_z in tqdm.tqdm(np.linspace(-10,20,60)):

    cam_pos = np.array([0,0,cam_z],dtype=np.float32)
    cam_rot = np.array([0,0,rot_z],dtype=np.float32)
    e = np.array([0,0,10],dtype=np.float32)

    rot_z += 0.01

    out = SpaceVis.gpurenderer.draw_frame_GPU(cam_pos,cam_rot,e,im_x,im_y,coords,50,Ng,2,2,2)

    #SpaceVis.renderer.GPU_close()

    out.tofile("raw_frames/frame" + str(idx) + ".dat")
    idx += 1
#plt.show()