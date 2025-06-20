# Information Distribution Approach

This document outlines the decision framework for organizing and distributing technical learnings across documentation.

## Core Principle: Right Information in the Right Place

Each piece of information should have a single, logical home based on its nature and intended audience.

## Document Types and Their Purposes

### 1. Retrospective Documents (`docs/completed-plans/*-retrospective.md`)
**Purpose**: Preserve complete implementation context and story
**Audience**: Future implementers, knowledge miners
**Content**:
- Full implementation narrative
- Detailed technical discoveries
- Problems encountered and solutions
- Timeline and commit history
- Unfiltered learnings and reflections

### 2. Reference Documents (`docs/*-reference.md`)
**Purpose**: Provide reusable, generalized knowledge
**Audience**: Developers facing similar problems
**Content**:
- Extracted patterns and best practices
- Common pitfalls and solutions
- Code examples and templates
- Quick lookup information
- Cross-domain applicable knowledge

### 3. Project Documentation (`README.md`)
**Purpose**: Help users understand and use the project
**Audience**: Library users, API consumers
**Content**:
- Installation and setup
- API documentation
- Usage examples
- Feature overview
- Quick start guides

### 4. Development Guidelines (`CLAUDE.md`)
**Purpose**: Guide future development on this project
**Audience**: Contributors, AI assistants, maintainers
**Content**:
- Project-specific patterns
- Architecture decisions
- Development workflow
- Testing strategies
- Commit conventions

### 5. Tool-Specific References (`docs/{tool}-reference.md`)
**Purpose**: Deep knowledge about specific tools
**Audience**: Developers using that tool
**Content**:
- Tool-specific patterns
- Integration strategies
- Common issues and workarounds
- Version-specific information
- Advanced usage patterns

## Decision Framework

### Step 1: Categorize the Information

Ask these questions:
1. **Is it specific to this implementation?** → Retrospective
2. **Is it a reusable pattern?** → Reference document
3. **Do users need it to use the code?** → README
4. **Is it about how to develop this project?** → CLAUDE.md
5. **Is it deep knowledge about a specific tool?** → Tool reference

### Step 2: Determine Generalizability

| Specificity Level | Document Type | Example |
|------------------|---------------|---------|
| Project-specific implementation details | Retrospective | "We chose 6 commits for phases 3-4" |
| Project-specific patterns | Project CLAUDE.md | "Run lint_fix before commits" |
| Domain patterns (e.g., parsing) | Domain reference | "Use match.groupdict() for safety" |
| Tool-specific knowledge | Tool reference | "Mypy note patterns never have error codes" |
| Universal patterns | General reference | "Walrus operator improves readability" |

### Step 3: Consider the Audience Journey

Users typically follow this path:
1. **README** - "How do I use this?"
2. **API docs** - "What can it do?"
3. **References** - "How do I solve specific problems?"
4. **CLAUDE.md** - "How do I contribute?"
5. **Retrospectives** - "Why was it built this way?"

Place information where users will naturally look for it.

### Step 4: Apply the DRY Principle

- Each concept should have ONE authoritative location
- Other documents should link to it, not duplicate it
- Use cross-references liberally
- Summaries are OK, full duplications are not

## Information Distribution Patterns

### Pattern 1: Extraction and Elevation
```
Retrospective (specific story)
    ↓ Extract patterns
Reference Doc (generalized knowledge)
    ↓ Link back
Retrospective (for full context)
```

### Pattern 2: Hub and Spoke
```
Tool Reference (central knowledge)
    ← Link from README (usage)
    ← Link from CLAUDE.md (development)
    ← Link from Retrospective (implementation)
```

### Pattern 3: Progressive Disclosure
```
README (quick start)
    → Reference (detailed patterns)
    → Retrospective (full story)
```

## Anti-Patterns to Avoid

1. **Scattering**: Don't spread related information across many documents
2. **Duplication**: Don't copy-paste the same content in multiple places
3. **Wrong Audience**: Don't put user docs in developer guides
4. **Over-Nesting**: Don't create deep hierarchies that hide information
5. **Under-Documenting**: Don't assume knowledge; err on the side of clarity

## Maintenance Guidelines

1. **Regular Reviews**: Check for outdated information quarterly
2. **Update Together**: When changing code, update all related docs
3. **Preserve History**: Never delete retrospectives; they're historical records
4. **Refactor Thoughtfully**: Consolidate similar references over time
5. **Listen to Users**: If people can't find info, reorganize

## Example Application

From the parser implementation:

1. **Full story with timeline** → `parser-implementation-retrospective.md`
2. **Regex safety patterns** → `regex-reference.md`
3. **General parsing patterns** → `parsing-patterns-reference.md`
4. **API usage** → `README.md`
5. **Mypy-specific parsing** → `mypy-reference.md`
6. **Project patterns** → `CLAUDE.md`

Each document serves its purpose without duplication, creating a comprehensive knowledge system.