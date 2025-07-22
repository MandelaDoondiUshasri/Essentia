import requests
import gradio as gr

# DeepSeek API Endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

def summarize_text(text):

    payload = {
        "model": "gemma:2b",
        "prompt": f"Summarize the following text in 3 simple bullet points for a general audience:\n\n{text}",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json().get("response", "No summary generated.")
    else:
        return f"Error: {response.text}"



# Create Gradio interface
interface = gr.Interface(
    fn=summarize_text,
    inputs=gr.Textbox(lines=10, placeholder="Enter text to summarize"),
    outputs=gr.Textbox(label="Summarized Text"),
    title="InstaGist",
    description="From essay to essence in a click. Summarize smarter with InstaGist."
)

# Launch the web app
if __name__ == "__main__":
    interface.launch()


# # Test Summarization
# if __name__ == "__main__":
#     sample_text = """
#     Artificial Intelligence is transforming industries across the world. AI models like DeepSeek-R1 enable businesses to automate tasks,
#     analyze large datasets, and enhance productivity. With advancements in AI, applications range from virtual assistants to predictive analytics
#     and personalized recommendations.
#     """
#     print("### Summary ###")
#     print(summarize_text(sample_text))
