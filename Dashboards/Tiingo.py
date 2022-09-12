
import quandl as qd
from datetime import datetime as dt
import matplotlib.pyplot as plt


qd.ApiConfig.api_key = 'VUsfvNfybt3vg2KnMTvu'

USA = qd.get('SGE/CHNIR', start_date='2000-01-01')

plt.figure()

plt.plot(USA)

plt.show()

USA 