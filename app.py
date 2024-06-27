import gradio as gr
from llm_models import get_text_image_pairs
from tqdm import tqdm

# Markdown HTML for the title
title_markdown = """
<div style="display: flex; justify-content: center; align-items: center; text-align: center; direction: rtl;">
  <img src="https://s11.ax1x.com/2023/12/28/piqvDMV.png" alt="MoE-LLaVA🚀" style="max-width: 120px; height: auto; margin-right: 20px;">
  <div style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
    <h1 style="margin: 0; font-size: 4em;">الراوي</h1>
    <br>
    <h2 style="margin: 0; font-size: 1.5em;">صانع القصص بالذكاء الاصطناعي التوليدي</h2>
  </div>
</div>
"""

# Function to fetch text and image pairs
def get_text_images_values(k, input_prompt):
    pages = int(k)
    segments_list, images_names = get_text_image_pairs(pages, input_prompt)
    return segments_list, images_names

# Custom CSS for RTL direction and styling
css = """
.gradio-container {direction: rtl}
.gradio-container-4-18-0 .prose h1 {direction: rtl};
}

.rtl-textbox {
    direction: rtl;
}
"""

# Define the Gradio interface
with gr.Blocks(css=css) as demo:
    # Display title as Markdown
    gr.Markdown(title_markdown)

    # Textbox for input prompt
    prompt = gr.Textbox(
        label="معلومات بسيطة عن القصة",
        info="أدخل بعض المعلومات عن القصة، مثلاً: خالد صبي في الرابعة من عمره، ويحب أن يصبح طياراً في المستقبل",
        placeholder="خالد صبي في الرابعة من عمره، ويحب أن يصبح طياراً في المستقبل",
        text_align="right",
        rtl=True,
        elem_classes="rtl-textbox",
        elem_id="rtl-textbox"
    )

    # Row for dynamic text and image outputs
    with gr.Row():
        max_textboxes = 10  # Maximum number of textboxes and images in the layout

        # Function to create dynamic textboxes based on number of pages selected
        def variable_outputs(k, segments_list):
            k = int(k)
            return [gr.Textbox(label=f"الصفحة رقم {i+1}", value=item, text_align="right", visible=True) for i, item in enumerate(segments_list)] + [gr.Textbox(visible=False, text_align="right", rtl=True)]*(max_textboxes-k)

        # Function to create dynamic image boxes based on number of pages selected
        def variable_outputs_image(k, images_names):
            k = int(k)
            return [gr.Image(value=item, scale=1, visible=True) for item in images_names] + [gr.Image(scale=1, visible=False)]*(max_textboxes-k)

        # Column for layout
        with gr.Column():
            options = list(range(1, max_textboxes + 1))
            s = gr.Dropdown(choices=options, value=1, label="كم عدد صفحات القصة التي تريدها؟")
            textboxes = []
            imageboxes = []
            for i in tqdm(range(max_textboxes)):
                with gr.Row():
                    i_t = gr.Image(visible=False)
                    t = gr.Textbox(visible=False)
                    imageboxes.append(i_t)
                    textboxes.append(t)

            segment_list = gr.JSON(value=[], visible=False)
            images_list = gr.JSON(value=[], visible=False)

    # Markdown to display status message
    status_text = gr.Markdown(
        value='<div style="background-color: #f0f0f0; color: #333; padding: 10px; border-radius: 5px; text-align: center;">جاري إنشاء القصة، يرجى الانتظار...</div>',
        visible=False
    )

    # Button to submit and trigger story generation
    submit = gr.Button(value="أنشئ القصة الآن")

    # Function to handle button click event
    submit.click(
        fn=lambda: gr.update(value=status_text.value, visible=True),
        inputs=None,
        outputs=status_text,
    ).then(
        fn=get_text_images_values,
        inputs=[s, prompt],
        outputs=[segment_list, images_list]
    ).then(
        fn=variable_outputs,
        inputs=[s, segment_list],
        outputs=textboxes,
    ).then(
        fn=variable_outputs_image,
        inputs=[s, images_list],
        outputs=imageboxes,
    ).then(
        fn=lambda: gr.update(visible=False),
        inputs=None,
        outputs=status_text,
    )

# Launch the Gradio app
demo.launch()
