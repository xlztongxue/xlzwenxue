class BaseConfig:
    SECRET_KEY = '3Zcc7PyJasMyO081QA3z9qFlnxzWqSkB'

    REDIS_SETTINGS = {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB':0,
    }

    QINIU_SETTINGS = {
        'access_key': '51DGWfSzbBws6szT3GVoZ8nMuqVVFAFV2P_StMbr',
        'secret_key': 'pAo3kBotA7PQLCuIF9Y2wCc7AfRs0MEss2-qdTbb',
        'bucket_name': 'toutiao-gz1501',
        'host': 'q0sskvqbp.bkt.clouddn.com',
    }

    JWT_SECRET = 'LAAKohInOAlDl89s1C89dS24v3MDTYu2'
    JWT_EXPIRY_HOURS = 24


class AppletConfig(BaseConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/hmwx'
    DEBUG = True


