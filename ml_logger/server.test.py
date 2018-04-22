from time import sleep

from ml_logger.log_client import LogClient
from tqdm import trange

TEST_URL = "http://localhost:8081"

if __name__ == '__main__':

    logger = LogClient(TEST_URL, prefix="experiment/some-test")

    for i in trange(10):
        import scipy.misc

        logger.log('experiment1/some-test/data.pkl', dict(some=100, this=[3, 21]))
        logger.send_image(f'experiment1/some-test/figures/{i:04d}', scipy.misc.face())
        logger.log_text(f'experiment1/some-test/some.md', "# some header\n")
        # note('experiment1/some-test', dict(some=100, this=[3, 21]))
        sleep(0.001)

    # app.run_server(debug=True)
