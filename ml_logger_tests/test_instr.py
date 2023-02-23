def test_instr_prefix():
    import os, glob
    from ml_logger import logger, instr

    train = lambda: print("running experiment")
    instr(train)
    print(logger)

    assert logger.prefix.startswith("geyang/scratch/2023/02-23/test_instr/")