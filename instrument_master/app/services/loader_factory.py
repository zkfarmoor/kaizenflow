"""
Import as: import instrument_master.app.services.loader_factory as iasloa.
"""
from typing import Any

import instrument_master.common.data.load.data_loader as icdlda
import instrument_master.common.data.load.s3_data_loader as icdls3
import instrument_master.common.data.load.sql_data_loader as icdlsq
import instrument_master.ib.data.load.ib_s3_data_loader as iidlib3
import instrument_master.ib.data.load.ib_sql_data_loader as iidlib
import instrument_master.kibot.data.load.kibot_s3_data_loader as ikdlki3
import instrument_master.kibot.data.load.kibot_sql_data_loader as ikdlki

# TODO: Move it out to app/


class LoaderFactory:
    """
    Builds AbstractDataLoader objects based on different criteria (e.g.,
    provider and storage type).
    """

    @classmethod
    def get_loader(
        cls, storage_type: str, provider: str, **kwargs: Any
    ) -> icdlda.AbstractDataLoader:
        """
        Return a data loader for the requested `storage_type` and `provider`.

        :param storage_type: load from where (e.g., s3, sql)
        :param provider: provider (e.g., kibot, ib)
        :param kwargs: additional parameters for loader instantiation
        :raises ValueError: `storage_type` loader is not implemented for provider
        """
        if storage_type == "sql":
            loader = cls._get_sql_loader(provider, **kwargs)
        elif storage_type == "s3":
            loader = cls._get_s3_loader(provider)
        else:
            raise ValueError("Storage type %s is not supported" % storage_type)
        return loader

    @staticmethod
    def _get_s3_loader(provider: str) -> icdls3.AbstractS3DataLoader:
        """
        Return a data loader from S3 for the requested `provider`.

        :param provider: provider (e.g., kibot)
        :raises ValueError: if loader is not implemented for provider
        """
        loader: icdls3.AbstractS3DataLoader
        if provider == "kibot":
            loader = ikdlki3.KibotS3DataLoader()
        elif provider == "ib":
            loader = iidlib3.IbS3DataLoader()
        else:
            raise ValueError("S3 loader for %s is not implemented" % provider)
        return loader

    @staticmethod
    def _get_sql_loader(
        provider: str, dbname: str, user: str, password: str, host: str, port: int
    ) -> icdlsq.AbstractSqlDataLoader:
        """
        Return a data loader from SQL for the requested `provider`.

        :param provider: provider (e.g., kibot)
        :param dbname: database name to connect
        :param user: authorization user
        :param password: authorization password
        :param host: database host
        :param port: database port
        :raises ValueError: if SQL loader is not implemented for provider
        """
        loader: icdlsq.AbstractSqlDataLoader
        if provider == "kibot":
            loader = ikdlki.KibotSqlDataLoader(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
        elif provider == "ib":
            loader = iidlib.IbSqlDataLoader(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
        else:
            raise ValueError("SQL loader for %s is not implemented" % provider)
        return loader