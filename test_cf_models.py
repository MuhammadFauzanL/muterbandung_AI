import requests
import time
import os

account_id = os.getenv('CF_ACCOUNT_ID') or os.getenv('CLOUDFLARE_ACCOUNT_ID')
api_key = os.getenv('CF_API_TOKEN') or os.getenv('CLOUDFLARE_API_TOKEN')

if not account_id or not api_key:
    raise SystemExit('Set CF_ACCOUNT_ID and CF_API_TOKEN before running this test.')

models = [
    '@cf/qwen/qwen1.5-14b-chat-awq',
    '@cf/meta/llama-3.1-8b-instruct',
    '@cf/google/gemma-7b-it'
]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
data = {
    'messages': [
        {'role': 'system', 'content': 'Anda adalah asisten AI wisata MuterBandung.'},
        {'role': 'user', 'content': 'Rekomendasikan 2 tempat wisata alam di Bandung untuk anak-anak, berikan alasan singkat dalam bahasa Indonesia.'}
    ],
    'max_tokens': 150
}

for model in models:
    url = f'https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}'
    print(f'=== PENGUJIAN: {model} ===')
    start = time.time()
    try:
        res = requests.post(url, headers=headers, json=data)
        elapsed = time.time() - start
        if res.status_code == 200 and res.json().get('success'):
            print(f'Waktu: {elapsed:.2f} detik')
            print(f"Jawaban AI:\n{res.json()['result']['response']}\n")
        else:
            print(f"Gagal memuat model. Status: {res.status_code} - {res.text}\n")
    except Exception as e:
        print(f'Error: {e}')
