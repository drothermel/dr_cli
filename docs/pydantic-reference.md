# Pydantic Reference

## Core Features

### Automatic Validation
- Validates data at object instantiation
- Type annotations enforced at runtime
- Raises detailed, formatted errors for invalid data
- No manual validation methods required

### Type Coercion
- **Lax mode** (default): Automatically converts compatible types
  - `"123"` → `123`
  - `"true"` → `True`
- **Strict mode**: No type conversion, exact type matching required

### Performance
- Core validation logic written in Rust
- Among the fastest Python validation libraries
- ~8,000 packages on PyPI use Pydantic

## Comparison with Dataclasses

### Standard Dataclasses
```python
@dataclass
class User:
    name: str
    age: int
    # No automatic validation
    # Manual __post_init__ required for validation
    # No JSON serialization built-in
```

### Pydantic Models
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    # Automatic validation
    # Built-in JSON support
    # Type coercion
```

### Pydantic Dataclasses
```python
from pydantic.dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    # Drop-in replacement for stdlib dataclass
    # Adds Pydantic validation
    # Familiar dataclass syntax
```

## Validation Features

### Field Constraints
```python
from pydantic import Field

class Model(BaseModel):
    age: int = Field(gt=0, le=150)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    items: list[str] = Field(min_length=1, max_length=10)
```

### Custom Validators
```python
from pydantic import field_validator

class Model(BaseModel):
    name: str
    
    @field_validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Name too short')
        return v
```

## Serialization

### JSON Support
```python
model = User(name="John", age=30)
model.model_dump()         # → dict
model.model_dump_json()    # → JSON string
User.model_validate(data)  # dict → model
User.model_validate_json(json_str)  # JSON → model
```

### JSON Schema
```python
User.model_json_schema()   # Generates JSON Schema
```

## Error Format
```python
try:
    User(name="John", age="invalid")
except ValidationError as e:
    print(e.errors())
    # [
    #   {
    #     'type': 'int_parsing',
    #     'loc': ('age',),
    #     'msg': 'Input should be a valid integer',
    #     'input': 'invalid'
    #   }
    # ]
```

## Configuration

### Model Config
```python
class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip strings
        validate_assignment=True,    # Validate on attribute assignment
        extra='forbid'              # Forbid extra fields
    )
```

## Type Support

### Standard Library Types
- All standard types: `int`, `float`, `str`, `bool`, `list`, `dict`, `set`, `tuple`
- `datetime`, `date`, `time`, `timedelta`
- `UUID`, `Path`, `FilePath`, `DirectoryPath`
- `Enum`, `Literal`, `Union`, `Optional`
- `TypedDict`, `NamedTuple`

### Special Types
- `EmailStr`, `HttpUrl`, `IPvAnyAddress`
- `SecretStr`, `SecretBytes` (for sensitive data)
- `Json` (for JSON strings)
- `conint`, `constr`, `confloat` (constrained types)

## Performance Characteristics

### Memory Usage
- Pydantic: Higher memory overhead than dataclasses
- Dataclasses: Minimal overhead, especially with `slots=True` (Python 3.10+)

### Speed
- Validation: Pydantic faster than manual validation
- Instantiation: Dataclasses faster for simple object creation
- Serialization: Pydantic optimized for JSON operations

## Integration

### Popular Frameworks Using Pydantic
- FastAPI (web framework)
- LangChain (LLM framework)
- Hugging Face libraries
- SQLModel (SQL + Pydantic)
- Django Ninja

### API Design
- Automatic OpenAPI/Swagger documentation
- Request/response validation
- Settings management
- Configuration parsing