import cv2
import numpy as np
from utils import segmentation, normalise, motion_blur
from scipy.ndimage import gaussian_filter


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


def xdog(I, sigma, p=20, epsilon=20, phi=.01, base='gray', n_tones=None):
    """
    Apply the XDoG algorithm to a picture I.
    sigma   - standard deviation of the Gaussians used to convolve the image, usually set around 2.
    p       - depicts the sharpness of the output. Use higher values to catch more subtle details, usually set between 5 and 30.
    epsilon - describes at which value the filter goes from a constant to a hyperbolic tangent.
    phi     - the slope of the second part of the filter.
    base    - 'gray' or 'RGB'
    """
    return apply_to_components(I, xdog_core, base, n_tones, sigma, p, epsilon, phi)


def xdog_core(I, sigma, p, epsilon, phi, n_tones=None, k = 1.5):
    # Convolve with both standard deviations.
    g1 = gaussian_filter(I, sigma)
    gk = gaussian_filter(I, k * sigma)

    # Rescale phi and epsilon with respect to p.
    phi0 = phi * (p + 1)
    epsilon0 = epsilon / (p + 1)
    tau = p / (p + 1)

    # Compute the difference of gaussians and apply the filter
    D = g1 - tau * gk
    filtered = np.where(D >= epsilon0, 1 + np.tanh(phi0 * (D)), 1)

    # Eventually quantify the tones of the output.
    if n_tones is not None:
        filtered = segmentation(filtered, n_tones, mmin=1, mmax=2)
    out = 255 * normalise(filtered)
    return out


def motion(I, sigma_v=25, sigma=.7, p=65, epsilon=45, phi=.015, vertical=False):
    """
        Use the XDoG algorithm to create a speed-lines effect on an image, namely
        the effect used in comics/manga to create the illusion of a fast motion.
    """
    if I.ndim == 3:
        I = .2989 * I[:, :, 0] + .5870 * I[:, :, 1] + .1140 * I[:, :, 2]
    blurred = normalise(motion_blur(I, sigma_v, vertical=vertical))
    return xdog(blurred, sigma, p, epsilon, phi)


def sharpen(I, sigma_blur=.1, sigma=2, p=25, epsilon=0, phi=.002):
    """
    sharpen effect by highlighting edges.
    """
    mask = xdog(I, sigma, p, phi=np.inf)
    N, M = mask.shape
    sharpened = np.zeros_like(I).astype(np.float64)
    blurred = np.zeros_like(I).astype(np.float64)
    for i in range(3):
        blurred[:,:,i] = gaussian_filter(I[:,:,i], sigma_blur)
    blurred = normalise(blurred)
    for k in range(3):
        sharpened[:,:,k] = np.where(mask == 0, 0, blurred[:,:,k])
    output = np.where(sharpened >= epsilon, 1+np.tanh(phi*(sharpened+1e-10)), 1)
    output = normalise(output)
    return output
