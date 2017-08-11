import samba
import ldb
from samba.dcerpc import samr, security, lsa
from samba import credentials
from samba import param
from samba.auth import system_session
from samba.samdb import SamDB

lp = param.LoadParm()
lp.load_default()


def _connect(username, password, hostname='localhost'):
      try:
         creds = credentials.Credentials()
         creds.set_username(username)
         creds.set_password(password)
         creds.set_domain("")
         creds.set_workstation("")
         conn = samba.Ldb("ldap://"+ hostname,lp=lp,credentials=creds)
      except Exception, e:
            return False;
      return True;
