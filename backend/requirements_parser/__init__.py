"""
Requirements Parser Module for Healthcare Test Case Generation System

This module handles the parsing and extraction of requirements from various document formats
including PDF, Word, XML, and Markdown files. It uses Google Document AI for advanced
document understanding and extraction.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import mimetypes
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

# Document processing libraries
import PyPDF2
import pdfplumber
from docx import Document
import xml.etree.ElementTree as ET
import markdown
from bs4 import BeautifulSoup

# Google Cloud Document AI
from google.cloud import documentai
from google.cloud import storage

# Internal imports
from backend.models.requirements import RequirementDocument, Requirement, RequirementType
from backend.utils.text_processing import clean_text, extract_entities
from backend.utils.exceptions import DocumentProcessingError, UnsupportedFormatError

logger = logging.getLogger(__name__)


class DocumentFormat(Enum):
    """Supported document formats"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    XML = "xml"
    MARKDOWN = "md"
    HTML = "html"
    TXT = "txt"


@dataclass
class DocumentMetadata:
    """Document metadata structure"""
    filename: str
    format: DocumentFormat
    size_bytes: int
    page_count: Optional[int] = None
    creation_date: Optional[str] = None
    modified_date: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    checksum: Optional[str] = None
    language: Optional[str] = None


@dataclass
class ParsedContent:
    """Parsed document content structure"""
    text: str
    sections: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Optional[DocumentMetadata] = None
    requirements: List[Requirement] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)


class DocumentParser:
    """Main document parser class"""
    
    def __init__(self, 
                 document_ai_client: Optional[documentai.DocumentProcessorServiceClient] = None,
                 storage_client: Optional[storage.Client] = None,
                 project_id: Optional[str] = None,
                 location: str = "us",
                 processor_id: Optional[str] = None):
        """
        Initialize document parser
        
        Args:
            document_ai_client: Google Document AI client
            storage_client: Google Cloud Storage client
            project_id: Google Cloud project ID
            location: Document AI processor location
            processor_id: Document AI processor ID
        """
        self.document_ai_client = document_ai_client
        self.storage_client = storage_client
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        
        # Supported file extensions mapping
        self.format_mapping = {
            '.pdf': DocumentFormat.PDF,
            '.docx': DocumentFormat.DOCX,
            '.doc': DocumentFormat.DOC,
            '.xml': DocumentFormat.XML,
            '.md': DocumentFormat.MARKDOWN,
            '.markdown': DocumentFormat.MARKDOWN,
            '.html': DocumentFormat.HTML,
            '.htm': DocumentFormat.HTML,
            '.txt': DocumentFormat.TXT
        }
    
    async def parse_document(self, 
                           file_path: Union[str, Path], 
                           content: Optional[bytes] = None,
                           use_document_ai: bool = True) -> ParsedContent:
        """
        Parse a document and extract its content
        
        Args:
            file_path: Path to the document file
            content: Document content as bytes (if file_path is not provided)
            use_document_ai: Whether to use Google Document AI for parsing
            
        Returns:
            ParsedContent object containing extracted information
        """
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            # Determine document format
            document_format = self._detect_format(file_path)
            
            # Generate metadata
            metadata = await self._extract_metadata(file_path, content)
            
            # Parse based on format and availability of Document AI
            if use_document_ai and self.document_ai_client and document_format in [DocumentFormat.PDF, DocumentFormat.DOCX]:
                parsed_content = await self._parse_with_document_ai(file_path, content, metadata)
            else:
                parsed_content = await self._parse_with_traditional_methods(file_path, content, document_format, metadata)
            
            # Extract requirements from parsed content
            parsed_content.requirements = await self._extract_requirements(parsed_content)
            
            logger.info(f"Successfully parsed document: {file_path.name if file_path else 'content'}")
            return parsed_content
            
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {str(e)}")
            raise DocumentProcessingError(f"Failed to parse document: {str(e)}")
    
    def _detect_format(self, file_path: Path) -> DocumentFormat:
        """Detect document format from file extension"""
        suffix = file_path.suffix.lower()
        if suffix not in self.format_mapping:
            raise UnsupportedFormatError(f"Unsupported file format: {suffix}")
        return self.format_mapping[suffix]
    
    async def _extract_metadata(self, 
                              file_path: Optional[Path], 
                              content: Optional[bytes]) -> DocumentMetadata:
        """Extract document metadata"""
        if file_path and file_path.exists():
            stat = file_path.stat()
            size_bytes = stat.st_size
            filename = file_path.name
            format_type = self._detect_format(file_path)
            
            # Calculate checksum
            if content:
                checksum = hashlib.sha256(content).hexdigest()
            else:
                with open(file_path, 'rb') as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()
        else:
            size_bytes = len(content) if content else 0
            filename = "uploaded_document"
            format_type = DocumentFormat.PDF  # Default assumption
            checksum = hashlib.sha256(content).hexdigest() if content else None
        
        return DocumentMetadata(
            filename=filename,
            format=format_type,
            size_bytes=size_bytes,
            checksum=checksum
        )
    
    async def _parse_with_document_ai(self, 
                                    file_path: Optional[Path], 
                                    content: Optional[bytes],
                                    metadata: DocumentMetadata) -> ParsedContent:
        """Parse document using Google Document AI"""
        try:
            # Prepare document for processing
            if content:
                document_content = content
            else:
                with open(file_path, 'rb') as f:
                    document_content = f.read()
            
            # Create the document object
            document = documentai.Document(
                content=document_content,
                mime_type=self._get_mime_type(metadata.format)
            )
            
            # Process the document
            request = documentai.ProcessRequest(
                name=f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}",
                raw_document=documentai.RawDocument(
                    content=document_content,
                    mime_type=self._get_mime_type(metadata.format)
                )
            )
            
            result = self.document_ai_client.process_document(request=request)
            processed_doc = result.document
            
            # Extract content
            text = processed_doc.text
            sections = self._extract_sections_from_document_ai(processed_doc)
            tables = self._extract_tables_from_document_ai(processed_doc)
            
            return ParsedContent(
                text=text,
                sections=sections,
                tables=tables,
                metadata=metadata,
                structure=self._build_document_structure(sections)
            )
            
        except Exception as e:
            logger.warning(f"Document AI parsing failed: {str(e)}. Falling back to traditional methods.")
            return await self._parse_with_traditional_methods(file_path, content, metadata.format, metadata)
    
    async def _parse_with_traditional_methods(self, 
                                            file_path: Optional[Path], 
                                            content: Optional[bytes],
                                            document_format: DocumentFormat,
                                            metadata: DocumentMetadata) -> ParsedContent:
        """Parse document using traditional parsing methods"""
        
        if document_format == DocumentFormat.PDF:
            return await self._parse_pdf(file_path, content, metadata)
        elif document_format == DocumentFormat.DOCX:
            return await self._parse_docx(file_path, content, metadata)
        elif document_format == DocumentFormat.XML:
            return await self._parse_xml(file_path, content, metadata)
        elif document_format == DocumentFormat.MARKDOWN:
            return await self._parse_markdown(file_path, content, metadata)
        elif document_format == DocumentFormat.HTML:
            return await self._parse_html(file_path, content, metadata)
        elif document_format == DocumentFormat.TXT:
            return await self._parse_txt(file_path, content, metadata)
        else:
            raise UnsupportedFormatError(f"Traditional parsing not supported for {document_format}")
    
    async def _parse_pdf(self, 
                        file_path: Optional[Path], 
                        content: Optional[bytes],
                        metadata: DocumentMetadata) -> ParsedContent:
        """Parse PDF document"""
        text = ""
        sections = []
        tables = []
        
        try:
            if content:
                # Use BytesIO for content
                import io
                pdf_file = io.BytesIO(content)
            else:
                pdf_file = open(file_path, 'rb')
            
            # Try with pdfplumber first (better for tables and layout)
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    metadata.page_count = len(pdf.pages)
                    
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                        
                        # Extract tables from page
                        page_tables = page.extract_tables()
                        for table_idx, table in enumerate(page_tables):
                            tables.append({
                                'page': page_num + 1,
                                'table_id': f"table_{page_num}_{table_idx}",
                                'data': table,
                                'headers': table[0] if table else []
                            })
            
            except Exception as e:
                logger.warning(f"pdfplumber failed: {str(e)}. Trying PyPDF2...")
                
                # Fallback to PyPDF2
                if content:
                    pdf_file.seek(0)
                else:
                    pdf_file.close()
                    pdf_file = open(file_path, 'rb')
                
                reader = PyPDF2.PdfReader(pdf_file)
                metadata.page_count = len(reader.pages)
                
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            finally:
                if hasattr(pdf_file, 'close'):
                    pdf_file.close()
            
            # Extract sections based on text structure
            sections = self._extract_sections_from_text(text)
            
            return ParsedContent(
                text=clean_text(text),
                sections=sections,
                tables=tables,
                metadata=metadata,
                structure=self._build_document_structure(sections)
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to parse PDF: {str(e)}")
    
    async def _parse_docx(self, 
                         file_path: Optional[Path], 
                         content: Optional[bytes],
                         metadata: DocumentMetadata) -> ParsedContent:
        """Parse DOCX document"""
        try:
            if content:
                import io
                doc_file = io.BytesIO(content)
            else:
                doc_file = file_path
            
            doc = Document(doc_file)
            
            # Extract text and structure
            text = ""
            sections = []
            tables = []
            
            # Extract document properties
            props = doc.core_properties
            metadata.author = props.author
            metadata.title = props.title
            metadata.subject = props.subject
            metadata.creation_date = props.created.isoformat() if props.created else None
            metadata.modified_date = props.modified.isoformat() if props.modified else None
            
            current_section = {"title": "Document", "content": "", "level": 0, "paragraphs": []}
            
            for element in doc.element.body:
                if element.tag.endswith('p'):  # Paragraph
                    para = doc.paragraphs[len(sections)]
                    para_text = para.text
                    text += para_text + "\n"
                    current_section["content"] += para_text + "\n"
                    current_section["paragraphs"].append(para_text)
                    
                    # Check if this is a heading
                    if para.style.name.startswith('Heading'):
                        if current_section["content"].strip():
                            sections.append(current_section)
                        
                        level = int(para.style.name.split()[-1]) if para.style.name.split()[-1].isdigit() else 1
                        current_section = {
                            "title": para_text,
                            "content": "",
                            "level": level,
                            "paragraphs": []
                        }
                
                elif element.tag.endswith('tbl'):  # Table
                    table_idx = len(tables)
                    table_data = []
                    
                    for table in doc.tables:
                        if len(table_data) <= table_idx:
                            rows = []
                            for row in table.rows:
                                cells = [cell.text for cell in row.cells]
                                rows.append(cells)
                            table_data.append(rows)
                    
                    if table_data:
                        tables.append({
                            'table_id': f"table_{table_idx}",
                            'data': table_data[-1],
                            'headers': table_data[-1][0] if table_data[-1] else []
                        })
            
            # Add final section
            if current_section["content"].strip():
                sections.append(current_section)
            
            return ParsedContent(
                text=clean_text(text),
                sections=sections,
                tables=tables,
                metadata=metadata,
                structure=self._build_document_structure(sections)
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to parse DOCX: {str(e)}")
    
    async def _parse_xml(self, 
                        file_path: Optional[Path], 
                        content: Optional[bytes],
                        metadata: DocumentMetadata) -> ParsedContent:
        """Parse XML document"""
        try:
            if content:
                xml_content = content.decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
            
            root = ET.fromstring(xml_content)
            
            text = ""
            sections = []
            
            def extract_xml_elements(element, level=0):
                section = {
                    "title": element.tag,
                    "content": element.text or "",
                    "level": level,
                    "attributes": element.attrib
                }
                
                for child in element:
                    child_section = extract_xml_elements(child, level + 1)
                    sections.append(child_section)
                    section["content"] += child_section["content"]
                
                return section
            
            # Extract all elements
            root_section = extract_xml_elements(root)
            sections.insert(0, root_section)
            
            # Create text representation
            text = ET.tostring(root, encoding='unicode', method='text')
            
            return ParsedContent(
                text=clean_text(text),
                sections=sections,
                metadata=metadata,
                structure={"xml_root": root.tag, "namespace": root.tag.split('}')[0] if '}' in root.tag else None}
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to parse XML: {str(e)}")
    
    async def _parse_markdown(self, 
                             file_path: Optional[Path], 
                             content: Optional[bytes],
                             metadata: DocumentMetadata) -> ParsedContent:
        """Parse Markdown document"""
        try:
            if content:
                md_content = content.decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['tables', 'toc', 'meta'])
            html_content = md.convert(md_content)
            
            # Extract metadata from markdown
            if hasattr(md, 'Meta'):
                for key, value in md.Meta.items():
                    if key == 'title':
                        metadata.title = value[0] if isinstance(value, list) else value
                    elif key == 'author':
                        metadata.author = value[0] if isinstance(value, list) else value
            
            # Parse HTML to extract structure
            soup = BeautifulSoup(html_content, 'html.parser')
            
            sections = []
            text = soup.get_text()
            
            # Extract sections based on headers
            for i, header in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
                level = int(header.name[1])
                title = header.get_text()
                
                # Get content until next header
                content = ""
                for sibling in header.next_siblings:
                    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    if hasattr(sibling, 'get_text'):
                        content += sibling.get_text() + "\n"
                
                sections.append({
                    "title": title,
                    "content": content.strip(),
                    "level": level
                })
            
            # Extract tables
            tables = []
            for i, table in enumerate(soup.find_all('table')):
                rows = []
                for row in table.find_all('tr'):
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    rows.append(cells)
                
                tables.append({
                    'table_id': f"table_{i}",
                    'data': rows,
                    'headers': rows[0] if rows else []
                })
            
            return ParsedContent(
                text=clean_text(text),
                sections=sections,
                tables=tables,
                metadata=metadata,
                structure=self._build_document_structure(sections)
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to parse Markdown: {str(e)}")
    
    async def _parse_html(self, 
                         file_path: Optional[Path], 
                         content: Optional[bytes],
                         metadata: DocumentMetadata) -> ParsedContent:
        """Parse HTML document"""
        try:
            if content:
                html_content = content.decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata from HTML head
            title_tag = soup.find('title')
            if title_tag:
                metadata.title = title_tag.get_text()
            
            author_meta = soup.find('meta', attrs={'name': 'author'})
            if author_meta:
                metadata.author = author_meta.get('content')
            
            # Extract text content
            text = soup.get_text()
            
            # Extract sections based on headers
            sections = []
            for i, header in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
                level = int(header.name[1])
                title = header.get_text()
                
                # Get content until next header
                content = ""
                for sibling in header.next_siblings:
                    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    if hasattr(sibling, 'get_text'):
                        content += sibling.get_text() + "\n"
                
                sections.append({
                    "title": title,
                    "content": content.strip(),
                    "level": level
                })
            
            # Extract tables
            tables = []
            for i, table in enumerate(soup.find_all('table')):
                rows = []
                for row in table.find_all('tr'):
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    rows.append(cells)
                
                tables.append({
                    'table_id': f"table_{i}",
                    'data': rows,
                    'headers': rows[0] if rows else []
                })
            
            return ParsedContent(
                text=clean_text(text),
                sections=sections,
                tables=tables,
                metadata=metadata,
                structure=self._build_document_structure(sections)
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to parse HTML: {str(e)}")
    
    async def _parse_txt(self, 
                        file_path: Optional[Path], 
                        content: Optional[bytes],
                        metadata: DocumentMetadata) -> ParsedContent:
        """Parse plain text document"""
        try:
            if content:
                text = content.decode('utf-8')
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Simple section extraction based on double newlines or numbered sections
            sections = self._extract_sections_from_text(text)
            
            return ParsedContent(
                text=clean_text(text),
                sections=sections,
                metadata=metadata,
                structure=self._build_document_structure(sections)
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to parse TXT: {str(e)}")
    
    def _extract_sections_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract sections from plain text"""
        sections = []
        lines = text.split('\n')
        
        current_section = {"title": "Document", "content": "", "level": 0}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered sections (1., 1.1., etc.)
            if line.match(r'^\d+\.(\d+\.)*\s+'):
                if current_section["content"].strip():
                    sections.append(current_section)
                
                level = line.count('.')
                current_section = {
                    "title": line,
                    "content": "",
                    "level": level
                }
            else:
                current_section["content"] += line + "\n"
        
        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_sections_from_document_ai(self, document) -> List[Dict[str, Any]]:
        """Extract sections from Document AI processed document"""
        sections = []
        
        # This would be implemented based on Document AI's output structure
        # For now, return basic text extraction
        if hasattr(document, 'pages'):
            for page_idx, page in enumerate(document.pages):
                if hasattr(page, 'blocks'):
                    for block_idx, block in enumerate(page.blocks):
                        section = {
                            "title": f"Page {page_idx + 1} Block {block_idx + 1}",
                            "content": self._get_text_from_layout(block, document.text),
                            "level": 1,
                            "page": page_idx + 1
                        }
                        sections.append(section)
        
        return sections
    
    def _extract_tables_from_document_ai(self, document) -> List[Dict[str, Any]]:
        """Extract tables from Document AI processed document"""
        tables = []
        
        if hasattr(document, 'pages'):
            for page_idx, page in enumerate(document.pages):
                if hasattr(page, 'tables'):
                    for table_idx, table in enumerate(page.tables):
                        table_data = []
                        
                        if hasattr(table, 'body_rows'):
                            for row in table.body_rows:
                                row_data = []
                                if hasattr(row, 'cells'):
                                    for cell in row.cells:
                                        cell_text = self._get_text_from_layout(cell, document.text)
                                        row_data.append(cell_text)
                                table_data.append(row_data)
                        
                        tables.append({
                            'page': page_idx + 1,
                            'table_id': f"table_{page_idx}_{table_idx}",
                            'data': table_data,
                            'headers': table_data[0] if table_data else []
                        })
        
        return tables
    
    def _get_text_from_layout(self, layout, document_text: str) -> str:
        """Extract text from Document AI layout element"""
        if hasattr(layout, 'text_anchor') and hasattr(layout.text_anchor, 'text_segments'):
            text = ""
            for segment in layout.text_anchor.text_segments:
                start_index = segment.start_index if hasattr(segment, 'start_index') else 0
                end_index = segment.end_index if hasattr(segment, 'end_index') else len(document_text)
                text += document_text[start_index:end_index]
            return text
        return ""
    
    def _build_document_structure(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build hierarchical document structure"""
        structure = {
            "type": "document",
            "sections": len(sections),
            "hierarchy": {}
        }
        
        for section in sections:
            level = section.get("level", 0)
            if level not in structure["hierarchy"]:
                structure["hierarchy"][level] = []
            structure["hierarchy"][level].append(section["title"])
        
        return structure
    
    async def _extract_requirements(self, parsed_content: ParsedContent) -> List[Requirement]:
        """Extract requirements from parsed content using AI and rule-based methods"""
        requirements = []
        
        # This will be implemented in the next phase with AI integration
        # For now, implement basic rule-based extraction
        
        text = parsed_content.text
        sections = parsed_content.sections
        
        # Look for requirement patterns
        requirement_patterns = [
            r'(?i)(shall|must|should|will)\s+(.+?)(?=\.|$)',
            r'(?i)requirement\s*\d*\s*:?\s*(.+?)(?=\.|$)',
            r'(?i)req\s*\d+\s*:?\s*(.+?)(?=\.|$)'
        ]
        
        import re
        
        for section in sections:
            section_text = section.get("content", "")
            
            for pattern in requirement_patterns:
                matches = re.finditer(pattern, section_text, re.MULTILINE)
                
                for match in matches:
                    requirement_text = match.group(0).strip()
                    
                    # Create requirement object
                    requirement = Requirement(
                        id=f"REQ_{len(requirements) + 1:04d}",
                        text=requirement_text,
                        type=self._classify_requirement_type(requirement_text),
                        section=section.get("title", "Unknown"),
                        priority="Medium",  # Default priority
                        source_location={
                            "section": section.get("title"),
                            "page": section.get("page"),
                            "line": None
                        }
                    )
                    
                    requirements.append(requirement)
        
        logger.info(f"Extracted {len(requirements)} requirements")
        return requirements
    
    def _classify_requirement_type(self, requirement_text: str) -> RequirementType:
        """Classify requirement type based on text content"""
        text_lower = requirement_text.lower()
        
        # Simple keyword-based classification
        if any(keyword in text_lower for keyword in ['security', 'access', 'authentication', 'authorization']):
            return RequirementType.SECURITY
        elif any(keyword in text_lower for keyword in ['performance', 'speed', 'time', 'response']):
            return RequirementType.PERFORMANCE
        elif any(keyword in text_lower for keyword in ['interface', 'ui', 'user', 'display']):
            return RequirementType.INTERFACE
        elif any(keyword in text_lower for keyword in ['data', 'database', 'storage']):
            return RequirementType.DATA
        else:
            return RequirementType.FUNCTIONAL
    
    def _get_mime_type(self, document_format: DocumentFormat) -> str:
        """Get MIME type for document format"""
        mime_mapping = {
            DocumentFormat.PDF: "application/pdf",
            DocumentFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            DocumentFormat.DOC: "application/msword",
            DocumentFormat.XML: "application/xml",
            DocumentFormat.HTML: "text/html",
            DocumentFormat.TXT: "text/plain"
        }
        return mime_mapping.get(document_format, "application/octet-stream")


# Initialize document parser
async def init_document_parser() -> DocumentParser:
    """Initialize and return document parser with Google Cloud services"""
    try:
        # Initialize Google Cloud clients
        document_ai_client = documentai.DocumentProcessorServiceClient()
        storage_client = storage.Client()
        
        # Get configuration
        from config import GOOGLE_CLOUD_PROJECT, VERTEX_AI_LOCATION
        
        parser = DocumentParser(
            document_ai_client=document_ai_client,
            storage_client=storage_client,
            project_id=GOOGLE_CLOUD_PROJECT,
            location=VERTEX_AI_LOCATION
        )
        
        logger.info("Document parser initialized successfully")
        return parser
        
    except Exception as e:
        logger.warning(f"Failed to initialize Google Cloud services: {str(e)}. Using local parsing only.")
        return DocumentParser()


# Export main classes
__all__ = [
    'DocumentParser',
    'DocumentFormat',
    'DocumentMetadata',
    'ParsedContent',
    'init_document_parser'
]