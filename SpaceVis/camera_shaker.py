import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
import numpy as np

#xpix, ypix = 100, 100
#pic = np.array([[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)])
def get_camera_shake(frames,max_degrees=10,octaves=3):
    noise_x = PerlinNoise(octaves=octaves, seed=21082001)
    noise_y = PerlinNoise(octaves=octaves, seed=12032001)
    xs = np.radians(np.degrees(np.array([[noise_x(i/frames),noise_y(i/frames)] for i in range(frames)]))/max_degrees)
    return xs[:,0],xs[:,1]

#plt.plot(xs[:,0])
#plt.plot(xs[:,1])
#plt.show()
#plt.imshow(pic, cmap='gray')
#plt.show()

if __name__ == "__main__":
    xs,ys = get_camera_shake(30,octaves=1)
    plt.plot(xs)
    plt.plot(ys)
    plt.show()