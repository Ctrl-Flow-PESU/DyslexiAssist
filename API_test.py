import requests

# Test text-to-speech
response = requests.post('http://localhost:5000/api/text-to-speech', 
    json={
        "text": "Hello, this is a test",
        "speed": 150
    })
print(response.json())