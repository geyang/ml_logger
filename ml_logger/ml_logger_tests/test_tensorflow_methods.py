"""
In this file we test the tensorflow specific logging methods.
"""
import pytest
from ml_logger import logger
from ml_logger_tests.test_ml_logger import setup, log_dir
from ml_logger_tests.conftest import LOCAL_TEST_DIR


def reset_graph():
    import tensorflow.compat.v1 as tf
    sess = tf.get_default_session()
    if sess and hasattr(sess, 'close'):
        print(">>>>> close the session")
        sess.close()
    if sess and hasattr(sess, '__exit__'):
        print(">>>>> exit the session")
        sess.__exit__(None, None, None)
    tf.reset_default_graph()


def test_save_checkpoint_and_load(setup):
    import tensorflow.compat.v1 as tf

    with tf.Session() as sess:
        # test saving variables in check point
        x = tf.get_variable('x', shape=[], initializer=tf.constant_initializer(0.0))
        y = tf.get_variable('y', shape=[], initializer=tf.constant_initializer(10.0))
        c = tf.Variable(1000)

        sess.run(tf.global_variables_initializer())
        trainables = tf.trainable_variables()
        logger.save_variables(trainables, 'checkpoints/variables.pkl')

    reset_graph()


    with tf.Session() as sess:
        # test loading variables from weight dict
        x = tf.get_variable('x', shape=[], initializer=tf.constant_initializer(0.0))
        y = tf.get_variable('y', shape=[], initializer=tf.constant_initializer(10.0))
        c = tf.Variable(1000)

        sess.run(tf.global_variables_initializer())
        logger.load_variables("checkpoints/variables.pkl")

        assert x.eval(session=sess) == 0, 'should be the same as the initial value'
        assert y.eval(session=sess) == 10, 'should be the same as the initial value'
        assert c.eval(session=sess) == 1000, 'variable declared without get_variable should work too.'

    reset_graph()


    with tf.Session() as sess:
        # test strict mode where we pass in variable list
        x = tf.get_variable('x', shape=[], initializer=tf.constant_initializer(0.0))
        y = tf.get_variable('y', shape=[], initializer=tf.constant_initializer(10.0))
        c = tf.Variable(1000)
        d_does_not_exist = tf.Variable(20)

        sess.run(tf.global_variables_initializer())

        occurred = False
        try:
            logger.load_variables("checkpoints/variables.pkl", variables=[x, y, c, d_does_not_exist])
        except KeyError as e:
            print(e)
            occurred = True
        assert occurred, "should raise KeyError"
    reset_graph()


if __name__ == "__main__":
    setup(LOCAL_TEST_DIR)
    test_save_checkpoint_and_load(setup)
