import numpy as np
import matplotlib.pyplot as plt
import tqdm

stars = np.fromfile("../data/stars.dat",dtype=np.float32)
stars = stars.reshape(stars.shape[0]//3,3)[::10]

gas = np.fromfile("../data/gas.dat",dtype=np.float32)
gas = gas.reshape(gas.shape[0]//3,3)

im_x = 256
im_y = 256

cam_pos = np.array([0,0,-1],dtype=np.float32)
cam_rot = np.array([0,0,0],dtype=np.float32)
cam_e = np.array([0,0,1])

def plot3d(*data):
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    for i in data:
        ax.scatter(i[:,0],i[:,1],i[:,2])
    ax.set_zlabel("z")
    plt.show()

def project(particles,cam_pos,cam_rot,cam_e,im_x,im_y):
    rot_mat_1 = np.array([[1,0,0],
                          [0,np.cos(cam_rot[0]),np.sin(cam_rot[0])],
                          [0,-np.sin(cam_rot[0]),np.cos(cam_rot[0])]])
    rot_mat_2 = np.array([[np.cos(cam_rot[1]),0,-np.sin(cam_rot[1])],
                          [0,1,0],
                          [np.sin(cam_rot[1]),0,np.cos(cam_rot[1])]])
    rot_mat_3 = np.array([[np.cos(cam_rot[2]),np.sin(cam_rot[2]),0],
                          [-np.sin(cam_rot[2]),np.cos(cam_rot[2]),0],
                          [0,0,1]])
    rot_mat = rot_mat_1 @ rot_mat_2 @ rot_mat_3

    new_coords = (particles-cam_pos)
    new_coords = (rot_mat @ new_coords.T).T

    bx = (((cam_e[2]/new_coords[:,2])*new_coords[:,0] + cam_e[0]) + 0.5)*(im_x-1)
    by = (((cam_e[2]/new_coords[:,2])*new_coords[:,1] + cam_e[1]) + 0.5)*(im_y-1)

    out = np.column_stack((bx,by,new_coords[:,0],new_coords[:,1],new_coords[:,2]))
    out = out[new_coords[:,2] >= 0]
    out = out[out[:,0] >= 0]
    out = out[out[:,0] < im_x]
    out = out[out[:,1] >= 0]
    out = out[out[:,1] < im_y]
    return out[:,:2],out[:,2:]

def psf(point,col,r=3,mul=0.1):
    out = np.zeros((2*r+1,2*r+1,3),dtype=np.float32)
    for i in range(2*r+1):
        for j in range(2*r+1):
            tot_dist = (abs(i-(r))/(mul*r) + abs(j-(r))/(mul*r)) + 1
            ratio = 1/(tot_dist*tot_dist+1)
            out[i,j] = col*point*ratio
    out /= np.sum(out)
    return out * point

projected,new_gas = project(gas,cam_pos,cam_rot,cam_e,im_x,im_y)

star_color = np.array([1,1,1],dtype=np.float32)
gas_colors = np.zeros_like(new_gas)
for idx,gas_particle in tqdm.tqdm(enumerate(new_gas),total = len(new_gas)):
    distances = np.linalg.norm(stars - gas_particle,axis=1)
    ratio = np.sum(1/(distances*distances))
    gas_colors[idx] = ratio * star_color

gas_colors /= np.max(gas_colors)

r = 10

#projected,pos = project(gas,cam_pos,cam_rot,cam_e,im_x,im_y)
#projected = projected.astype(np.int32)
#distances = np.linalg.norm(pos,axis=1)
#distances = (1/(distances*distances))

grid = np.zeros((im_x,im_y,3),dtype=np.float32)

col = np.array([1,1,1],dtype=np.float32)

for pixel,dist in tqdm.tqdm(zip(projected,gas_colors),total=len(projected)):
    point = psf(1,dist,r)
    left_x = pixel[0]-r
    right_x = pixel[0]+r+1
    left_y = pixel[1]-r
    right_y = pixel[1]+r+1
    point_lx = 0
    point_rx = 2*r+1
    point_ly = 0
    point_ry = 2*r+1
    if (left_x < 0):
        point_lx -= left_x
        left_x = 0
    if (left_y < 0):
        point_ly -= left_y
        left_y = 0
    if (right_x >= im_x):
        point_rx -= right_x - (im_x-1)
        right_x = im_x - 1
    if (right_y >= im_y):
        point_ry -= right_y - (im_y-1)
        right_y = im_y - 1
    #print(left_x,right_x,left_y,right_y,point_lx,point_rx,point_ly,point_ry)
    grid[left_x:right_x,left_y:right_y] += point[point_lx:point_rx,point_ly:point_ry]
    

grid /= np.max(grid)

plt.imshow(grid)
plt.savefig("blob.jpg")
plt.show()
#tar = psf(1000,col,10,mul=0.04)
#plt.imshow(star)
#plt.show()