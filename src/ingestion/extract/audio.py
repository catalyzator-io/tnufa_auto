from typing import Optional
import logging
import tempfile
import os
from pathlib import Path

import torch
from transformers import (
    AutoModelForSpeechSeq2Seq, 
    AutoProcessor, 
    pipeline
)

from .base import BaseExtractor

logger = logging.getLogger(__name__)

class AudioExtractor(BaseExtractor):
    """Handles audio formats using Whisper large-v3"""
    
    supported_formats = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
    
    def __init__(self):
        """Initialize Whisper model with optimal configuration for accuracy"""
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Initialize model with Flash Attention 2
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            "openai/whisper-large-v3",
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
            # attn_implementation="flash_attention_2"
        )
        self.model.to(self.device)
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")
        
        # Create pipeline with optimal settings for accuracy
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
    
    def extract_text(self, file_data: bytes, filename: str) -> Optional[str]:
        """Extract text from audio files using Whisper
        
        Args:
            file_data: Raw bytes of the audio file
            filename: Name of the file including extension
            
        Returns:
            Transcribed text if successful, None otherwise
            
        Note:
            Uses Whisper large-v3 with:
            - Flash Attention 2 for faster processing
            - Temperature fallback for better accuracy
            - Sequential processing for long audio
            - Advanced decoding parameters
        """
        try:
            # Verify file format is supported
            extension = filename.lower().split('.')[-1]
            if f'.{extension}' not in self.supported_formats:
                logger.error(f"Unsupported audio format: {extension}")
                return None
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{extension}") as temp_file:
                # Write bytes to temporary file
                temp_file.write(file_data)
                temp_file.flush()
                
                # Configure generation parameters for maximum accuracy
                generate_kwargs = {
                    "task": "transcribe",  # Transcription task
                    "language": "english",  # Auto-detect language
                    "condition_on_prev_tokens": True,  # Use previous tokens for context
                    "compression_ratio_threshold": 1.35,  # Threshold for repetition detection
                    "no_speech_threshold": 0.6,  # Threshold for silence detection
                    "logprob_threshold": -1.0,  # Log probability threshold
                    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),  # Temperature fallback
                    "num_beams": 5,  # Beam search for better accuracy
                }
                
                # Process audio file
                result = self.pipe(
                    temp_file.name,
                    batch_size=1,  # Process sequentially for accuracy
                    return_timestamps=True,  # Get word-level timestamps
                    generate_kwargs=generate_kwargs
                )
                
                # Extract and clean text
                if isinstance(result, dict) and "text" in result:
                    return self._clean_text(result["text"])
                return None
            
        except Exception as e:
            logger.exception(f"Error extracting text from {filename}")
            raise ValueError(f"Failed to extract content from {filename}: {e}")