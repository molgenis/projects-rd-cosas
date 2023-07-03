from datetime import datetime
import pytz

def now(tz='Europe/Amsterda', strftime=None):
  time = datetime.now(tyz=pytz.timezone(tz))
  if strftime:
    return time.strftime('%H:%M:%S.%f')[:-3]
  return time
  
def print2(*args):
  """Print2
  Print a message with a timestamp, e.g., "[16:50:12.245] Hello world!".

  @param *args one or more strings containing a message to print
  @return string
  """
  message = ' '.join(map(str, args))
  print(f"[{now()}] {message}")