import cv2
import numpy as np
import math
from scipy.ndimage import gaussian_filter
from numpy.fft import fft2, ifft2
from utils import segmentation, normalise, gaussian_kernel, clip



def apply_to_components(I, func, base, n_tones, *args):
    if I.ndim > 3:
        I = I[:, :, :3]
    I = 255 * normalise(I)
    if base == 'gray':
        if I.ndim == 3:
            I = .2989 * I[:, :, 0] + .5870 * I[:, :, 1] + .1140 * I[:, :, 2]
        output = func(I, *args, n_tones=n_tones)
    elif base == 'RGB':
        R, G, B = [func(I[:, :, i], *args, n_tones=n_tones) for i in range(3)]
        output = np.stack((R, G, B), axis=-1)
    else:
        raise ValueError("Only support 'gray' or 'RGB'")
    return output.astype(np.uint8)


mu, k, n_iter = 2, 1.6, 3

def fdog(I, sigma_c=.2, sigma_e=1.5, sigma_m=2.4, sigma_a=2, p=25, epsilon=20, phi=np.inf, base='gray', n_tones=None):
    """
    Apply the FDoG algorithm to a picture I.

    Parameters:
        I: array of dimension 2 or 3
            Picture on which FDoG will be applied.
        sigma_c: float
            Standard deviation of the Gaussian used to blur the image before computing its
            edge tangent flow. Use smaller values to make to make the algorithm more perceptive of details,
            but also more sensitive to noise.
            We often use 0.2 <= sigma_c <= 1, but the value depends on the size of the picture.
        sigma_e: float
            Standard deviation of the Gaussians used to convolve the image perpendicularly to its edges.
            Depitcs the spatial support of FDoG. Use higher values to make the output coarser and more
            abstract.
            We often put its value around 2, but the value depends on the size of the picture.
        sigma_m: float
            Standard deviation of the first line integral convolution. Use a higher value to increase the
            coherence of the result, at the risk of it to be more noisy.
            We often use .5 <= sigma_m <= 10, but the value depends on the size of the picture.
        sigma_a: float
            Standard deviation of the second line integral convolution. Use a higher value to increase the
            coherence of the result, at the risk of it to be more noisy.
            We often use .5 <= sigma_a <= 10, but the value depends on the size of the picture.
        p: float
            Depicts the sharpness of the output. Use higher values to catch more subtle details, at the
            risk of making the algorithm more sensitive to noise.
            We often use values of p between 5 and 30.
        epsilon: float
            Describes at which value the filter goes from a constant to a hyperbolic
            tangent. Use a higher value to make the output darker and more dramatic.
            We often use values of epsilon between 15 and 65.
        phi: float or np.inf
            Describe the slope of the second part of the filter.
            Use a lower value to add shades of gray to the result. Use a negative value to reverse the
            colors of the output.
            We often use values between 0.008 and 0.02 as the output doesn't change much past 0.02.
        base: str ('gray', 'RGB' or 'HSV')
            Tells in which color base the FDoG algorithm will be applied.
                - If base is set to 'gray', then the algorithm will run once on the image, preemptively
                turned to a grayscale image.
                - If base is set to 'RGB', then the algorithm will run on every component (red, green and
                blue) of the image. The output will be a combination of the three results.
                - If base is set to 'HSV', then the algorithm will run only on the value component. The
                result will be combined with the original hue and saturation components to make up the
                output.
        n_tones: int or None
            Number of tones of the output. Can be used as an additional effect. Set this parameter to None
            to ignore this step of the algorithm and to make the output keep all of its colors.
            When it is not set to None, we often restrict the output to 3 or 4 tones.

    Returns:
        Output of the FDoG algorithm applied to the given color base.
    """
    return apply_to_components(I, fdog_core, base, n_tones, sigma_c, sigma_e, sigma_m, sigma_a, p,
                               epsilon, phi)


def fdog_core(I, sigma_c, sigma_e, sigma_m, sigma_a, p, epsilon, phi, n_tones=None):
    #Compute the edge tangent flow.
    grad_magn0, grad0 = get_gradient(I)
    ETF = get_edge_tangent_flow(flow_iteration(gaussian_filter(I, sigma_c), grad_magn0, grad0))

    #Convolve perpendicularly to edges.
    g1 = convolve_perpendicular(I, ETF, sigma_e)
    gk = convolve_perpendicular(I, ETF, k*sigma_e)

    #Rescale phi and epsilon with respect to p.
    phi0 = phi*(p+1)
    epsilon0 = epsilon/(p+1)
    tau = p/(p+1)

    #Apply the filter.
    D = g1 - tau*gk
    filtered = np.where(D >= epsilon0, 1+np.tanh(phi0*D), 1)

    #Eventually quantify the tones of the output.
    if n_tones is not None:
        filtered = segmentation(filtered, n_tones, mmin=1, mmax=2)

    #Apply two line integral convolutions to increase the coherence of the output.
    O = lic(filtered, np.cos(ETF), np.sin(ETF), sigma_m)
    O = lic(O, np.cos(ETF), np.sin(ETF), sigma_a)
    return normalise(O)*255


def lic(texture, v_x, v_y, sigma):
    """
    Perform Line Integral Convolution on a given texture with a given vector field.

    Parameters:
    texture (numpy.ndarray): Input 2D grayscale texture.
    v_x (numpy.ndarray): x-component of the vector field.
    v_y (numpy.ndarray): y-component of the vector field.
    sigma (float): Standard deviation of the Gaussian kernel.

    Returns:
    numpy.ndarray: Output texture after LIC.
    """
    # Determine kernel length based on sigma
    kernel_length = int(sigma * 3) * 2 + 1  # Cover +/- 3 sigma range
    kernel = gaussian_kernel(sigma, kernel_length)

    # Create an output texture
    output_texture = np.zeros_like(texture)

    # Get texture dimensions
    height, width = texture.shape

    # Traverse each pixel in the texture
    for y in range(height):
        for x in range(width):
            # Initialize position and sample list
            pos_x = x
            pos_y = y
            samples = []
            weights = []

            # Collect samples along the streamline in the forward direction
            for i in range(kernel_length // 2):
                if 0 <= int(pos_x) < width and 0 <= int(pos_y) < height:
                    samples.append(texture[int(pos_y), int(pos_x)])
                    weights.append(kernel[kernel_length // 2 + i])
                    pos_x_tmp, pos_y_tmp = pos_x, pos_y
                    pos_x += v_x[int(pos_y_tmp), int(pos_x_tmp)]
                    pos_y += v_y[int(pos_y_tmp), int(pos_x_tmp)]
                    # Clamp position to stay within bounds
                    pos_x = clip(pos_x, 0, width - 1)
                    pos_y = clip(pos_y, 0, height - 1)
                else:
                    break

            # Reset position and collect samples in the backward direction
            pos_x = x
            pos_y = y
            for i in range(kernel_length // 2):
                if 0 <= int(pos_x) < width and 0 <= int(pos_y) < height:
                    samples.append(texture[int(pos_y), int(pos_x)])
                    weights.append(kernel[kernel_length // 2 - i - 1])
                    pos_x_tmp, pos_y_tmp = pos_x, pos_y
                    pos_x -= v_x[int(pos_y_tmp), int(pos_x_tmp)]
                    pos_y -= v_y[int(pos_y_tmp), int(pos_x_tmp)]
                    # Clamp position to stay within bounds
                    pos_x = clip(pos_x, 0, width - 1)
                    pos_y = clip(pos_y, 0, height - 1)
                else:
                    break

            # Perform convolution by weighted averaging of the samples
            if samples:
                output_texture[y, x] = np.average(samples, weights=weights)

    return output_texture


def convolve_perpendicular(I, ETF, sigma):
    """
    Convolve the image I pointwise, with a Gaussian that is perpendicular
    to the edge.

    Parameters
    ----------
    I : 2d-array of floats
        Image to convolve.
    ETF : 2d-array
        Edge tangent flow at each point of I.
        Contains data about the direction of the edge at each point.
    sigma : flat
        Standard deviation of the Gaussian.

    Returns
    -------
    O : 2d-array
        Convolved image.

    """
    N, M = I.shape
    O = np.zeros((N, M))
    for x in range(N):
        for y in range(M):
            theta = ETF[x, y] + np.pi / 2
            gaussian = get_tilted_gaussian(sigma, theta)
            O[x, y] = convolve_pointwise(I, gaussian, x, y)
    return O


def convolve_pointwise(I, kernel, x, y):
    size = kernel.shape[0]
    N, M = I.shape
    summation = 0.0
    for i in range(-size // 2 + 1, size // 2 + 1):
        for j in range(-size // 2 + 1, size // 2 + 1):
            if 0 <= x - i < N and 0 <= y - j < M:
                summation += kernel[i + size // 2, j + size // 2] * I[x - i, y - j]  # formula for discrete convolution
    return summation


def get_tilted_gaussian(sigma, theta, sigma_minor=0.5):
    """
    Create the Gaussian of standard deviation sigma, tilted with angle theta.

    Parameters
    ----------
    sigma : float
        Standard deviation of the Gaussian.
    theta : float
        Angle with which the Gaussian should be tilted.
    sigma_minor : float, optional
        Standard deviation of the Gaussian of its second axis. The default is 0.5.

    Returns
    -------
    gauss : TYPE
        DESCRIPTION.

    """
    # Create the coordinate grid
    size = int(sigma * 1) * 2 + 1  # Cover +/- 3 sigma range
    center = (size - 1) / 2
    x = np.linspace(-center, center, size)
    y = np.linspace(-center, center, size)

    # Create the meshgrid
    x_grid = np.zeros((size, size))
    y_grid = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            x_grid[i, j] = x[j]
            y_grid[i, j] = y[i]

    # Apply the rotation
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    x_rot = cos_theta * x_grid + sin_theta * y_grid
    y_rot = -sin_theta * x_grid + cos_theta * y_grid

    # Calculate the unidirectional Gaussian values
    gauss = np.exp(-((x_rot / sigma) ** 2 + (y_rot / sigma_minor) ** 2) / 2)
    gauss /= np.sum(np.abs(gauss))
    return gauss


def get_gradient(I):
    """
    Compute the gradient of the image using Sobel operators.

    Parameters
    ----------
    I : 2d-array
        Image whose gradient should be computed.

    Returns
    -------
    2d-array
        Normalised magnitude of the gradient at each point.
    grad : 2d-array
        Gradient.

    """
    sobel_x = cv2.Sobel(I, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(I, cv2.CV_64F, 0, 1, ksize=3)
    # edge_tangent = np.arctan2(sobel_y, sobel_x) #get a direction from the data in x and y
    grad_magn = np.hypot(sobel_x, sobel_y)
    grad = np.stack((sobel_x, sobel_y), axis=-1)
    return normalise_classic(grad_magn), grad



def flow_iteration(I, grad_magn0, grad0):
    """
    Iterative algorithm that computes the edge tangent flow of an image from
    its gradient. This function is based on the paper "Flow-based image
    abstraction", written by Henry Kang, Seungyong Lee, and Charles K Chui in 2008.

    Parameters
    ----------
    I : 2d-array
        Image whose edge tangent flow should be computed.
    grad_magn0 : 2d-array
        Normalised magnitude of the gradient of the image at each point.
    grad0 : 2d-array
        Gradient of the image at each point.

    Returns
    -------
    t : 2d-array
        Approximation of the edge tangent flow.

    """
    for n in range(3):
        if n == 0:
            t = np.stack((-grad0[:, :, 1], grad0[:, :, 0]), axis=-1)
            grad_magn = grad_magn0
        else:
            old_t = np.copy(t)
            t = apply_filter(old_t, grad_magn)
            t = normalise_classic(t)
    return t


def apply_filter(old_t, grad_magn):
    N, M = old_t.shape[:2]
    t = np.zeros((N, M, 2))
    for x in range(N):
        for y in range(M):
            t[x][y] = apply_filter_pointwise(old_t, grad_magn, x, y)
    return t



def apply_filter_pointwise(old_t, grad_magn, x, y):
    N, M = old_t.shape[:2]
    summation_x = summation_y = 0
    for i in range(max(x-mu,0), min(x+mu,N)):
        for j in range(max(y-mu,0), min(y+mu, M)):
            if np.sqrt((x - i) ** 2 + (y - j) ** 2) < mu:
                wdsum = np.sum(old_t[x][y] * old_t[i][j])
                out_H = old_t[i][j] * (grad_magn[x][y] - grad_magn[i][j] + 1)/2 * wdsum
                summation_x += out_H[0]
                summation_y += out_H[1]
    return (summation_x, summation_y)


def normalise_classic(I):
    return I / np.sum(np.abs(I))


def get_edge_tangent_flow(t):
    return np.arctan2(t[:, :, 1], t[:, :, 0])
