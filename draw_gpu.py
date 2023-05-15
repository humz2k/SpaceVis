import numpy as np
import matplotlib.pyplot as plt
import tqdm

for idx in tqdm.tqdm(range(450)):
    out = np.fromfile("frames/small" + str(idx) + ".dat",dtype=np.float32).reshape(1080,1080)
    #print(np.max(out),np.min(out))
    plt.imshow(out,cmap="inferno",vmax = 0.02, vmin=0)#,vmax=4,vmin=0))
    plt.axis('off')
    plt.savefig("frames/step" + str(idx) + ".jpg",bbox_inches='tight',pad_inches = 0,dpi=600)
    plt.close()
    #exit()