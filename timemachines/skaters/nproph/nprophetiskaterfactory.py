import pandas as pd
import sys
import logging
from typing import List, Tuple, Any
from timemachines.skatertools.utilities.conventions import wrap
from timemachines.skatertools.utilities.epochtime import infer_freq_from_epoch, is_valid_freq, epoch_to_naive_datetime, EPOCH
from timemachines.skatertools.utilities.suppression import no_stdout_stderr
from timemachines.skaters.nproph.nprophparams import NPROPHET_MODEL, NPROPHET_META
from timemachines.skatertools.utilities.wrangling import transpose
from neuralprophet import NeuralProphet


def nprophet_iskater_factory(y: [[float]], k: int, a: List = None, t: List = None, e=None, freq: str = None, n_max=1000,
                            recursive: bool = False, model_params: dict = None, return_forecast=True):
    # For now we keep it simple. Will add to this over time
    x, x_std, forecast,m = nprophet_fit_and_predict_simple(y=y,k=k,freq=freq,model_params=model_params)
    return (x, x_std, forecast, m) if return_forecast else (x, x_std)



def nprophet_fit_and_predict_simple(y: [float], k: int, freq: str = None, model_params: dict = None) -> Tuple[
    List, List, Any, Any]:
    """ Simpler wrapper for testing - univariate only """
    assert isinstance(y[0],float)
    freq = freq or NPROPHET_META['freq']
    used_params = NPROPHET_MODEL
    if model_params:
        used_params.update(model_params)

    if len(y)<used_params['n_lags']:
        x = [wrap(y)[0]]*k
        x_std = [1.0]*k
        return x, x_std, None, None
    else:
        model = NeuralProphet(**used_params)
        df = pd.DataFrame(columns=['y'], data=y)
        df['ds'] = pd.date_range(start='2021-01-01', periods=len(y), freq=freq)
        metrics = model.fit(df, freq='5min')
        future = model.make_future_dataframe(df, periods=k)
        forecast = model.predict(future)
        x = forecast['yhat1'].values[-k:]
        x_std = [1.0]*k
        return x, x_std, forecast, model


if __name__=='__main__':
    from timemachines.skatertools.data.real import hospital
    from timemachines.skatertools.utilities.nonemath import nearlysame

    k = 3
    n = 500
    y = hospital(n=n)[-200:]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_simple(y=y, k=k)
    if True:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()