from multiprocessing import Pool
import SpaceVis
import numpy as np
import matplotlib.pyplot as plt
import tqdm
import time

plt.rcParams['figure.figsize'] = [10, 10]
plt.rcParams['figure.dpi'] = 100

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
                final += SpaceVis.renderer.blur(i,size,blur)
    return final

def __draw(inputs):
    data,idx,cam_pos_x,cam_pos_y,cam_pos_z,cam_rot_x,cam_rot_y,cam_rot_z,e_x,e_y,e_z,im_x,im_y,scale,blur_focus,sqr,depth_bins,ng,v_max = inputs
    print("Rendering frame: " + str(idx))
    start = time.perf_counter()
    pixel_box = 50 #100
    vmax_mul = 0.9418932243289341
    maxs = []
    cam_pos = np.array([cam_pos_x,cam_pos_y,cam_pos_z],dtype=np.float32)
    cam_rot = np.array([cam_rot_x,cam_rot_y,cam_rot_z],dtype=np.float32)
    e = np.array([e_x,e_y,e_z],dtype=np.float32)
    out = SpaceVis.renderer.draw_frame(cam_pos,cam_rot,e,im_x,im_y,scale_data(data,scale,ng),pixel_box,ng,ng*scale,4,4,4,depth_bins=depth_bins)
    final = do_blurs(out,blur_focus,depth_bins,sqr=sqr,mul=30)
    if v_max == 0:
        plt.imshow(final,cmap="inferno")#,vmax=v_max,vmin=0)#,vmax=0.03,vmin=0)
    else:
        plt.imshow(final,cmap="inferno",vmax=v_max,vmin=0)#,vmax=0.03,vmin=0)
    plt.axis('off')
    plt.savefig("temp/step" + str(idx) + ".jpg",bbox_inches='tight',pad_inches = 0,dpi=600)
    plt.close()
    end = time.perf_counter()
    print("Finished frame: " + str(idx) + " in",end-start)

def draw_parallel(n_threads,n_frames,data,im_x,im_y,ng=32,depth_bin_end=128,depth_bin_step=5,**keyframes):
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
        out = (data[data_frames[i]],i,
                cam_pos_x[i],cam_pos_y[i],cam_pos_z[i],
                cam_rot_x[i],cam_rot_y[i],cam_rot_z[i],
                e_x[i],e_y[i],e_z[i],
                im_x,im_y,
                scale[i],blur_amount[i],sqr[i],depth_bins,ng,v_max[i])
        map_inputs.append(out)
    if __name__ == '__main__':
        start = time.perf_counter()
        with Pool(n_threads) as p:
            p.map(__draw, map_inputs)
        end = time.perf_counter()
        print("Executed in: " + str(end - start))

def keyframes(*keyframes):
    out = []
    for i in range(len(keyframes)-1):
        start = keyframes[i]
        end = keyframes[i+1]
        begin_frame = start[0]
        end_frame = end[0]
        start_val = start[1]
        end_val = end[1]
        if len(end) == 0:
            out += (np.linspace(start_val,end_val,end_frame - begin_frame)**2).tolist()
        else:
            out += np.linspace(start_val,end_val,end_frame - begin_frame).tolist()
    return np.array(out,dtype=np.float32)

    #return map_inputs

n_threads = 5
n_frames = 200
Ng = 32
steps = 200
n_particles = Ng*Ng*Ng

im_x = 1080
im_y = 1920

#col_max = 120
col_max = 40
rot_z = 0

zoom_start = 30
zoom_end = 60
unzoom_start = 170
unzoom_end = 200

cam_pos_x = keyframes((0,16),(n_frames,16))
cam_pos_y = keyframes((0,16),(n_frames,16))
cam_pos_z = keyframes((0,0),(n_frames,0))

shake_x,shake_y = SpaceVis.camera_shaker.get_camera_shake(n_frames,octaves=1)
cam_rot_x = keyframes((0,0),(n_frames,0)) + shake_x * keyframes((0,1),(zoom_start-5,1),(zoom_start,0.01),(unzoom_end,0.01))
cam_rot_y = keyframes((0,0),(n_frames,0)) + shake_y * keyframes((0,1),(zoom_start-5,1),(zoom_start,0.01),(unzoom_end,0.01))
#plt.plot(cam_rot_x)
#plt.plot(cam_rot_y)
#plt.show()
cam_rot_z = keyframes((0,0),(n_frames,0))

e_x = keyframes((0,0),(n_frames,0))
e_y = keyframes((0,0),(n_frames,0))
#e_z = keyframes((0,10),(zoom_start,10),(zoom_end,30000),(unzoom_start,30000),(unzoom_end,10))#[::-1]
e_z = keyframes((0,10),(zoom_start,10),((unzoom_start - zoom_end)//2 + zoom_end,30000),(unzoom_end,10))#[::-1] 

scale = keyframes((0,0.001),(n_frames,0.001))
blur_focus = keyframes((0,-128),(20,0),(zoom_start,16),(zoom_end,-128),((unzoom_start-zoom_end)//2 + zoom_end - 30,16),((unzoom_start-zoom_end)//2 + zoom_end + 30,16),(unzoom_start,-128),(unzoom_end,16))#[::-1] #np.linspace(-128,16,n_frames,dtype=np.float32)#np.zeros(n_frames,dtype=np.float32)
sqr = keyframes((0,2),(n_frames,2))
data_frames = np.arange(n_frames,dtype=np.int32)

v_max = keyframes((0,0),(zoom_end-1,0),(zoom_end,0.01),(unzoom_start-1,0.01),(unzoom_start,0),(unzoom_end,0))#keyframes((0,500),(zoom_start-1,500),(zoom_start,0),(zoom_end-1,0),(zoom_end,0.03),(unzoom_start-1,0.03),(unzoom_start,0),(unzoom_end-1,0),(unzoom_end,500))#keyframes((0,500),(30,500),(31,50),(38,5),(50,2),(60,0.5),(112,1),(120,500))#[::-1]

data = np.fromfile("data/small_sim.dat",dtype=np.float32)
data = data.reshape(steps+1,n_particles,3)

map_inputs = draw_parallel(n_threads,n_frames,data,im_x,im_y,depth_bin_step=5,
              cam_pos_x = cam_pos_x,
              cam_pos_y = cam_pos_y,
              cam_pos_z = cam_pos_z,
              cam_rot_x = cam_rot_x,
              cam_rot_y = cam_rot_y,
              cam_rot_z = cam_rot_z,
              e_x = e_x,
              e_y = e_y,
              e_z = e_z,
              scale = scale,
              blur_focus = blur_focus,
              sqr = sqr,
              data_frames = data_frames,
              v_max = v_max,
              ng = Ng)
    

#def f(inputs):
#    x,y = inputs
#    return x*x

#if __name__ == '__main__':
    #with Pool(3) as p:
    #    print(p.map(f, [(1,0), (2,0), (3,0), (5,0)]))
#if __name__ == '__main__':
#    with Pool(n_threads) as p:
#        p.map(__draw, map_inputs)
