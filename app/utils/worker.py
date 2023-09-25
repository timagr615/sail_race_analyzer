import asyncio
import os
# import time
from celery import Celery, shared_task
import pandas
from pandas import DataFrame
from geopy import distance

from app.core.config import settings


celery = Celery(__name__)
celery.conf.broker_url = settings.celery_broker_url2
celery.conf.result_backend = settings.celery_result_backend


def filter_data(dataframe: str):
    dataframe = pandas.read_json(dataframe)
    if 'time' not in dataframe:
        time = pandas.to_datetime(dataframe["date"], errors='coerce')
        dataframe['time'] = time
        # dataframe.drop('datetime', axis=1, inplace=True)

    time0 = dataframe.time[0]
    coord0 = (dataframe.lat.iloc[0], dataframe.lon.iloc[0])
    c0 = (dataframe.lat.iloc[0], dataframe.lon.iloc[0])
    coordf0 = (dataframe.latf.iloc[0], dataframe.lonf.iloc[0])
    timelast = dataframe.time.iloc[len(dataframe)-1]
    indexes = []
    dista = []
    dataframe.reset_index()
    for i in range(len(dataframe)):
        delta = dataframe.time.iloc[i] - time0
        time0 = dataframe.time.iloc[i]

        coord = (dataframe.lat.iloc[i], dataframe.lon.iloc[i])
        coordf = (dataframe.latf.iloc[i], dataframe.lonf.iloc[i])
        dist = distance.distance(coord, coord0).m
        dista.append(distance.distance(coord, c0).m)
        distf = distance.distance(coordf, coordf0).m
        coord0 = coord
        coordf0 = coordf

        if pandas.isnull(dataframe.time.iloc[i]) or delta > pandas.Timedelta(days=1) or dist > 10 or distf > 10:
            indexes.append(dataframe.iloc[i].name)
    dataframe['dist'] = dista
    dataframe.drop(index=indexes, axis=0, inplace=True)
    return dataframe

def save_data(path: str, dataframe: str) -> int:
    dataframe = filter_data(dataframe)
    res = dataframe.to_csv(path, index=False)
    # print(path, res)
    size = os.path.getsize(path)
    return size

@celery.task(name='process_data')
def process_data(path: str, df: str) -> dict:
    try:
        size = save_data(path, df)
        return {'success': True, 'size': size}
    except Exception as e:
        return {'success': False, 'error': e}
