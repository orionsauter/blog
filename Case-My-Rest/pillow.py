"""
Adaptation of https://github.com/evouga/DaurizioPaper/blob/master/main.cpp
Implementing https://core.ac.uk/download/pdf/81194615.pdf
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.tri import Triangulation
from scipy.spatial import ConvexHull

def elasticEnergy(q, F, origV):
    kstretch = 500.0
    nfaces = F.shape[0]
    nverts = origV.shape[0]
    result = 0
    deriv = np.zeros((3 * nverts,))
    hess = np.zeros((3 * nverts, 3 * nverts))

    for i in range(nfaces):
        face = F[i, :]
        for v1 in range(3):
            v2 = (v1 + 1) % 3

            op1 = origV[face[v1], :]
            op2 = origV[face[v2], :]
            odist = np.sqrt((op1 - op2).dot(op1 - op2))

            p1 = q[face[v1], :]
            p2 = q[face[v2], :]
            dist = np.sqrt((p1 - p2).dot(p1 - p2))
            if (dist < odist):
               continue
            result += 0.5 * kstretch *\
                (dist - odist)*(dist - odist) / odist / odist
            fi1 = 3 * face[v1]
            fi2 = 3 * face[v2]
            deriv[fi1:(fi1+3)] += kstretch *\
                (dist - odist) * (p1 - p2) / dist / odist / odist
            deriv[fi2:(fi2+3)] -= kstretch *\
                (dist - odist) * (p1 - p2) / dist / odist / odist
            I = np.identity(3)
            localH = kstretch*(p1 - p2).transpose()*(p1 - p2) / \
                     dist / dist / odist / odist + \
                     kstretch * (dist - odist) * \
                     (I / dist - (p1 - p2).transpose()*(p1 - p2) / \
                     dist / dist / dist) / odist / odist

            for j in range(3):
                for k in range(3):
                    hess[3 * face[v1] + j, 3 * face[v1] + k] = localH[j, k]
                    hess[3 * face[v1] + j, 3 * face[v2] + k] = -localH[j, k]
                    hess[3 * face[v2] + j, 3 * face[v1] + k] = -localH[j, k]
                    hess[3 * face[v2] + j, 3 * face[v2] + k] = localH[j, k]

    pressure = 1e-3
    for i in range(nfaces):
        v0 = q[F[i, 0], :]
        v1 = q[F[i, 1], :]
        v2 = q[F[i, 2], :]
        result -= pressure / 6.0 * (np.cross(v0, v1).dot(v2))
        n = np.cross(v1 - v0, v2 - v0)
        for j in range(3):
            deriv[F[i, j]:(F[i, j]+3)] -= pressure / 6.0 * n
    
    return result, deriv, hess

def createMesh(w, h, res):
    xp, yp, zp = np.meshgrid(
        np.arange(0, w, res),
        np.arange(0, h, res),
        res)
    xn, yn, zn = np.meshgrid(
        np.arange(0, w, res),
        np.arange(0, h, res),
        -res)
    # Vertices
    V = np.transpose(np.array([
        np.concatenate((xp.flatten(), xn.flatten())),
        np.concatenate((yp.flatten(), yn.flatten())),
        np.concatenate((zp.flatten(), zn.flatten()))]))

    triang = Triangulation(V[:, 0], V[:, 1])
    # Faces
    F = triang.triangles
    return V, F, triang

def computeVolume(V):
    return ConvexHull(V).volume

def takeOneStep(curV, origV, F, reg):
    nverts = curV.shape[0]
    freeDOFs = 3 * nverts

    while (True):

        energy, derivative, hessian = \
            elasticEnergy(curV, F, origV)    

        I = np.identity(freeDOFs)
        hessian += reg * I;        

        # hessian * fullDir = derivative
        fullDir = np.linalg.solve(hessian, derivative)

        newPos = curV + np.reshape(fullDir, (nverts, 3))
        newenergy, derivative, hessian = \
            elasticEnergy(newPos, F, origV)       

        if (newenergy <= energy):
            print("Old energy: ", energy, " new energy: ", newenergy)
            print("Volume is ", computeVolume(newPos, F))
            curV = newPos
            reg = np.max(1e-6, reg/2.0)
            break
        else:
            reg *= 2.0
            print("Old energy: ", energy, " new energy: ", newenergy)
    return curV, reg


if (__name__ == "__main__"):
    fig = plt.figure(figsize=plt.figaspect(0.5))
    ax = fig.add_subplot(1, 2, 1, projection='3d')
    origV, F, triang = createMesh(65, 65, 2)
    ax.plot_trisurf(origV[:,0], origV[:,1], origV[:,2],
                    triangles=triang.triangles,
                    cmap=plt.cm.Spectral)
    plt.show()
    curV = origV
    
    reg = 1e-6
    for i in range(100):
        curV, reg = takeOneStep(curV, origV, F, reg)
        ax.plot_trisurf(curV[:,0], curV[:,1], curV[:,2],
                        triangles=triang.triangles,
                        cmap=plt.cm.Spectral)
        plt.show()
