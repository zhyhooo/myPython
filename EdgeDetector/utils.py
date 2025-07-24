import numpy as np
from numpy.fft import fft2, ifft2



def segmentation(I, n_tones, mmin=0, mmax=255):
    return np.floor(I*(n_tones-1)/(mmax-mmin)+.5)*(mmax-mmin)/(n_tones-1)


def gaussian1d(n, std):
    alpha = 2 * std * std
    logarg = (np.arange(n) - n // 2) ** 2 / alpha
    return np.exp(-logarg) / np.sqrt(np.pi * alpha)


def gaussian2d(m, n, sigma, sigma2):
    g1 = gaussian1d(m, sigma)
    g2 = gaussian1d(n, sigma2)
    return np.outer(g1, g2)


def normalise_2d(I_2d):
    ## normalises I_2d between 0 and 1
    I_2d_min, I_2d_max = np.min(I_2d), np.max(I_2d)
    assert I_2d_max != I_2d_min, ("pure color image, no normalization needed.")
    return (I_2d - I_2d_min)/(I_2d_max - I_2d_min)


def normalise(I, I_min_max=None):
    ## Normalises I between 0 and 1.
    I2 = np.array(I, dtype=np.float64)
    if I2.ndim == 3:
        for i in range(I.shape[2]):
            I2[:,:,i] = normalise_2d(I2[:,:,i])
    else: #I2.ndim=2
        I2 = normalise_2d(I2)
    return I2


def gaussian_kernel(sigma, length):
    x = np.linspace(-length / 2, length / 2, length)
    kernel = np.exp(-0.5 * (x / sigma) ** 2)
    kernel = kernel / np.sum(kernel)
    return kernel


def clip(x, x_min, x_max):
    #Clip the value of the parameter so that it stays within boundaries.
    if x >= x_max:
        return x_max
    if x <= x_min:
        return x_min
    return x


def handle_borders(u):
    """
    inflate image size by 2 in each direction.
    """
    u = np.array(u)
    N, M = u.shape
    blank = np.zeros((2*N, 2*M))
    reversed_x = u[::-1]
    reversed_y = u[:, ::-1]
    reversed_xy = reversed_x[:, ::-1]
    blank[:N, :M] = u
    blank[N:, M:] = reversed_xy
    blank[:N, M:] = reversed_y
    blank[N:, :M] = reversed_x
    return blank


def motion_blur(I, sigma, vertical=False):
    if I.ndim == 3:
        I = .2989*I[:,:,0] + .5870*I[:,:,1] + .1140*I[:,:,2]
    N, M = I.shape
    I = handle_borders(I)
    if vertical:
        gauss = gaussian2d(2*N, 2*M, sigma, 1e-10)
    else:
        gauss = gaussian2d(2*N, 2*M, 1e-10, sigma)
    N, M = I.shape
    blurred = np.real(ifft2(fft2(gauss)*fft2(I)))[N//2:, M//2:]
    return normalise(blurred)


