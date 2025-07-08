### Dependencies

The project requires the following Python packages:
- `pydantic` - Data validation
- `pycountry` - Country and currency data
- `babel` - Internationalization support
- `num2words` - Number to words conversion
- `roman` - Roman numeral processing
- `python-dateutil` - Date parsing
- `indic-numtowords` - Indian language number conversion
- `unicodedata` - Unicode normalization

## Usage

### Basic Usage

```python
import sys 
sys.path.append("<path_to_repo>")
from preprocesor import OrpheusTextNormalizer

# Initialize the normalizer
normalizer = OrpheusTextNormalizer()

# Process text
text = "The meeting is on 15th March 2024 at 2:30 PM. Call me at +91-98765-43210."
result = normalizer.process_text(text, to_lang="en")

print(result.formatted_text)
# Output: "The meeting is on fifteenth March two thousand and twenty four at two thirty p m. Call me at plus nine one nine eight seven six five four three two one zero."

print(result.replaced_entities)
# Output: List of tuples containing (original_text, replaced_text, entity_type)
```

### Multi-language Support

```python
# Hindi processing
hindi_text = "मैं १५ मार्च २०२४ को ₹५००० कमाऊंगा"
result = normalizer.process_text(hindi_text, to_lang="hi")

# Tamil processing
tamil_text = "நான் மார்ச் 15, 2024 அன்று ₹5000 சம்பாதிப்பேன்"
result = normalizer.process_text(tamil_text, to_lang="ta")
```

### Entity Types

The library processes the following entity types:

- `DATE` - Date expressions
- `TIME` - Time and duration expressions
- `CURRENCY` - Currency amounts
- `NUM_WITH_WORDS` - Numbers with commas
- `PHONE_NUMBERS` - Phone numbers
- `DECIMAL` - Decimal numbers
- `ORDINAL` - Ordinal numbers (1st, 2nd, etc.)
- `VEHICLE_NUMBER` - Vehicle registration numbers
- `ALPHANUMERICS` - Alphanumeric codes
- `NON_COMMA_NUMBERS` - Numbers without commas (PIN codes, years)
- `ACRONYMS_READ_OUT` - Acronyms and abbreviations

## API Reference

### OrpheusTextNormalizer

Main class for text normalization.

#### Methods

##### `process_text(text: str, to_lang: str = "en") -> DeterministicPreTTSPreprocessingResponse`

Processes input text and converts entities to spoken format.

**Parameters:**
- `text` (str): Input text to process
- `to_lang` (str): Target language code (default: "en")

**Returns:**
- `DeterministicPreTTSPreprocessingResponse`: Object containing:
  - `formatted_text` (str): Processed text
  - `replaced_entities` (list): List of tuples (original, replaced, entity_type)

### OrpheusTextCleaner

Text cleaning utility class.

#### Methods

##### `__call__(text: str) -> str`

Cleans and normalizes text.

## Supported Languages

| Language | Code | Number System | Features |
|----------|------|---------------|----------|
| English | `en` | Arabic | Full support |
| Hindi | `hi` | Devanagari | Full support |
| Tamil | `ta` | Tamil | Full support |
| Telugu | `te` | Telugu | Full support |
| Malayalam | `ml` | Malayalam | Full support |
| Kannada | `kn` | Kannada | Full support |
| Marathi | `mr` | Devanagari | Full support |
| Gujarati | `gu` | Gujarati | Full support |
| Odia | `or` | Odia | Full support |
| Bengali | `bn` | Bengali | Full support |
| Punjabi | `pa` | Gurmukhi | Full support |

## Examples

### Date Processing
```python
# Input: "15/03/2024"
# Output: "fifteenth March two thousand and twenty four"

# Input: "March 15th, 2024"
# Output: "March fifteenth two thousand and twenty four"
```

### Currency Processing
```python
# Input: "₹50,000"
# Output: "fifty thousand rupees"

# Input: "USD 1.5M"
# Output: "one million five hundred thousand US dollars"
```

### Phone Number Processing
```python
# Input: "+91-98765-43210"
# Output: "plus nine one nine eight seven six five four three two one zero"
```

### Vehicle Number Processing
```python
# Input: "KA 05 AB 1234"
# Output: "K A, zero five, A B, one two three four"
```
