import requests
import json
import sys

def main():
    print("=========================================")
    print("   CLOUDFLARE WORKERS AI - API TESTER   ")
    print("=========================================")
    
    account_id = input("Masukkan Account ID Cloudflare : ").strip()
    api_key = input("Masukkan API Token Cloudflare  : ").strip()
    model = "@cf/meta/llama-3.1-8b-instruct"

    if not account_id or not api_key:
        print("⚠️  Error: Account ID dan API Token tidak boleh kosong!")
        sys.exit(1)

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "user", "content": "Halo! Jawab pesan ini dengan: 'Koneksi ke Llama-3 Cloudflare Berhasil!'"}
        ]
    }

    print(f"\n🔄 Mengirim permintaan ke model {model}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success"):
                reply = res_json["result"]["response"]
                print("\n✅ SUCCESS! KONEKSI BERHASIL.")
                print("-" * 40)
                print(f"Jawaban AI: {reply}")
                print("-" * 40)
            else:
                print(f"\n❌ GAGAL. Server merespon, tetapi ada error: {res_json.get('errors')}")
        else:
            print(f"\n❌ GAGAL (Error {response.status_code})")
            print("Pastikan Token Anda memiliki izin 'Workers AI' dan Account ID benar.")
            print(f"Pesan Server: {response.text}")
            
    except Exception as e:
        print(f"\n❌ KONEKSI ERROR: {e}")
        print("Pastikan komputer Anda terhubung ke internet.")

if __name__ == "__main__":
    main()
