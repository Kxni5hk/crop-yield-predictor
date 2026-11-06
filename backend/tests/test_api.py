import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
import main
os.environ['INFERENCE_TOKEN']='review-test-token-not-a-secret-123456789'
client=TestClient(main.app)
headers={'X-Inference-Token':os.environ['INFERENCE_TOKEN']}
row=dict(Region='North',Soil_Type='Loam',Crop='Wheat',Rainfall_mm=550,Temperature_Celsius=27.5,Fertilizer_Used=True,Irrigation_Used=True,Weather_Condition='Sunny')
def test_requires_token():assert client.post('/api/predict',json=row).status_code==401
@pytest.mark.parametrize('patch',[{'Crop':'Coffee'},{'Rainfall_mm':99},{'Temperature_Celsius':41},{'Fertilizer_Used':'yes'},{'Days_to_Harvest':100},{'Rainfall_mm':True}])
def test_invalid_inputs(patch):assert client.post('/api/predict',json={**row,**patch},headers=headers).status_code==422
def test_actual_prediction_matches_pipeline():
    r=client.post('/api/predict',json=row,headers=headers);assert r.status_code==200
    expected=float(main.load_model().predict(main.pd.DataFrame([row],columns=main.FEATURES))[0])
    assert r.json()['yield_t_ha']==expected
    assert r.json()['yield_kg_ha']==expected*1000
    assert r.json()['data_status']=='real_model'
def test_all_six_crops():
    r=client.post('/api/compare-crops',json=row,headers=headers);assert r.status_code==200
    assert [x['inputs']['Crop'] for x in r.json()['results']]==main.CROPS
def test_batch_limits():
    assert len(client.post('/api/batch-predict',json={'rows':[row,row]},headers=headers).json()['results'])==2
    assert client.post('/api/batch-predict',json={'rows':[row]*51},headers=headers).status_code==422
def test_unavailable_model_has_no_estimate(monkeypatch):
    def fail():raise RuntimeError('Unavailable')
    monkeypatch.setattr(main,'load_model',fail)
    r=client.post('/api/predict',json=row,headers=headers);assert r.status_code==503;assert 'yield_t_ha' not in r.json()
def test_checksum_rejects_untrusted_artifact(monkeypatch,tmp_path):
    bad=tmp_path/'bad.joblib';bad.write_bytes(b'not the model');monkeypatch.setenv('MODEL_PATH',str(bad));monkeypatch.setattr(main,'_model',None)
    with pytest.raises(RuntimeError,match='checksum'):main.load_model()
def test_body_limit():assert client.post('/api/predict',content=b'x'*131073,headers=headers).status_code==413
