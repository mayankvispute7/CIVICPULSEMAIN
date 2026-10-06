import requests, json, datetime

res2 = requests.post('http://localhost:8000/api/v1/execution/evidence', json={
  'work_order_id': 'test',
  'captured_at': datetime.datetime.now().isoformat(),
  'latitude': 18.0,
  'longitude': 73.0,
  'image_url': 'A' * 4000000
})
print('Verify:', res2.status_code, res2.text)
