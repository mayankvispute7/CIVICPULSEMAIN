import requests, json
res = requests.post('http://localhost:8000/api/v1/execution/work-orders/e8ccf604-7ffb-4e6d-8f1c-181963b441fc/verify')
print('RunVerify:', res.status_code, res.text)
