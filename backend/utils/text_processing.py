"""
Text processing utilities for the Healthcare Test Case Generation System
"""

import re
import string
from typing import List, Dict, Any, Optional, Tuple
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import spacy
from collections import Counter
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('chunkers/maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

logger = logging.getLogger(__name__)

# Initialize spaCy model for advanced NLP
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# Initialize NLTK components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Healthcare-specific terms and patterns
HEALTHCARE_TERMS = {
    'medical_devices': [
        'device', 'equipment', 'instrument', 'monitor', 'scanner', 'pump', 'ventilator',
        'defibrillator', 'pacemaker', 'implant', 'prosthetic', 'catheter', 'stent'
    ],
    'clinical_terms': [
        'patient', 'physician', 'doctor', 'nurse', 'clinician', 'practitioner',
        'diagnosis', 'treatment', 'therapy', 'procedure', 'surgery', 'medication',
        'drug', 'pharmaceutical', 'dosage', 'prescription'
    ],
    'data_terms': [
        'patient data', 'medical record', 'health information', 'clinical data',
        'phi', 'pii', 'protected health information', 'personally identifiable information',
        'electronic health record', 'ehr', 'emr', 'electronic medical record'
    ],
    'compliance_terms': [
        'fda', 'hipaa', 'gdpr', 'iso 13485', 'iso 27001', 'iec 62304',
        'compliance', 'regulation', 'standard', 'validation', 'verification',
        'audit', 'documentation', 'traceability', 'risk management'
    ]
}

# Requirement keywords and patterns
REQUIREMENT_PATTERNS = {
    'modal_verbs': ['shall', 'must', 'should', 'will', 'may', 'can', 'could', 'would'],
    'requirement_indicators': [
        'requirement', 'req', 'specification', 'spec', 'criterion', 'criteria',
        'condition', 'constraint', 'rule', 'standard', 'guideline'
    ],
    'functional_indicators': [
        'function', 'feature', 'capability', 'operation', 'process', 'behavior',
        'perform', 'execute', 'display', 'calculate', 'generate', 'provide'
    ],
    'non_functional_indicators': [
        'performance', 'speed', 'time', 'response', 'throughput', 'reliability',
        'availability', 'scalability', 'usability', 'security', 'safety'
    ]
}


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    # Remove special characters but keep punctuation that might be important
    # for requirements (periods, commas, colons, semicolons)
    text = re.sub(r'[^\w\s\.\,\:\;\!\?\-\(\)\[\]\'\"]+', ' ', text)
    
    # Remove page numbers and headers/footers patterns
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'--- Page \d+ ---', '', text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    try:
        sentences = sent_tokenize(text)
        return [sent.strip() for sent in sentences if sent.strip()]
    except Exception as e:
        logger.warning(f"Error in sentence tokenization: {str(e)}")
        # Fallback to simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [sent.strip() for sent in sentences if sent.strip()]


def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extract important keywords from text
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords sorted by importance
    """
    try:
        # Tokenize and clean
        words = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        words = [word for word in words if word not in stop_words and word not in string.punctuation]
        
        # Remove very short words
        words = [word for word in words if len(word) > 2]
        
        # Lemmatize words
        words = [lemmatizer.lemmatize(word) for word in words]
        
        # Count word frequency
        word_freq = Counter(words)
        
        # Get most common words
        keywords = [word for word, freq in word_freq.most_common(max_keywords)]
        
        return keywords
        
    except Exception as e:
        logger.warning(f"Error in keyword extraction: {str(e)}")
        return []


def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract named entities from text
    
    Args:
        text: Input text
        
    Returns:
        List of entities with their types and positions
    """
    entities = []
    
    try:
        # Use spaCy if available (more accurate)
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'description': spacy.explain(ent.label_)
                })
        else:
            # Fallback to NLTK
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            chunks = ne_chunk(pos_tags)
            
            current_chunk = []
            current_label = None
            
            for i, chunk in enumerate(chunks):
                if hasattr(chunk, 'label'):
                    if current_chunk:
                        entities.append({
                            'text': ' '.join(current_chunk),
                            'label': current_label,
                            'start': None,
                            'end': None,
                            'description': current_label
                        })
                    current_chunk = [token for token, pos in chunk]
                    current_label = chunk.label()
                else:
                    if current_chunk:
                        entities.append({
                            'text': ' '.join(current_chunk),
                            'label': current_label,
                            'start': None,
                            'end': None,
                            'description': current_label
                        })
                        current_chunk = []
                        current_label = None
            
            # Add final chunk if exists
            if current_chunk:
                entities.append({
                    'text': ' '.join(current_chunk),
                    'label': current_label,
                    'start': None,
                    'end': None,
                    'description': current_label
                })
    
    except Exception as e:
        logger.warning(f"Error in entity extraction: {str(e)}")
    
    return entities


def identify_requirements(text: str) -> List[Dict[str, Any]]:
    """
    Identify potential requirements in text using pattern matching
    
    Args:
        text: Input text
        
    Returns:
        List of potential requirements with metadata
    """
    requirements = []
    sentences = extract_sentences(text)
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        
        # Check for requirement patterns
        requirement_score = 0
        indicators = []
        
        # Check for modal verbs
        for verb in REQUIREMENT_PATTERNS['modal_verbs']:
            if re.search(r'\b' + verb + r'\b', sentence_lower):
                requirement_score += 2
                indicators.append(f"modal_verb: {verb}")
        
        # Check for requirement indicators
        for indicator in REQUIREMENT_PATTERNS['requirement_indicators']:
            if re.search(r'\b' + indicator + r'\b', sentence_lower):
                requirement_score += 1
                indicators.append(f"requirement_indicator: {indicator}")
        
        # Check for functional patterns
        for func_indicator in REQUIREMENT_PATTERNS['functional_indicators']:
            if re.search(r'\b' + func_indicator + r'\b', sentence_lower):
                requirement_score += 0.5
                indicators.append(f"functional: {func_indicator}")
        
        # Check for numbered requirements
        if re.match(r'^\d+\.', sentence.strip()):
            requirement_score += 1
            indicators.append("numbered_requirement")
        
        # Consider it a requirement if score is high enough
        if requirement_score >= 1.5:
            req_type = classify_requirement_type(sentence)
            
            requirements.append({
                'text': sentence,
                'score': requirement_score,
                'indicators': indicators,
                'type': req_type,
                'sentence_index': i,
                'keywords': extract_keywords(sentence, max_keywords=10)
            })
    
    return requirements


def classify_requirement_type(text: str) -> str:
    """
    Classify the type of requirement based on text content
    
    Args:
        text: Requirement text
        
    Returns:
        Requirement type
    """
    text_lower = text.lower()
    
    # Security requirements
    security_keywords = ['security', 'access', 'authentication', 'authorization', 'encrypt', 'password', 'login']
    if any(keyword in text_lower for keyword in security_keywords):
        return 'security'
    
    # Performance requirements
    performance_keywords = ['performance', 'speed', 'time', 'response', 'fast', 'latency', 'throughput']
    if any(keyword in text_lower for keyword in performance_keywords):
        return 'performance'
    
    # Interface requirements
    interface_keywords = ['interface', 'ui', 'user interface', 'display', 'screen', 'button', 'menu']
    if any(keyword in text_lower for keyword in interface_keywords):
        return 'interface'
    
    # Data requirements
    data_keywords = ['data', 'database', 'storage', 'store', 'save', 'record', 'information']
    if any(keyword in text_lower for keyword in data_keywords):
        return 'data'
    
    # Compliance requirements
    compliance_keywords = ['compliance', 'regulation', 'standard', 'fda', 'hipaa', 'gdpr']
    if any(keyword in text_lower for keyword in compliance_keywords):
        return 'compliance'
    
    # Default to functional
    return 'functional'


def extract_healthcare_concepts(text: str) -> Dict[str, List[str]]:
    """
    Extract healthcare-specific concepts from text
    
    Args:
        text: Input text
        
    Returns:
        Dictionary of healthcare concepts by category
    """
    concepts = {category: [] for category in HEALTHCARE_TERMS.keys()}
    text_lower = text.lower()
    
    for category, terms in HEALTHCARE_TERMS.items():
        for term in terms:
            if term in text_lower:
                concepts[category].append(term)
    
    return concepts


def calculate_complexity_score(text: str) -> int:
    """
    Calculate complexity score for a requirement (1-10 scale)
    
    Args:
        text: Requirement text
        
    Returns:
        Complexity score from 1 (simple) to 10 (very complex)
    """
    score = 1
    
    # Length-based scoring
    word_count = len(text.split())
    if word_count > 50:
        score += 3
    elif word_count > 30:
        score += 2
    elif word_count > 15:
        score += 1
    
    # Sentence complexity
    sentences = extract_sentences(text)
    if len(sentences) > 3:
        score += 2
    elif len(sentences) > 1:
        score += 1
    
    # Technical terms
    healthcare_concepts = extract_healthcare_concepts(text)
    total_concepts = sum(len(concepts) for concepts in healthcare_concepts.values())
    if total_concepts > 5:
        score += 2
    elif total_concepts > 2:
        score += 1
    
    # Modal verbs (multiple requirements in one)
    modal_count = sum(1 for verb in REQUIREMENT_PATTERNS['modal_verbs'] 
                     if re.search(r'\b' + verb + r'\b', text.lower()))
    if modal_count > 2:
        score += 2
    elif modal_count > 1:
        score += 1
    
    # Conditional statements
    conditionals = ['if', 'when', 'unless', 'provided that', 'in case']
    conditional_count = sum(1 for cond in conditionals if cond in text.lower())
    if conditional_count > 0:
        score += conditional_count
    
    return min(score, 10)  # Cap at 10


def extract_dependencies(text: str) -> List[str]:
    """
    Extract potential dependencies from requirement text
    
    Args:
        text: Requirement text
        
    Returns:
        List of potential dependencies
    """
    dependencies = []
    
    # Look for dependency patterns
    dependency_patterns = [
        r'depends on (.+?)(?=\.|,|$)',
        r'requires (.+?)(?=\.|,|$)',
        r'after (.+?)(?=\.|,|$)',
        r'before (.+?)(?=\.|,|$)',
        r'following (.+?)(?=\.|,|$)',
        r'based on (.+?)(?=\.|,|$)'
    ]
    
    for pattern in dependency_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dependency = match.group(1).strip()
            if dependency and len(dependency) > 3:
                dependencies.append(dependency)
    
    return dependencies


def normalize_requirement_text(text: str) -> str:
    """
    Normalize requirement text for better processing
    
    Args:
        text: Raw requirement text
        
    Returns:
        Normalized requirement text
    """
    # Clean the text
    text = clean_text(text)
    
    # Normalize common requirement phrases
    text = re.sub(r'\bshall\b', 'must', text, flags=re.IGNORECASE)
    text = re.sub(r'\bwill\b', 'must', text, flags=re.IGNORECASE)
    
    # Remove redundant words
    text = re.sub(r'\b(the system|the application|the software)\b', 'the system', text, flags=re.IGNORECASE)
    
    # Normalize spacing around punctuation
    text = re.sub(r'\s*([.,:;!?])\s*', r'\1 ', text)
    
    return text.strip()


def split_compound_requirements(text: str) -> List[str]:
    """
    Split compound requirements into individual requirements
    
    Args:
        text: Compound requirement text
        
    Returns:
        List of individual requirements
    """
    # Split on coordinating conjunctions that indicate separate requirements
    split_patterns = [
        r'\band\b',
        r'\bor\b',
        r'\bas well as\b',
        r'\bin addition\b',
        r'\bfurthermore\b',
        r'\bmoreover\b'
    ]
    
    requirements = [text]
    
    for pattern in split_patterns:
        new_requirements = []
        for req in requirements:
            parts = re.split(pattern, req, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Clean up each part
                for part in parts:
                    part = part.strip()
                    if len(part) > 10:  # Minimum length for a meaningful requirement
                        new_requirements.append(part)
            else:
                new_requirements.append(req)
        requirements = new_requirements
    
    return requirements


# Export main functions
__all__ = [
    'clean_text',
    'extract_sentences',
    'extract_keywords',
    'extract_entities',
    'identify_requirements',
    'classify_requirement_type',
    'extract_healthcare_concepts',
    'calculate_complexity_score',
    'extract_dependencies',
    'normalize_requirement_text',
    'split_compound_requirements'
]