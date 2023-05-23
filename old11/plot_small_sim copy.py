import SpaceVis
import numpy as np
import matplotlib.pyplot as plt
import tqdm


Ng = 32
steps = 200
n_particles = Ng*Ng*Ng

im_x = 1080
im_y = 1080

#col_max = 120
col_max = 40
rot_z = 0

data = np.fromfile("data/small_sim.dat",dtype=np.float32)
data = data.reshape(steps+1,n_particles,3)

idx = 0
for cam_z in tqdm.tqdm(np.linspace(-10,32+10,600)):

    cam_pos = np.array([16,16,cam_z],dtype=float)
    cam_rot = np.array([0,0,rot_z],dtype=float)
    rot_z += 0.01
    e = np.array([0,0,10],dtype=float)

    out = SpaceVis.renderer.draw_frame(cam_pos,cam_rot,e,im_x,im_y,data[-1],100,32,4,4,4)
    #print(np.max(out))

    plt.imshow(out,cmap="inferno",vmax=0.03,vmin=0)
    plt.axis('off')
    plt.savefig("frames/step" + str(idx) + ".jpg",bbox_inches='tight',pad_inches = 0,dpi=600)
    plt.close()
    

    idx += 1
    #exit()
    #plt.show()