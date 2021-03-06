import logging
import os

from sqlalchemy.exc import OperationalError
import gevent
from redis import Redis


import api_gateway.cache
import api_gateway.config
import api_gateway.executiondb
import api_gateway.scheduler
from api_gateway.config import Config
from api_gateway.appgateway.appcache import AppCache
from api_gateway.senders_receivers import WorkflowResultsReceiver, WorkflowResultsSender


logger = logging.getLogger(__name__)


class Context(object):

    def __init__(self, init_all=True, app=None):
        """Initializes a new Context object. This acts as an interface for objects to access other event specific
            variables that might be needed.
        """
        try:
            self.execution_db = api_gateway.executiondb.ExecutionDatabase(api_gateway.config.Config.EXECUTION_DB_TYPE,
                                                                      api_gateway.config.Config.EXECUTION_DB_PATH,
                                                                      api_gateway.config.Config.EXECUTION_DB_HOST)
        except OperationalError as e:
            if "password" in str(e):
                logger.error("Incorrect username and/or password for execution database. Please make sure these are "
                             "both set correctly in their respective environment variables and try again."
                             "Error Message: {}".format(str(e)))
            else:
                logger.error("Error connecting to execution database. Please make sure all database settings are "
                             "correct and try again. Error Message: {}".format(str(e)))
            os._exit(1)

        if init_all:
            self.cache = api_gateway.cache.make_cache(api_gateway.config.Config.CACHE)
            self.app_cache = AppCache.initialize(redis=Redis(host=Config.CACHE["host"], port=Config.CACHE["port"]))
            self.scheduler = api_gateway.scheduler.Scheduler()
            self.results_sender = WorkflowResultsSender(execution_db=self.execution_db)
            self.receiver = WorkflowResultsReceiver(current_app=app)
            gevent.spawn(self.receiver.receive_results)

    def inject_app(self, app):
        self.scheduler.app = app
