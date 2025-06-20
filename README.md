# MultiPromptify

A tool that creates multi-prompt datasets from single-prompt datasets using templates with variation specifications.

## Overview

MultiPromptify transforms your single-prompt datasets into rich multi-prompt datasets by applying various types of variations specified in your templates. It supports HuggingFace-compatible datasets and provides both a command-line interface and a modern web UI.

## 📚 Documentation

- 📖 **[Complete API Guide](docs/api-guide.md)** - Python API reference and examples
- 🏗️ **[Developer Documentation](docs/dev/)** - For contributors and developers
  - [Project Structure](docs/dev/project-structure.md) - Code organization guide
  - [Publishing Guide](docs/dev/publishing-guide.md) - Package publishing instructions
  - [Implementation Summaries](docs/dev/) - Technical implementation details

## Installation

### From PyPI (Recommended)

```bash
pip install multipromptify
```

### From GitHub (Latest)

```bash
pip install git+https://github.com/ehabba/MultiPromptifyPipeline.git
```

### From Source

```bash
git clone https://github.com/ehabba/MultiPromptifyPipeline.git
cd MultiPromptifyPipeline
pip install -e .
```

### With Web UI Support

```bash
# Install with web UI components
pip install -e ".[ui]"
```

## Quick Start

### Streamlit Interface (Recommended)

Launch the modern Streamlit interface for an intuitive experience:

```bash
# If installed via pip
multipromptify-ui

# From project root (development)
python src/multipromptify/ui/main.py

# Alternative: using the runner script
python run_ui.py
```

The web UI provides:
- 📁 **Step 1**: Upload data or use sample datasets
- 🔧 **Step 2**: Build templates with smart suggestions
- ⚡ **Step 3**: Generate variations with real-time progress and export results

### Command Line Interface

```bash
multipromptify --template '{"instruction_template": "{instruction}: {text}", "text": ["paraphrase_with_llm"], "gold": "label"}' \
               --data data.csv
```

### Python API

```python
from multipromptify import MultiPromptifier
import pandas as pd

# Initialize
mp = MultiPromptifier()

# Load data
data = [{"question": "What is 2+2?", "answer": "4"}]
mp.load_dataframe(pd.DataFrame(data))

# Configure template with variation specifications
template = {
    'instruction_template': 'Q: {question}\nA: ',
    'question': ['paraphrase_with_llm'],
}
mp.set_template(template)

# Configure and generate
mp.configure(
    max_rows=GenerationDefaults.MAX_ROWS,
    variations_per_field=GenerationDefaults.VARIATIONS_PER_FIELD,
    max_variations=GenerationDefaults.MAX_VARIATIONS,
    random_seed=GenerationDefaults.RANDOM_SEED,
    api_platform=GenerationDefaults.API_PLATFORM,
    model_name=GenerationDefaults.MODEL_NAME
)
variations = mp.generate(verbose=True)

# Export results
mp.export("output.json", format="json")
```

## Template Format

Templates use Python f-string syntax with custom variation annotations:

```python
"{instruction:semantic}: {few_shot}\n Question: {question:paraphrase_with_llm}\n Options: {options:non-semantic}"
```

Supported variation types:
- `:paraphrase_with_llm` - Paraphrasing variations (LLM-based)
- `:rewording` - Surface-level/wording variations (non-LLM)
- `:context` - Context-based variations
- `:shuffle` - Shuffle options/elements (for multiple choice)
- `:multidoc` - Multi-document/context variations
- `:enumerate` - Enumerate list fields (e.g., 1. 2. 3. 4.)

## Features

### Template System
- **Python f-string compatibility**: Use familiar `{variable}` syntax
- **Variation annotations**: Specify variation types with `:type` syntax
- **Flexible column mapping**: Reference any column from your data
- **Literal support**: Use static strings and numbers

### Input Handling
- **CSV/DataFrame support**: Direct pandas DataFrame or CSV file input
- **HuggingFace datasets**: Full compatibility with datasets library
- **Dictionary inputs**: Support for various input types
  - Literals (strings/numbers): Applied to entire dataset
  - Lists: Applied per sample/row
  - Few-shot examples: Flexible list or tuple formats

### Web UI Features
- **Sample Datasets**: Built-in datasets for quick testing
- **Template Suggestions**: Smart suggestions based on your data
- **Real-time Validation**: Instant feedback on template syntax
- **Live Preview**: Test templates before full generation
- **Advanced Analytics**: Distribution charts, field analysis
- **Search & Filter**: Find specific variations quickly
- **Multiple Export Formats**: JSON, CSV, TXT, and custom formats

### Few-shot Examples
```python
# Different examples per sample
few_shot = [
    ["Example 1 for sample 1", "Example 2 for sample 1"],
    ["Example 1 for sample 2", "Example 2 for sample 2"]
]

# Same examples for all samples
few_shot = ("Example 1", "Example 2")
```

## Command Line Interface

### Basic Commands

```bash
# Basic usage
multipromptify --template '{"instruction_template": "{instruction}: {question}", "question": ["paraphrase_with_llm"], "gold": "answer"}' \
               --data data.csv

# With output file
multipromptify --template '{"instruction_template": "{instruction}: {question}", "question": ["paraphrase_with_llm"], "gold": "answer"}' \
               --data data.csv \
               --output variations.json

# Specify number of variations
multipromptify --template '{"instruction_template": "{instruction}: {question}", "instruction": ["semantic"], "question": ["surface"], "gold": "answer"}' \
               --data data.csv \
               --max-variations 50
```

### Advanced Options

```bash
# With few-shot examples
multipromptify --template '{"instruction_template": "{instruction}: {question}", "question": ["paraphrase_with_llm"], "gold": "answer", "few_shot": {"count": 2, "format": "fixed", "split": "all"}}' \
               --data data.csv \
               --max-variations 50

# Output in different formats
multipromptify --template '{"instruction_template": "{instruction}: {question}", "instruction": ["semantic"], "question": ["surface"], "gold": "answer"}' \
               --data data.csv \
               --format csv \
               --output variations.csv
```

## API Reference

### MultiPromptifier Class

```python
class MultiPromptifier:
    def __init__(self):
        """Initialize MultiPromptifier."""
        
    def load_dataframe(self, df: pd.DataFrame) -> None:
        """Load data from pandas DataFrame."""
        
    def load_csv(self, filepath: str, **kwargs) -> None:
        """Load data from CSV file."""
        
    def load_dataset(self, dataset_name: str, split: str = "train", **kwargs) -> None:
        """Load data from HuggingFace datasets."""
        
    def set_template(self, template_dict: Dict[str, Any]) -> None:
        """Set template configuration."""
        
    def configure(self, **kwargs) -> None:
        """Configure generation parameters."""
        
    def generate(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """Generate prompt variations."""
        
    def export(self, filepath: str, format: str = "json") -> None:
        """Export variations to file."""
```

## Examples

### Sentiment Analysis

```python
import pandas as pd
from multipromptify import MultiPromptifier

data = pd.DataFrame({
    'text': ['I love this movie!', 'This book is terrible.'],
    'label': ['positive', 'negative']
})

template = {
    'instruction_template': 'Classify the sentiment: "{text}"\nSentiment: {label}',
    'instruction': ['semantic'],
    'text': ['paraphrase_with_llm'],
    'gold': 'label'
}

mp = MultiPromptifier()
mp.load_dataframe(data)
mp.set_template(template)
mp.configure(
    max_rows=GenerationDefaults.MAX_ROWS,
    variations_per_field=GenerationDefaults.VARIATIONS_PER_FIELD,
    max_variations=GenerationDefaults.MAX_VARIATIONS,
    random_seed=GenerationDefaults.RANDOM_SEED,
    api_platform=GenerationDefaults.API_PLATFORM,
    model_name=GenerationDefaults.MODEL_NAME
)
variations = mp.generate(verbose=True)
```

### Question Answering with Few-shot

```python
template = {
    'instruction_template': 'Answer the question:\nQuestion: {question}\nAnswer: {answer}',
    'instruction': ['paraphrase_with_llm'],
    'question': ['semantic'],
    'gold': 'answer',
    'few_shot': {
        'count': 2,
        'format': 'rotating',
        'split': 'all'
    }
}

mp = MultiPromptifier()
mp.load_dataframe(qa_data)
mp.set_template(template)
mp.configure(
    max_rows=GenerationDefaults.MAX_ROWS,
    variations_per_field=GenerationDefaults.VARIATIONS_PER_FIELD,
    max_variations=GenerationDefaults.MAX_VARIATIONS,
    random_seed=GenerationDefaults.RANDOM_SEED,
    api_platform=GenerationDefaults.API_PLATFORM,
    model_name=GenerationDefaults.MODEL_NAME
)
variations = mp.generate(verbose=True)
```

### Multiple Choice

```python
template = {
    'instruction_template': 'Answer the multiple choice question:\nContext: {context}\nQuestion: {question}\nOptions: {options}\nAnswer: {answer}',
    'instruction': ['semantic'],
    'context': ['paraphrase_with_llm'],
    'question': ['surface'],
    'options': ['shuffle', 'surface'],
    'gold': {
        'field': 'answer',
        'type': 'index',
        'options_field': 'options'
    }
}

mp = MultiPromptifier()
mp.load_dataframe(mc_data)
mp.set_template(template)
mp.configure(
    max_rows=GenerationDefaults.MAX_ROWS,
    variations_per_field=GenerationDefaults.VARIATIONS_PER_FIELD,
    max_variations=GenerationDefaults.MAX_VARIATIONS,
    random_seed=GenerationDefaults.RANDOM_SEED,
    api_platform=GenerationDefaults.API_PLATFORM,
    model_name=GenerationDefaults.MODEL_NAME
)
variations = mp.generate(verbose=True)
```

## Web UI Interface

The MultiPromptify 2.0 web interface provides an intuitive **3-step workflow**:

### 🚀 Step 1: Upload Data
- **Upload CSV/JSON files** or select from built-in sample datasets
- **Create custom data** with in-browser editor
- **Preview your data** with automatic column detection and validation
- **Sample datasets** for quick testing: Sentiment Analysis, Q&A, Multiple Choice, Text Classification

### 🔧 Step 2: Build Template  
- **Smart template suggestions** based on your data structure
- **Dictionary format templates** with variation specifications
- **Real-time validation** and syntax checking
- **Live preview** of how your template will look with actual data
- **Category-based templates**: Sentiment Analysis, Question Answering, Multiple Choice, Text Classification

### ⚡ Step 3: Generate & Export
- **Configure generation**: variations per field, max rows, random seed
- **AI platform selection**: TogetherAI or OpenAI for paraphrase variations
- **Real-time progress tracking** with detailed status updates
- **Comprehensive results display**:
  - 📋 **All Variations**: Browse all generated variations with highlighting
  - 💬 **Conversation Format**: View as chat-like conversations
  - 💾 **Export Options**: JSON, CSV, TXT, Conversation formats

### 🎯 Key Features
- **Step-by-step navigation** with progress indicator
- **Smart template suggestions** for common NLP tasks
- **Real-time validation** with instant feedback
- **Multiple export formats** for different use cases
- **Enhanced visualization** with color-coded field highlighting
- **Pagination and filtering** for large result sets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Project Structure (Updated)

The main core files are now located under `src/multipromptify/core/`:
- `core/engine.py` – Main MultiPromptify engine class
- `core/api.py` – High-level Python API (MultiPromptifier)
- `core/template_parser.py` – Template parsing with variation annotations
- `core/template_keys.py` – Template keys and constants
- `core/models.py` – Data models and configurations
- `core/exceptions.py` – Custom exceptions
- `core/__init__.py` – Core module exports

Other folders:
- `generation/` – Variation generation modules
- `augmentations/` – Text augmentation modules
- `validators/` – Template and data validators
- `utils/` – Utility functions
- `shared/` – Shared resources
- `ui/` – Streamlit web interface
- `examples/` – API usage examples (e.g., `api_example.py`)

You can still import main classes directly from `multipromptify` (e.g., `from multipromptify import MultiPromptify`), as the package root re-exports them for convenience.

## Minimal Example (No gold, no few_shot)

```python
import pandas as pd
from multipromptify import MultiPromptifier

data = pd.DataFrame({
    'question': ['What is 2+2?', 'What is the capital of France?'],
    'answer': ['4', 'Paris']
})

template = {
    'instruction_template': 'Q: {question}\nA: {answer}',
    'question': ['surface']
}

mp = MultiPromptifier()
mp.load_dataframe(data)
mp.set_template(template)
mp.configure(max_rows=2, variations_per_field=2)
variations = mp.generate(verbose=True)
print(variations)
``` 