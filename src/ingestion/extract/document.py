from typing import Optional
import logging
from pathlib import Path
import tempfile
import os

from docling.document_converter import (
    DocumentConverter, 
    InputFormat,
    ConversionStatus,
    PdfFormatOption,
    WordFormatOption,
    PowerpointFormatOption,
    ExcelFormatOption
)
from docling.datamodel.pipeline_options import (
    PipelineOptions,
    PdfPipelineOptions,
    TableFormerMode
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

from src.ingestion.extract.base import BaseExtractor

logger = logging.getLogger(__name__)

class DocumentExtractor(BaseExtractor):
    """Handles document formats using Docling's advanced document understanding"""
    
    supported_formats: set[str] = {
        # Documents
        '.pdf',
        '.docx',
        '.doc',
        # Presentations
        '.pptx',
        '.ppt',
        # Spreadsheets
        '.xlsx',
        '.xls',
        # Text formats
        '.txt',
        '.json',
        '.md',
        # Web formats
        '.html',
        '.htm',
        # Documentation formats
        '.adoc',
        '.asciidoc'
    }
    
    def __init__(self):
        """Initialize Docling converter with appropriate options"""
        # Configure PDF pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        
        # Configure format-specific options
        format_options = {
            # PDF with advanced processing
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                pipeline_cls=StandardPdfPipeline
            ),
            # Microsoft Word documents
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline,
                pipeline_options=PipelineOptions(
                    keep_images=True,
                    do_table_structure=True
                )
            ),
            # PowerPoint presentations
            InputFormat.PPTX: PowerpointFormatOption(
                pipeline_cls=SimplePipeline,
                pipeline_options=PipelineOptions(
                    keep_images=True
                )
            ),
            # Excel spreadsheets
            InputFormat.XLSX: ExcelFormatOption(
                pipeline_cls=SimplePipeline,
                pipeline_options=PipelineOptions(
                    do_table_structure=True,
                    extract_formulas=True
                )
            )
        }
        
        # Initialize document converter with all supported formats
        self.converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.PPTX,
                InputFormat.XLSX,
                InputFormat.HTML,
                InputFormat.MD,
                InputFormat.ASCIIDOC
            ],
            format_options=format_options
        )
    
    def extract_text(self, file_data: bytes, filename: str) -> Optional[str]:
        """Extract text from document files using Docling
        
        Args:
            file_data: Raw bytes of the document
            filename: Name of the file including extension
            
        Returns:
            Extracted text if successful, None otherwise
            
        Note:
            Uses Docling's advanced document understanding capabilities:
            - Layout analysis for PDFs
            - Table structure recognition
            - OCR using Tesseract
            - Format-specific optimizations
        """
        try:
            # Verify file format is supported
            extension = filename.lower().split('.')[-1]
            if f'.{extension}' not in self.supported_formats:
                logger.error(f"Unsupported file format: {extension}")
                return None
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{extension}") as temp_file:
                # Write bytes to temporary file
                temp_file.write(file_data)
                temp_file.flush()
                
                # Convert document using Docling with file path
                result = self.converter.convert(Path(temp_file.name))
                
                # Handle conversion failure
                if not result.document or result.status == ConversionStatus.FAILURE:
                    logger.error(f"Failed to extract content from {filename}")
                    if result.errors:
                        logger.error(f"Conversion errors: {result.errors}")
                    return None
                
                # Log partial success
                if result.status == ConversionStatus.PARTIAL_SUCCESS:
                    logger.warning(f"Partial success extracting from {filename}")
                    if result.errors:
                        logger.warning(f"Conversion warnings: {result.errors}")
                
                # Export to markdown to preserve structure
                text = result.document.export_to_markdown()
                return self._clean_text(text)
            
        except Exception as e:
            raise ValueError(f"Failed to extract content from {filename}: {e}")
