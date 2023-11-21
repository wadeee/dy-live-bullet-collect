from fastapi import FastAPI, HTTPException
import aiohttp
from aiohttp import web
import asyncio
import uvicorn
from server import wshandler
app = FastAPI()

async def fetch_data_from_external_api(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@app.get("/fastapi-data/")
async def read_fastapi_data():
    return {"message": "This data is from FastAPI"}

@app.get("/aiohttp-data/")
async def read_aiohttp_data():

    external_api_url = "https://jsonplaceholder.typicode.com/todos/1"
    data = await fetch_data_from_external_api(external_api_url)
    return data

app.mount("/id", wshandler)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
