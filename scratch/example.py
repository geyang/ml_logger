from params_proto import ParamsProto, Proto, Flag


class Args(ParamsProto):
    """ CLI Args for the program
    Try:
        python3 example.py --help
    And it should print out the help strings
    """
    seed = Proto(1, help="random seed")
    D_lr = 5e-4
    G_lr = 1e-4
    Q_lr = 1e-4
    T_lr = 1e-4
    plot_interval = 10
    verbose = Flag("the verbose flag")


if __name__ == '__main__':
    import scipy
    import numpy as np
    from ml_logger import logger, LOGGER_USER

    # Put in your ~/.bashrc
    # export ML_LOGGER_ROOT = "http://<your-logging-server>:8081"
    # export ML_LOGGER_USER = $USER
    logger.configure(prefix=f"{LOGGER_USER}/scratch/your-experiment-prefix!")

    logger.log_params(Args=vars(Args))
    logger.upload_file(__file__)

    for epoch in range(10):
        logger.log(step=epoch, D_loss=0.2, G_loss=0.1, mutual_information=0.01)
        logger.log_key_value(epoch, 'some string key', 0.0012)
        # when the step index updates, logger flushes all of the key-value pairs to file system/logging server

    logger.flush()

    # Images
    face = scipy.misc.face()
    face_bw = scipy.misc.face(gray=True)
    logger.save_image(face, "figures/face_rgb.png")
    logger.save_image(face_bw, "figures/face_bw.png")
    image_bw = np.zeros((64, 64, 1))
    image_bw_2 = scipy.misc.face(gray=True)[::4, ::4]

    logger.save_video([face] * 5, "videos/face.mp4")
