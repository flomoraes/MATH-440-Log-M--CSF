import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev


def dist(x1,y1,x2,y2):
    return np.sqrt((np.abs(x2-x1))**2 + (np.abs(y2-y1))**2)




#REQUIRES: deg is a float between [0,2pi), (tentatively) both upper bounds, scale >= 0
def random_init(num_pts, x_upper, y_upper, deg, scale):
    result = np.random.random((num_pts, 2)) * np.array([x_upper, y_upper])

    degs = deg * np.random.random(num_pts)
    scales = scale * np.random.random(num_pts)

    x_shift = scales * np.array(np.cos(degs))
    y_shift = scales * np.array(np.sin(degs))

    shift = np.column_stack((x_shift, y_shift))

    return result + shift


def init_naive(result):
    n = len(result)
    mat = np.zeros((n,n))

    for i in range(0, n):
        for j in range(i+1, n):
            d = dist(result[i][0], result[i][1], result[j][0], result[j][1])
            mat[i,j] = d
            mat[j,i] = d

    return mat


def find_naive(mat):
    n = len(mat)

    search = mat.copy()

    current = 0
    tour = [current]

    search[:, current] = np.inf

    for k in range(1, n):
        next_node = np.argmin(search[k])

        tour.append(next_node)
        search[:, k] = np.inf
        current = next_node

    tour.append(tour[0])
    return tour

    

#REQUIRES: result is valid array of points
def tsp(result):
    # so our goal here is to use 2-opt TSP to connect these points

    #first do a naive tour so we have a benchmark
    mat = init_naive(result)
    naive = find_naive(mat)
 
    improved = True
    
    while(improved):
        improved = False

        for i in range(1, len(naive) - 2):
            for j in range(i+1, len(naive) - 1):
                A,B = naive[i-1],naive[i]
                C,D = naive[j],naive[j+1]

                #check if an improvement may be made
                old = mat[A,B] + mat[C,D]
                new = mat[A,C] + mat[B,D]

                if(old > new):
                    naive[i : j+1] = naive[i : j+1][::-1]
                    improved = True    

    
    return naive


def plot_route(result, tour):

    path = tour + [tour]

    x = [result[i][0] for i  in tour]
    y = [result[i][1] for i in tour]
    
    plt.plot(x,y, marker = 'o', linestyle = '-', color = 'blue')    
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.show()




def plot_result(result):

    x = result[:, 0]
    y = result[:, 1]

    plt.scatter(x,y)

    plt.grid(True)
    plt.show()


def interpolate(result, tour):

    x = [result[i][0] for i  in tour]
    y = [result[i][1] for i in tour]

    tck, u = splprep([x,y], s = 2000, k = 5, per = True)

    u_new = np.linspace(0,1,300)

    x_smooth, y_smooth = splev(u_new, tck)

    return x_smooth, y_smooth


def plot_smooth(x_smooth, y_smooth):
    plt.plot(x_smooth, y_smooth)
    plt.grid(True)
    plt.show()


#TESTING BLOCK
def main():
    result = random_init(100, 100, 100, (np.pi / 6), 5)
    plot_result(result)

    tour = tsp(result)

    #check tsp is right
    plot_route(result, tour)

    x_s, y_s = interpolate(result, tour)
    plot_smooth(x_s, y_s)

    # can still overlap from interpolation, 
    # but it could be from smoothing factor being too high, 
    # so need to see what smoothing factor to pick
    return 0

if __name__ == "__main__":
    main()
    return 0

if __name__ == "__main__":
    main()
