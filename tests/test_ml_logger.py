from ml_logger import logger, Color, percent
from shutil import rmtree

# clean up previous tasks
TEST_LOG_DIR = '/tmp/ml_logger/test'
try:
    rmtree(TEST_LOG_DIR)
except FileNotFoundError as e:
    print(e)

logger.configure(TEST_LOG_DIR, prefix='main')

print("logging to {}".format(TEST_LOG_DIR))


def test_load_pkl():
    import numpy
    d1 = numpy.random.randn(20, 10)
    logger.log_data(d1, 'test_file.pkl')
    d2 = numpy.random.randn(20, 10)
    logger.log_data(d2, 'test_file.pkl')

    data = logger.load_pkl('test_file.pkl')
    assert len(data) == 2, "data should contain two arrays"
    assert numpy.array_equal(data[0], d1), "first should be the same as d1"
    assert numpy.array_equal(data[1], d2), "first should be the same as d2"


def test():
    d = Color(3.1415926, 'red')
    s = "{:.1}".format(d)
    print(s)

    logger.log_params(G=dict(some_config="hey"))
    logger.log(step=0, some=Color(0.1, 'yellow'))
    logger.log(step=1, some=Color(0.28571, 'yellow', lambda v: "{:.5f}%".format(v * 100)))
    logger.log(step=2, some=Color(0.85, 'yellow', percent))
    logger.log({"some_var/smooth": 10}, some=Color(0.85, 'yellow', percent), step=3)
    logger.log(step=4, some=Color(10, 'yellow'))


def test_image():
    import scipy.misc
    import numpy as np

    image_bw = np.zeros((64, 64, 1), dtype=np.uint8)
    image_bw_2 = scipy.misc.face(gray=True)[::4, ::4]
    image_rgb = np.zeros((64, 64, 3), dtype=np.uint8)
    image_rgba = scipy.misc.face()[::4, ::4, :]
    logger.log_image(image_bw, "black_white.png")
    logger.log_image(image_bw_2, "bw_face.png")
    logger.log_image(image_rgb, 'rgb.png')
    logger.log_image(image_rgba, f'rgba_face_{100}.png')
    logger.log_image(image_bw, f"bw_{100}.png")
    logger.log_image(image_rgba, f"rbga_{100}.png")

    # todo: animation is NOT implemented.
    # now print a stack
    # for i in range(10):
    #     logger.log_image(i, animation=[image_rgba] * 5)


def test_pyplot():
    import os, scipy.misc
    import matplotlib
    matplotlib.use('TKAgg')
    import matplotlib.pyplot as plt
    import numpy as np

    face = scipy.misc.face()
    logger.log_image(face, "face.png")

    fig = plt.figure(figsize=(4, 2))
    xs = np.linspace(0, 5, 1000)
    plt.plot(xs, np.cos(xs))
    logger.savefig("face_02.png", fig=fig)
    plt.close()

    fig = plt.figure(figsize=(4, 2))
    xs = np.linspace(0, 5, 1000)
    plt.plot(xs, np.cos(xs))
    logger.savefig('sine.pdf')


def test_video():
    import numpy as np

    def im(x, y):
        canvas = np.zeros((200, 200))
        for i in range(200):
            for j in range(200):
                if x - 5 < i < x + 5 and y - 5 < j < y + 5:
                    canvas[i, j] = 1
        return canvas

    frames = [im(100 + i, 80) for i in range(20)]

    logger.log_video(frames, "test_video.mp4")


class FakeTensor:
    def cpu(self):
        return self

    def detach(self):
        return self

    def numpy(self):
        import numpy as np
        return np.ones([100, 2])


class FakeModule:
    @staticmethod
    def state_dict():
        return dict(var_1=FakeTensor())


def test_module():
    logger.log_module(step=0, Test=FakeModule)


def test_load_module():
    result, = logger.load_pkl(f"modules/{0:04d}_Test.pkl")
    import numpy as np
    assert (result['var_1'] == np.ones([100, 2])).all(), "should be the same as test data"


def test_load_params():
    pass


def test_diff():
    logger.diff()


def test_git_rev():
    print([logger.__head__])


def test_current_branch():
    print([logger.__current_branch__])


def test_split():
    assert logger.split() is None, 'The first tick should be None'
    assert type(logger.split().microseconds) is int, 'Then it should return a a floating for the seconds'


if __name__ == "__main__":
    test_split()
    test_git_rev()
    test_current_branch()
    test_load_pkl()
    test_diff()
    test()
    test_load_params()
    test_pyplot()
    test_module()
    test_load_module()
    test_image()
    test_video()
    # todo: logger.log_module(6, rgba_face=image_rgba)
    # todo: logger.log_params(6, rgba_face=image_rgba)
    # todo: logger.log_file(6, rgba_face=image_rgba)
