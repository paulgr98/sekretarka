import os
import config.config as cfg
os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '1'
os.environ['OPENAI_API_KEY'] = cfg.OPENAI_API_KEY
