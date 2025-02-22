import tensorflow as tf
from tf_keras.models import Model
from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer

def summarize(text):
    model_name = "t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = TFAutoModelForSeq2SeqLM.from_pretrained(model_name)
    input_text = "summarize: " + text
    inputs = tokenizer(input_text, return_tensors="tf", max_length=512, truncation=True)
    summary_ids = model.generate(inputs["input_ids"], max_length=300, min_length=30, length_penalty=4.0, num_beams=4)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary
