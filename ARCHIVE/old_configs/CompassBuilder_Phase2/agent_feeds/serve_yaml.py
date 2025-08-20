# Local server to serve YAML to agents via API

from fastapi import FastAPI, HTTPException
import yaml
import uvicorn

app = FastAPI()

@app.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """
    Serve a specific prompt module
    """
    # TODO: Implement prompt serving
    pass

@app.get("/prompts")
async def list_prompts():
    """
    List available prompts
    """
    # TODO: Implement prompt listing
    pass

def main():
    """
    Main server routine
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
