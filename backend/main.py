"""CropCast Model B inference. No substitute predictions, user database or credentials in responses."""
from __future__ import annotations
import hashlib, hmac, logging, os, threading, time
from contextlib import asynccontextmanager
import asyncio
from pathlib import Path
from typing import Literal
from collections import OrderedDict
import joblib, numpy as np, pandas as pd, httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

VERSION='Model B v1.0.1'
MODEL_URL='https://github.com/Kxni5hk/crop-yield-predictor/releases/download/v1.0.1/crop_yield_model_b_for_release.joblib'
DIGEST='2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b'
CROPS=['Wheat','Rice','Maize','Barley','Cotton','Soybean']
FEATURES=['Region','Soil_Type','Crop','Rainfall_mm','Temperature_Celsius','Fertilizer_Used','Irrigation_Used','Weather_Condition']
class Conditions(BaseModel):
    model_config=ConfigDict(extra='forbid')
    Region: Literal['North','South','East','West']
    Soil_Type: Literal['Loam','Clay','Sandy','Silt','Peaty','Chalky']
    Crop: Literal['Wheat','Rice','Maize','Barley','Cotton','Soybean']
    Rainfall_mm: float=Field(ge=100,le=1000,allow_inf_nan=False)
    Temperature_Celsius: float=Field(ge=15,le=40,allow_inf_nan=False)
    Fertilizer_Used: StrictBool
    Irrigation_Used: StrictBool
    Weather_Condition: Literal['Sunny','Cloudy','Rainy']
    @field_validator('Rainfall_mm','Temperature_Celsius',mode='before')
    @classmethod
    def number(cls,v):
        if isinstance(v,bool) or not isinstance(v,(int,float)): raise ValueError('Expected a JSON number')
        return v
class Batch(BaseModel):
    model_config=ConfigDict(extra='forbid')
    rows:list[Conditions]=Field(min_length=1,max_length=50)

_model=None
_lock=threading.Lock()
def load_model():
    global _model
    with _lock:
        if _model is not None:return _model
        import sklearn
        if sklearn.__version__!='1.6.1':raise RuntimeError('scikit-learn 1.6.1 is required')
        path=Path(os.environ.get('MODEL_PATH','/tmp/cropcast-model-b.joblib'))
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            partial=path.with_suffix('.part')
            try:
                with httpx.stream('GET',MODEL_URL,follow_redirects=True,timeout=120) as response:
                    response.raise_for_status()
                    with partial.open('wb') as f:
                        total=0
                        for chunk in response.iter_bytes():
                            total+=len(chunk)
                            if total>200_000_000:raise RuntimeError('Model exceeds trusted artifact size limit')
                            f.write(chunk)
                with partial.open('rb') as downloaded:actual_download=hashlib.file_digest(downloaded,'sha256').hexdigest()
                if actual_download!=DIGEST:raise RuntimeError('Model checksum mismatch')
                partial.replace(path)
            finally:partial.unlink(missing_ok=True)
        with path.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
        if not hmac.compare_digest(actual,DIGEST):raise RuntimeError('Model checksum mismatch')
        _model=joblib.load(path)
        # Constrain CPU parallelism; use one process because the artifact is large.
        if hasattr(_model,'named_steps'):
            for step in _model.named_steps.values():
                if hasattr(step,'n_jobs'):step.n_jobs=1
        return _model

@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(load_model)
    yield

app=FastAPI(lifespan=lifespan,title='CropCast Model B',version='3.0.0',docs_url=None,redoc_url=None)
origins=[x.strip() for x in os.getenv('ALLOWED_ORIGINS','').split(',') if x.strip()]
if origins:app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Inference-Token'],allow_credentials=False)
requests_seen=OrderedDict()
rate_lock=threading.Lock()
def authorize(request:Request):
    expected=os.getenv('INFERENCE_TOKEN','')
    if len(expected)<32:raise HTTPException(503,'Inference access is not configured')
    if not hmac.compare_digest(request.headers.get('X-Inference-Token',''),expected):raise HTTPException(401,'Invalid service credentials')
    # This per-process limit supplements the staging Site’s best-effort edge limit.
    key=request.client.host if request.client else 'unknown'; now=int(time.time()//60)
    with rate_lock:
        count,minute=requests_seen.get(key,(0,now)); count=count+1 if minute==now else 1
        requests_seen[key]=(count,now)
        while len(requests_seen)>1000:requests_seen.popitem(last=False)
    if count>120:raise HTTPException(429,'Too many requests; retry in a minute',headers={'Retry-After':'60'})

@app.middleware('http')
async def limit_body(request:Request,call_next):
    if request.method=='POST':
        try:
            length=int(request.headers.get('content-length','0'))
            if length<0 or length>131072:raise ValueError()
        except ValueError:
            from fastapi.responses import JSONResponse
            return JSONResponse({'detail':'Request exceeds 128 KB'},status_code=413)
        chunks=[]; size=0
        async for chunk in request.stream():
            size+=len(chunk)
            if size>131072:
                from fastapi.responses import JSONResponse
                return JSONResponse({'detail':'Request exceeds 128 KB'},status_code=413)
            chunks.append(chunk)
        request._body=b''.join(chunks)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/health')
def health():return {'status':'ok','model_loaded':_model is not None,'model_version':VERSION}
@app.get('/ready')
def ready():
    if _model is None:raise HTTPException(503,'Model is not loaded')
    return {'status':'ready','model_version':VERSION}
@app.get('/api/model/info')
def info():return {'model_version':VERSION,'algorithm':'Random Forest Regression','features':FEATURES,'sha256':DIGEST,'units':'tonnes/hectare','independently_validated':False}
@app.get('/api/model/metrics')
def metrics():return {'source':'Original README random test split; 10000 test examples','model_a':{'r2':.9039,'rmse':.5211,'mae':.4156},'model_b':{'r2':.9031,'rmse':.5233,'mae':.4175}}
@app.get('/api/options')
def options():return {'Region':['North','South','East','West'],'Soil_Type':['Loam','Clay','Sandy','Silt','Peaty','Chalky'],'Crop':CROPS,'Weather_Condition':['Sunny','Cloudy','Rainy'],'Rainfall_mm':{'min':100,'max':1000},'Temperature_Celsius':{'min':15,'max':40}}
def predict_rows(rows):
    try:
        model=load_model()
        frame=pd.DataFrame([r.model_dump() for r in rows],columns=FEATURES)
        values=np.asarray(model.predict(frame),dtype=float).reshape(-1)
        if len(values)!=len(rows) or not np.isfinite(values).all():raise RuntimeError('Invalid model response')
        return [{'inputs':row.model_dump(),'yield_t_ha':float(value),'yield_kg_ha':float(value)*1000,'model_version':VERSION,'data_status':'real_model','warning':'Negative estimate; review inputs and limitations' if value<0 else None} for row,value in zip(rows,values)]
    except Exception:
        logging.error('Model prediction unavailable')
        raise HTTPException(503,'Model unavailable; retry later. No substitute prediction was generated.')
@app.post('/api/predict',dependencies=[Depends(authorize)])
def predict(row:Conditions):return predict_rows([row])[0]
@app.post('/api/compare-crops',dependencies=[Depends(authorize)])
def compare(row:Conditions):return {'results':predict_rows([Conditions(**{**row.model_dump(),'Crop':crop}) for crop in CROPS])}
@app.post('/api/batch-predict',dependencies=[Depends(authorize)])
def batch(body:Batch):return {'results':predict_rows(body.rows)}
