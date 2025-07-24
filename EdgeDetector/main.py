import cv2
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from PIL import Image
from xdog import xdog, motion, sharpen
from fdog import fdog

def teaser(I):
    list_data = ["I",
                 "motion(I, sigma_v=4, sigma=.5)",
                 "sharpen(I, sigma_blur=.1, sigma=.9, p=25, epsilon=0, phi=.001)",
                 "xdog(I, .9, p=20, epsilon=20, phi=.01, base='gray', n_tones=None)",
                 "xdog(I, .9, p=20, epsilon=20, phi=.01, base='gray', n_tones=3)",
                 "xdog(I, .9, p=20, epsilon=20, phi=.01, base='gray', n_tones=15)",
                 #"xdog(I, .9, p=20, epsilon=20, phi=.01, base='RGB', n_tones=None)",
                 #"xdog(I, .9, p=20, epsilon=20, phi=.01, base='RGB', n_tones=3)",
                 #"xdog(I, .9, p=20, epsilon=20, phi=.01, base='RGB', n_tones=15)",
                 "fdog(I, .2, 1.5, 1.3, 1, p=25, epsilon=40, phi=.01, n_tones=None, base='gray')",
                 "fdog(I, .2, 1.5, 1.3, 1, p=25, epsilon=40, phi=.01, n_tones=3, base='gray')",
                 "fdog(I, .2, 1.5, 1.3, 1, p=25, epsilon=40, phi=.01, n_tones=15, base='gray')",
                 #"fdog(I, .2, 1.5, 1.3, 1, p=25, epsilon=40, phi=.01, n_tones=None, base='RGB')",
                 #"fdog(I, .2, 1.5, 1.3, 1, p=25, epsilon=40, phi=.01, n_tones=3, base='RGB')",
                 #"fdog(I, .2, 1.5, 1.3, 1, p=25, epsilon=40, phi=.01, n_tones=15, base='RGB')",
                 ]
    list_titles = ['input', 'motion', 'sharpen',
                   'XDoG (grayscale)', 'XDoG (grayscale, 3 tones)', 'XDoG (grayscale, 15 tones)',
                   #'XDoG (RGB)', 'XDoG (RGB, 3 tones)', 'XDoG (RGB, 15 tones)',
                   'FDoG (grayscale)', 'FDoG (grayscale, 3 tones)', 'FDoG (grayscale, 15 tones)',
                   #'FDoG (RGB)', 'FDoG (RGB, 3 tones)', 'FDoG (RGB, 15 tones)',
                   ]
    plt.axis('off')
    for i in tqdm(range(1, 10)):
        plt.subplot(3, 3, i)
        #try:
        if True:
            plt.imshow(eval(list_data[i-1]), cmap='gray')
            plt.title(list_titles[i-1])
        #except IndexError:
        #    break
    plt.suptitle('Image Effects')
    plt.show()


if __name__ == '__main__':

    def resize_img(img, max_size=200):
        I = np.array(img).astype(np.float64)
        N, M = I.shape[:2]
        r = max(N,M) / max_size
        out = np.array(img.resize((int(M/r), int(N/r)), Image.Resampling.LANCZOS)).astype(np.uint8)
        return out

    big_pirate = cv2.imread(r'../image/chenps.jpg')
    pirate = resize_img(Image.open(r'../image/chenps.jpg'))
    teaser(pirate)
