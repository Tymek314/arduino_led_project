import uvicorn
#run this to start

if __name__ == "__main__":
    uvicorn.run(
        "web_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )

