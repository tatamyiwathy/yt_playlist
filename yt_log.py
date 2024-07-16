from logging import DEBUG, StreamHandler, Formatter, FileHandler

def init_log(logger, name="yt_playlist"):
    handler = {
        "stream": StreamHandler(),
        "file": FileHandler("%s.log" % name, "a")
    }

    handler["stream"].setFormatter(Formatter('%(message)s'))
    handler["file"].setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler["stream"])
    logger.addHandler(handler["file"])

    return logger
