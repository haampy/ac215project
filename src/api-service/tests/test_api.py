import requests

def test_inference_api():
    url = "http://localhost:9000/infer/"
    files = {'file': open('tests/test_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    assert response.status_code == 200
    assert "identified_drug_name" in response.json()
