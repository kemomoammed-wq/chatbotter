# first line: 75
@memory.cache
def load_hf_model() -> Optional[pipeline]:
    """Load the BART model for text generation."""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available. Skipping HF model loading.")
        return None
    try:
        tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large")
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large")
        return pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)
    except Exception as e:
        logger.error(f"Failed to load HF model: {e}")
        return None
