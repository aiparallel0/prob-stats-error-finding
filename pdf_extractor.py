"""
PDF text extraction module for extracting text from PDF files page by page.
"""
import pdfplumber
from typing import List, Dict, Optional


class PDFExtractor:
    """Extract text from PDF files page by page."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF extractor.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
    
    def extract_page(self, page_number: int) -> Optional[str]:
        """
        Extract text from a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if page_number < len(pdf.pages):
                    page = pdf.pages[page_number]
                    return page.extract_text()
                return None
        except Exception as e:
            print(f"Error extracting page {page_number}: {e}")
            return None
    
    def extract_all_pages(self) -> List[Dict[str, any]]:
        """
        Extract text from all pages in the PDF.
        
        Returns:
            List of dictionaries containing page number and text
        """
        pages_data = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    pages_data.append({
                        'page_number': i + 1,
                        'text': text if text else ""
                    })
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        
        return pages_data
    
    def get_page_count(self) -> int:
        """
        Get the total number of pages in the PDF.
        
        Returns:
            Number of pages
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            print(f"Error getting page count: {e}")
            return 0
