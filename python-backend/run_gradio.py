from atom_rag import pipeline_completo
import gradio as gr

demo = gr.Interface(fn=pipeline_completo, inputs=["text"], outputs=["text"])
demo.launch(server_name="0.0.0.0", server_port=7860)