import cv2
import urllib.request
import numpy as np

opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

def floyd_steinberg_dither(img):
    '''Applies the Floyd-Steinberf dithering to img, in place.
    img is expected to be a 8-bit grayscale image.

    Algorithm borrowed from wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering.
    '''
    h, w = img.shape[:2]

    def adjust_pixel(y, x, delta):
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        img[y][x] = min(255, max(0, img[y][x] + delta))

    for y in range(h):
        for x in range(w):
            new_val = 255 if img[y][x] > 127 else 0
            err = img[y][x] - new_val
            img[y][x] = new_val
            adjust_pixel(y, x + 1, err * 7/16)
            adjust_pixel(y + 1, x - 1, err * 3/16)
            adjust_pixel(y + 1, x, err * 5/16)
            adjust_pixel(y + 1, x + 1, err * 1/16)


def read_img(
        url,
        print_width,
        logger,
        img_binarization_algo,
        show_preview):
    print(f'sent url: {url}')
    if not (url.startswith('http://') or url.startswith('https://') or url.startswith('file://')):
        # Assume a local file
        url = 'file://' + url
    print(f'new url: {url}')
    req = urllib.request.urlopen(url)
    if req.getcode() != 200:
        print(f'Received non-200 code {req.getcode()} retrieving {url}')
        return None
    arr = np.asarray(bytearray(req.read()))
    im = cv2.imdecode(arr, -1)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    height = gray.shape[0]
    width = gray.shape[1]
    factor = print_width / width
    resized = cv2.resize(gray, (int(width * factor), int(height *
                         factor)), interpolation=cv2.INTER_AREA)

    if img_binarization_algo == 'floyd-steinberg':
        logger.info(f'⏳ Applying Floyd-Steinberg dithering to image...')
        floyd_steinberg_dither(resized)
        logger.info(f'✅ Done.')
        resized = resized > 127
    elif img_binarization_algo == 'mean-threshold':
        resized = resized > resized.mean()
    else:
        logger.error(
            f'🛑 Unknown image binarization algorithm: {img_binarization_algo}')
        raise RuntimeError(
            f'unknown image binarization algorithm: {img_binarization_algo}')

    if show_preview:
        # Convert from our boolean representation to float.
        preview_img = resized.astype(float)
        cv2.imshow('Preview', preview_img)
        logger.info('ℹ️  Displaying preview.')
        # Calling waitKey(1) tells OpenCV to process its GUI events and actually display our image.
        cv2.waitKey(1)
        if input(f'🤔 Go ahead with print? [Y/n]? ').lower() == 'n':
            logger.info('🛑 Aborted print.')
            return None

    # Invert the image before returning it.
    return ~resized
