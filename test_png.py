import io
import cv2
import glob
import time
import numpy
from PIL import Image
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plotlib


time_stats = []
comp_stats = []
files = glob.glob('test/**/*.png')


@profile
def full_cv2(f):
    s = time.perf_counter()
    im = cv2.imread(f, flags=cv2.IMREAD_UNCHANGED)
    im = cv2.resize(im, [256, 256], interpolation=cv2.INTER_NEAREST)
    byarr = cv2.imencode('.png', im)[1]
    comp_stats.append(len(byarr))
    time_stats.append(time.perf_counter() - s)
    return byarr.tobytes()


@profile
def full_pil(f):
    s = time.perf_counter()
    im = Image.open(f)
    im = im.resize((256, 256), Image.Resampling.LANCZOS)
    bs = io.BytesIO()
    im.save(bs, 'png', compress_level=1)
    comp_stats.append(len(bs.getvalue()))
    time_stats.append(time.perf_counter() - s)
    return bs.getvalue()


@profile
def full_mpl(f):
    s = time.perf_counter()
    im = plotlib.imread(f)
    im = numpy.clip(cv2.resize(im, [256, 256], interpolation=cv2.INTER_LANCZOS4), 0, 1)
    bs = io.BytesIO()
    plotlib.imsave(bs, im, format='png')
    comp_stats.append(len(bs.getvalue()))
    time_stats.append(time.perf_counter() - s)
    return bs.getvalue()


for method in [full_cv2, full_pil]:
    with ThreadPool(8) as pool:
        pool.map(method, files)
    time_stats.clear()
    comp_stats.clear()
    with ThreadPool(1) as pool:
        xs = pool.map(method, files)
    with open('test/' + method.__name__ + '.png', "wb") as fo:
        fo.write(xs[0])
    millis = numpy.array(time_stats) * 1000
    print(
        method.__name__,
        "Time: %.2f ± %.2f ms" % (numpy.mean(millis), numpy.std(millis)),
        "Size: %.1f KB" % (numpy.mean(comp_stats) / 1024),
    )
