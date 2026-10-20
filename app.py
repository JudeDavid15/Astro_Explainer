from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from pydantic import BaseModel
from fastapi import FastAPI

from src.graph import app as agent_app

api = FastAPI(title="Astro Event Explainer")
class Question(BaseModel):
    question: str


@api.post("/ask")
def ask(payload: Question):
    result = agent_app.invoke({"question": payload.question, "route": "", "answer": ""})
    return {
        "question": payload.question,
        "route": result["route"],
        "answer": result["answer"],
    }


def respond(question: str):
    result = agent_app.invoke({"question": question, "route": "", "answer": ""})
    return f"**Route:** {result['route']}\n\n{result['answer']}"


demo = gr.Interface(
    fn=respond,
    inputs=gr.Textbox(label="Ask an astronomy question"),
    outputs=gr.Markdown(label="Answer"),
    title="Astro Event Explainer",

    examples=[
        "Why do stars twinkle?",
        "What's the astronomy picture of the day?",
        "Tell me about space",
    ],
)

# Register /ask FIRST, then mount Gradio at "/" so /ask takes precedence.
app = gr.mount_gradio_app(api, demo, path="/",
                          ssr_mode=False,
                          theme=gr.Theme.load("crimson.json"))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
