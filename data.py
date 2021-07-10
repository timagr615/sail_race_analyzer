import pandas as pd
import math

data = pd.read_csv('data/DATALOG2.CSV', delimiter=",",
                   names=['date', 'time', 'lat', 'lon', 'vgps', 'velocity', 'course', 'heading', 'pitch', 'roll'])
# data['vhead'] = data['velocity']*math.cos(math.pi/180*(data['course']-data['heading']))
data['drift'] = data.apply(lambda row: math.fabs(row['velocity'] *
                                                 math.sin(math.pi / 180 * math.fabs(row['course'] - row['heading']))),
                           axis=1)
data['vhead'] = data.apply(lambda row: math.fabs(row['velocity'] *
                                                 math.cos(math.pi / 180 * (row['course'] - row['heading']))), axis=1)
print(data)
