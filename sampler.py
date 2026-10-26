from collections import queue
import numpy as np
import matplotlib.pyplot as plt

#REQUIRES: deg is a float between [0,2pi), (tentatively) both upper bounds, scale >= 0
def random_init(num_pts, x_upper, y_upper, deg, scale):
    result = np.random.random((num_pts, 2)) * np.array([x_upper, y_upper])

    degs = deg * np.random.random(num_pts)
    scales = scale * np.random.random(num_pts)

    x_shift = scales * np.array(np.cos(degs))
    y_shift = scales * np.array(np.sin(degs))

    shift = np.column_stack((x_shift, y_shift))

    return result + shift


#REQUIRES: result is valid array of points, nbhd size >= 1
def graphify(result, nbhd_size):
    unvisited = list(range(len(result)))
    connected = []

    start_idx = np.argmin(results[:,0])

    unvisited.remove(start_idx)
    curr_pt = result[start_idx]

    def_dir = np.array([0.0, 1.0])

    while unvisited:
        
        #get an array of distances so we can find closest ones
        dist = np.linalg.norm(result[unvisited] - currpt, axis = 1)
        candidates = min(nbhd_size, dist)

        closest_idx = np.argsort(dists)[:k]
        

        for candidate in candidates:
            #check angle
            
            #if angle works out, connect (how?)








        unvisited.remove(curr_idx)






    
    return 0



def plot_result(result):

    x = result[:, 0]
    y = result[:, 1]

    plt.scatter(x,y)

    plt.grid(True)
    plt.show()





#TESTING BLOCK
def main():
    plot_result(random_init(8, 10, 10, (np.pi / 6), 5))

    # ok it works!

    return 0

if __name__ == "__main__":
    main()
