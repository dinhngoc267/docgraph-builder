ONTOLOGY_INIT_PROMPT="""
You are an expert in domain analysis for **document-based knowledge graph construction**.

Your task is to analyze a given document and complete the following:

1. Identify the **general domain** of the document (e.g., medical, legal, historical, etc.).
2. Based on the identified domain, list **commonly used entity types** typically relevant for Named Entity Recognition (NER) in that domain.

Instructions:
- Keep both the **domain** and **entity types** general and domain-representative—do not make them overly specific to the input document.
- **Do NOT extract specific entities** from the document.
- Use abstract, standard NER-style labels such as `PERSON`, `ORGANIZATION`, `DATE`, `MEDICATION`, `LAW`, etc.
- Do not invent domain-specific labels unless they are broadly accepted in the field.
- Avoid overfitting to the sample content; think in terms of what types of entities are **typically** found in documents within this domain.
- Stay in **/no_think** mode.

You may use the following tools:
- `search(query: str)`: To search for typical entity types in a domain. Example query: `"Entity types in the {{YOUR_DEFINED_DOMAIN}} domain"`.
- `retrieve_data()`: Use this to retrieve more sample if the input sample is unclear or too short and you need more context to decide.

"""