# config.py

# OOAD Vocabulary (for fuzzy fallback)
OOAD_VOCAB = {
    "uml", "unified", "modeling", "language", "diagram", "class", "sequence", "use", "case",
    "encapsulation", "bundling", "data", "methods", "class", "hides", "implementation", "interface",
    "inheritance", "parent", "child", "derives", "properties", "behavior",
    "polymorphism", "objects", "types", "treated", "common", "interface",
    "advantages", "communication", "visual", "simplifies", "complex", "systems",
    "error", "detection", "design", "flaws", "documentation", "code", "generation",
    "skeleton", "protects", "integrity", "unauthorized", "access", "reduces",
    "complexity", "abstraction", "enables", "modular", "maintainable",
    "example", "extends", "vehicle", "car", "start", "bike"
}

# Combined model answer (all 3 questions merged)
MODEL_ANSWER = (
    "UML Unified Modeling Language provides a standardized way to visualize system architecture and behavior. "
    "Advantages include improved communication, simplified complex systems using class sequence use case diagrams, "
    "early error detection, documentation support, and code generation. "
    "Encapsulation is the bundling of data and methods within a class, hiding implementation details and exposing only a public interface. "
    "It protects object integrity, reduces complexity through abstraction, and enables modular maintainable code. "
    "Inheritance allows a child class to derive properties and behavior from a parent class. "
    "Polymorphism allows objects of different types to be treated as instances of the same parent class through a common interface."
)

# Combined keywords for grading (union of all expected terms)
EXPECTED_KEYWORDS = {
    "uml", "unified", "modeling", "language", "communication", "visual", 
    "diagrams", "class", "sequence", "use", "case", "error", "detection", 
    "documentation", "code", "generation", "simplifies", "complex",
    "encapsulation", "bundling", "data", "methods", "hides", 
    "implementation", "interface", "protects", "integrity", "unauthorized", 
    "access", "reduces", "complexity", "abstraction", "modular", "maintainable",
    "inheritance", "parent", "child", "derives", "properties", "behavior", 
    "polymorphism", "objects", "types", "treated", "common", "example", "extends"
}