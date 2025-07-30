import gradio as gr
import threading
import uvicorn

def run_api():
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860)

# Start FastAPI in background
threading.Thread(target=run_api).start()

# Minimal dummy Gradio app to keep the Space alive
gr.Interface(lambda x: x, inputs="text", outputs="text").launch()