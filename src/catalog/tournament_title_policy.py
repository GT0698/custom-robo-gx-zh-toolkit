"""Allow only title IDs from the original30-row tournament definition table."""
from pathlib import Path
import hashlib
SOURCE=(Path(__file__).resolve().parents[2]/'work/roms/custom-robo-gx-jp.gba')
def allowed_ids():
 data=SOURCE.read_bytes();assert hashlib.sha1(data).hexdigest()=='0b5ce051aa1fd83ab0ec79122b07b02bb41096a5'
 start=0x4fed9a;ids=[]
 for i in range(30):
  row=start+i*108;assert int.from_bytes(data[row:row+3],'little')==i
  ids.append(int.from_bytes(data[row+3:row+6],'little'))
 assert len(set(ids))==30
 return set(ids)
