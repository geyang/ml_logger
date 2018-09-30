"""
In this file we test the tensorflow specific logging methods.
"""
import pytest
from ml_logger import logger
from tests.test_ml_logger import setup, log_dir
from tests.conftest import LOCAL_TEST_DIR


def reset_graph():
    import tensorflow as tf
    sess = tf.get_default_session()
    if sess and hasattr(sess, 'close'):
        sess.close()
    if sess and hasattr(sess, '__exit__'):
        sess.__exit__(None, None, None)
    tf.reset_default_graph()


def test_save_checkpoint_and_load(setup):
    import tensorflow as tf

    x = tf.get_variable('x', shape=[], initializer=tf.constant_initializer(0.0))
    y = tf.get_variable('y', shape=[], initializer=tf.constant_initializer(10.0))
    c = tf.Variable(1000)

    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())

    trainables = tf.trainable_variables()
    logger.save_variables(trainables)
    reset_graph()

    x = tf.get_variable('x', shape=[], initializer=tf.constant_initializer(0.0))
    y = tf.get_variable('y', shape=[], initializer=tf.constant_initializer(10.0))
    c = tf.Variable(1000)

    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())

    logger.load_variables("checkpoints/variables.pkl")
    assert x.eval() == 0, 'should be the same as the initial value'
    assert y.eval() == 10, 'should be the same as the initial value'
    assert c.eval() == 1000, 'variable declared without get_variable should work too.'
    reset_graph()


if __name__ == "__main__":
    setup(LOCAL_TEST_DIR)
    test_save_checkpoint_and_load(setup)
