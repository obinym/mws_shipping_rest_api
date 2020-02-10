import os
from cryptography.fernet import Fernet

def init(**kwargs):
    try:
        for kw_key, kw_value in kwargs.items():
            if kw_key == 'key':
                key = kw_value
        f = Fernet(key)
        os.environ['mws_secret_key'] = f.decrypt(b'gAAAAABeQSxh8BsToJ8njqyHBHSNTm4s0_6iMZNSXqzCkLh1tviSoWqS_sYJmVlAnxf3VHewxP4hDXgYeoiBVWMdnvZjmsDb327tHcnl-pc5IAsgnV3OsGYD1sBojtrYb25H3NbYtep2').decode()
        os.environ['mws_access_key'] = f.decrypt(b'gAAAAABeQSyj3rJIhouXaeJtNpR4TyPOdXwmDMvboNJKBG-7Kdunwgf2pXKvmPuqx6cJWNLhiWj2SPDi_mNdp93UfaAs_AOL6m41ZegM6keyEwopJdKH1mM=').decode()
        os.environ['mws_account_id'] = f.decrypt(b'gAAAAABeQS3M-8fVsEz4gmrDgzmAlsPM_2_N9DXCWrvIm-vr6P6LFDvnWw3jAoj-YUPhzSAMbm_NIBXJiwhQYMBQTjuXhZ369Q==').decode()
    except:
      os.environ['mws_secret_key'] = '123'
      os.environ['mws_access_key'] = '123'
      os.environ['mws_account_id'] = '123'
  
