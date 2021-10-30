import argparse
import asyncio
import logging
import sys
import os

from types import SimpleNamespace
from catprinter.cmds import PRINT_WIDTH, cmds_print_img
from catprinter.ble import run_ble
from catprinter.img import read_img


def parse_args():
    args = argparse.ArgumentParser(
        description='prints an image on your cat thermal printer')
    args.add_argument('url', type=str)
    args.add_argument('--log-level', type=str,
                      choices=['debug', 'info', 'warn', 'error'], default='info')
    args.add_argument('--img-binarization-algo', type=str,
                      choices=['mean-threshold', 'floyd-steinberg'], default='floyd-steinberg',
                      help='Which image binarization algorithm to use.')
    args.add_argument('--show-preview', action='store_true',
                      help='If set, displays the final image and asks the user for confirmation before printing.')
    args.add_argument('--devicename', type=str, default='GT01',
                      help='Specify the Bluetooth device name to search for. Default value is GT01.')
    return args.parse_args()


def make_logger(log_level):
    logger = logging.getLogger('catprinter')
    logger.setLevel(log_level)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(log_level)
    logger.addHandler(h)
    return logger

# URL can be a local file of the form file://<path-to-file>
async def print_from_url(url, log_level='info', img_binarization_algo='floyd-steinberg', devicename='GT01', show_preview=False):
    await amain(SimpleNamespace(**{
        'url' : url,
        'log_level' : log_level,
        'img_binarization_algo' : img_binarization_algo,
        'show_preview' : show_preview,
        'devicename' : devicename
    }))
async def amain(kwargs):
    log_level = getattr(logging, kwargs.log_level.upper())
    logger = make_logger(log_level)

    url = kwargs.url
    bin_img = read_img(url, PRINT_WIDTH,
                       logger, kwargs.img_binarization_algo, kwargs.show_preview)
    if bin_img is None:
        logger.info(f'🛑 No image generated. Exiting.')
        return False

    logger.info(f'✅ Read image: {bin_img.shape} (h, w) pixels')
    data = cmds_print_img(bin_img)
    logger.info(f'✅ Generated BLE commands: {len(data)} bytes')

    await run_ble(data, kwargs.devicename, logger)
    return True

def main(kwargs):
    print(kwargs)
    log_level = getattr(logging, kwargs.log_level.upper())
    logger = make_logger(log_level)

    url = kwargs.url
    bin_img = read_img(url, PRINT_WIDTH,
                       logger, kwargs.img_binarization_algo, kwargs.show_preview)
    if bin_img is None:
        logger.info(f'🛑 No image generated. Exiting.')
        return False

    logger.info(f'✅ Read image: {bin_img.shape} (h, w) pixels')
    data = cmds_print_img(bin_img)
    logger.info(f'✅ Generated BLE commands: {len(data)} bytes')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_ble(data, kwargs.devicename, logger))
    return True

if __name__ == '__main__':
    kwargs = parse_args()
    main(kwargs)
