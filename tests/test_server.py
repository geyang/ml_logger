from random import random, randint
from time import sleep
from ml_logger.log_client import LogClient
from tqdm import trange

# TEST_URL = "http://localhost:8081"
with open('../../_cluster-infra/torch-gym-prebuilt/ip_address.txt', 'r') as f:
    ip = f.read()
    TEST_URL = "http://{}:8081".format(ip.strip())
    print(TEST_URL)

prefix = randint(0, 100)
if __name__ == '__main__':

    logger = LogClient(TEST_URL, prefix="experiment/some-test")

    for i in trange(10):
        import scipy.misc

        logger.log('experiment1/some-test-{}-{}/data.pkl'.format(prefix, i), dict(some=100, this=[3, 21]))
        sleep(0.001)
        logger.send_image('experiment1/some-test-{}-{}/figures/{:04d}'.format(prefix, i, i), scipy.misc.face())
        sleep(0.001)
        logger.log_text('experiment1/some-test-{}-{}/some.md'.format(prefix, i), "# some header\n")
        # note('experiment1/some-test', dict(some=100, this=[3, 21]))
        sleep(0.001)

    # app.run_server(debug=True)
