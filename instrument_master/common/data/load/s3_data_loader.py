import instrument_master.common.data.load.data_loader as vcdlda


# TODO(*): Move it to data_loader.py
class AbstractS3DataLoader(vcdlda.AbstractDataLoader):
    """
    Interface for class reading data from S3.
    """