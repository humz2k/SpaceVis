from multiprocessing import Pool
import SpaceVis
import numpy as np
import matplotlib.pyplot as plt
import tqdm
import time
import interpolation

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
    redshift,data,idx,cam_pos_x,cam_pos_y,cam_pos_z,cam_rot_x,cam_rot_y,cam_rot_z,e_x,e_y,e_z,im_x,im_y,scale,blur_focus,sqr,depth_bins,ng,v_max = inputs
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
    redshift = (redshift/199)*200
    redshift = str(int(200-redshift))
    plt.text(20,45,"z=" + redshift,c=(1,1,1),backgroundcolor=None)
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
        out = (data_frames[i],data[data_frames[i]],i,
                cam_pos_x[i],cam_pos_y[i],cam_pos_z[i],
                cam_rot_x[i],cam_rot_y[i],cam_rot_z[i],
                e_x[i],e_y[i],e_z[i],
                im_x,im_y,
                scale[i],blur_amount[i],sqr[i],depth_bins,ng,v_max[i])
        map_inputs.append(out)
    if __name__ == '__main__':
        start = time.perf_counter()
        with Pool(n_threads) as p:
            p.map(__draw, map_inputs[200:])
        end = time.perf_counter()
        print("Executed in: " + str(end - start))

def keyframes(*keyframes,degree=3,sub_sample=2):
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
    interpolated = interpolation.interpolate(np.array(out,dtype=np.float32),degree=degree,sub_sample=sub_sample)
    return interpolated

def raw_keyframes(*keyframes):
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
n_frames = 330
Ng = 32
steps = 200
n_particles = Ng*Ng*Ng

im_x = 1080
im_y = 1920

#col_max = 120
col_max = 40
rot_z = 0

zoom_start = 50
zoom_end = 80
unzoom_start = 90
unzoom_end = 120
expand_start = 160
end_expand = 190

cam_pos_x = keyframes((0,16),(n_frames,16))
cam_pos_y = keyframes((0,16),(n_frames,16))
cam_pos_z = keyframes((0,0),(end_expand,0),(n_frames-15,32),(n_frames,25),sub_sample=10,degree=6)

shake_x_1,shake_y_1 = SpaceVis.camera_shaker.get_camera_shake(n_frames,octaves=1)
shake_x_2,shake_y_2 = SpaceVis.camera_shaker.get_camera_shake(n_frames,octaves=6)
shake_x = shake_x_1 * 0.05 + shake_x_2 * raw_keyframes((0,1),(zoom_start-10,0),(expand_start,0),(expand_start+10,1),(end_expand-5,1),(end_expand,0.1),(n_frames,0))
shake_y = shake_y_1 * 0.05 + shake_y_2 * raw_keyframes((0,1),(zoom_start-10,0),(expand_start,0),(expand_start+10,1),(end_expand-5,1),(end_expand,0.1),(n_frames,0))
cam_rot_x = keyframes((0,0),(end_expand,0),(240,np.pi/2),(300,0),(n_frames,0),sub_sample=20,degree=6) + shake_x #* raw_keyframes((0,0.05),(zoom_start-5,0.05),(zoom_start,0.05),(unzoom_end,0.05),(expand_start+10,10),(n_frames,5))
cam_rot_y = keyframes((0,0),(end_expand,0),(240,np.pi/2),(300,0),(n_frames,0),sub_sample=20,degree=6) + shake_y #* raw_keyframes((0,0.05),(zoom_start-5,0.05),(zoom_start,0.05),(unzoom_end,0.05),(expand_start+10,10),(n_frames,5))
cam_rot_z = keyframes((0,0),(unzoom_end,0),(n_frames,2),sub_sample=20)

#plt.plot(shake_x)
#plt.plot(shake_y)
#plt.show()
#exit()

e_x = keyframes((0,0),(n_frames,0))
e_y = keyframes((0,0),(n_frames,0))
#e_z = keyframes((0,10),(zoom_start,10),(zoom_end,30000),(unzoom_start,30000),(unzoom_end,10))#[::-1]
e_z = keyframes((0,10),(zoom_start,10),((unzoom_start - zoom_end)//2 + zoom_end,30000),(unzoom_end,10),(n_frames,10),sub_sample=5,degree=6)#[::-1] 

#plt.plot(e_z)
#plt.plot(shake_x)
#plt.plot(shake_y)
#plt.show()
#exit()

scale = keyframes((0,0.001),(expand_start,0.001),(end_expand,1),(n_frames,1),sub_sample=5)

#blur_focus = keyframes((0,-128),(20,0),(zoom_start,16),(zoom_end,-16),((unzoom_start-zoom_end)//2 + zoom_end - 10,16),((unzoom_start-zoom_end)//2 + zoom_end + 10,16),(unzoom_start,-16),(unzoom_end,16),(end_expand,16),(n_frames,5))#[::-1] #np.linspace(-128,16,n_frames,dtype=np.float32)#np.zeros(n_frames,dtype=np.float32)

#plt.plot(scale/np.max(scale))
#plt.plot(e_z/np.max(e_z))
#plt.plot(blur_focus)
blur_focus = keyframes((0,-128),(20,0),(zoom_start,16),(zoom_end,-16),((unzoom_start-zoom_end)//2 + zoom_end - 3,16),((unzoom_start-zoom_end)//2 + zoom_end + 3,16),(unzoom_start,-16),(unzoom_end,16),(end_expand,16),(300,32),(n_frames,0),sub_sample=5)#[::-1] #np.linspace(-128,16,n_frames,dtype=np.float32)#np.zeros(n_frames,dtype=np.float32)

sqr = keyframes((0,2),(n_frames,2))
init = np.linspace(0,199,95).astype(np.int32)
unzoom = np.linspace(0,199,35).astype(np.int32)[::-1]
expand = np.linspace(0,199,85).astype(np.int32)
data_frames = np.concatenate((init,unzoom,expand,np.array([199]*(n_frames-len(init)-len(unzoom) + len(expand)),dtype=np.int32)))

v_max = raw_keyframes((0,0),(unzoom_end,0),(expand_start-1,0),(expand_start,0.03),(n_frames,0.03))#keyframes((0,500),(zoom_start-1,500),(zoom_start,0),(zoom_end-1,0),(zoom_end,0.03),(unzoom_start-1,0.03),(unzoom_start,0),(unzoom_end-1,0),(unzoom_end,500))#keyframes((0,500),(30,500),(31,50),(38,5),(50,2),(60,0.5),(112,1),(120,500))#[::-1]

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
