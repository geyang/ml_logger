from contextlib import ExitStack, contextmanager
from fnmatch import fnmatch
from glob import glob

from params_proto import ParamsProto, Proto, Flag


class UploadArgs(ParamsProto):
    """ ML-Logger upload command

    Example:
        ml-upload --list  # to see all files in the current directory for upload
        ml-upload --target /fast_nerf/fast_nerf/panda_exp/2022  # uploads to this folder
        ml-upload --target /$USER/sratch/tmp --overwrite  # overwrite existing files
        ml-upload --target /$USER/scratch/tmp --archive  # upload the files as a tar file
    """
    list = Flag("List all of the folders if set.")

    target: str = Proto(help="The target prefix on the logging server")  # , required=True)
    workdir = Proto(".", help="cache directory")
    source = Proto("*", help="""Query pattern for the files to be tarred.""")
    archival = Flag("Use archive to upload the files")
    exclude = Proto(".git*", help="Exclude files matching this pattern when uploading")

    overwrite = Flag("overwrite existing folders in the cache directory")


@contextmanager
def WorkDir(path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """
    import os

    origin = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


# def list(source, query):


def upload(source, target, overwrite=False):
    """download dataset from source to the target folder (local)

    Args:
        source (str): source folder. Example: "/fast_nerf/fast_nerf/panda_exp/2022"
        target (str): target folder. Example: "$DATASETS/panda_exp/2022"
        overwrite (bool, optional): overwrite the target folder. Defaults to False.
            Other-wise it will skip the download if the target folder exists.
    """
    from ml_logger import logger

    raise NotImplementedError("This is a snippet. You need to implement this function.")


def entrypoint():
    from ml_logger import logger

    """list the current directory into a tree"""

    with WorkDir(UploadArgs.workdir):
        folders = glob(UploadArgs.source, recursive=True)

    exclude_patterns = UploadArgs.exclude.split(';')
    if exclude_patterns:
        # show me the code for match the child string against a list of exclude patterns, step by step
        folders = [f for f in folders if not any([fnmatch(f, e) for e in exclude_patterns])]

    if UploadArgs.list:
        print(UploadArgs.workdir + ":", *folders, sep="\n")
        return

    if UploadArgs.target is None:
        logger.print("setting the upload target to ", logger.prefix)
        PCntx = ExitStack()
    else:
        PCntx = logger.Prefix(UploadArgs.target)

    with logger.Sync(), PCntx, WorkDir(UploadArgs.workdir):  # use synchronous mode to make sure the upload finished
        from tqdm import tqdm

        pbar = tqdm(folders)
        for local_name in pbar:
            desc = f"Uploading the {local_name} to {logger.get_dash_url()}/{local_name}"
            pbar.write(desc)

            import os
            if os.path.isfile(local_name):
                logger.upload_file(local_name, local_name)
                continue

            tar_filename = local_name + ".tar"

            if tar_filename in (logger.glob(tar_filename) or []):
                if UploadArgs.overwrite:
                    pbar.write(f"overwriting {tar_filename} on the server")
                    logger.remove(tar_filename)
                else:
                    pbar.write(f"{tar_filename} alread exists on the server"
                               "Set the --overwrite flag to overwrite it.")
                    continue

            logger.upload_dir(local_name, tar_filename, excludes=exclude_patterns, archive="tar")

            if local_name in (logger.glob(local_name) or []):
                if UploadArgs.overwrite:
                    pbar.write(f"overwriting {local_name} on the server")
                    logger.remove(local_name)
                else:
                    pbar.write(f"{local_name} alread exists on the server"
                               "Set the --overwrite flag to overwrite it.")
                    continue

            if not UploadArgs.archival:
                logger.shell(f"mkdir -p {local_name} && tar -xvf {tar_filename} --directory {local_name}")
                logger.remove(tar_filename)
                pbar.write("Decompressed the archive on the server")

        print("Uploading completed")


if __name__ == "__main__":
    # UploadArgs.list = True
    # UploadArgs.overwrite = True
    # UploadArgs.archive = False
    # UploadArgs.target = "/fast_nerf/fast_nerf/panda_exp/2023/ge_upload_example/"
    # UploadArgs.prefix = os.path.expandvars("/fast_nerf/fast_nerf/panda_exp/2022")
    # UploadArgs.output = os.path.expandvars("$DATASETS/panda_exp/2022")
    entrypoint()
