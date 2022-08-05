# CosIng-Toxicity
This project contains source code for research into the automation of literature reviews using Python and NLTK. The CosIng-Toxicity case study in particular uses data about cosmetic ingredients to search for research into their toxicity.

This project was carried out in collaboration with the **Kanazawa University Practical Pharmacology Laboratory**. The goal was to verify an automated literature review process using natural language processing (NLP).

The data for this project comes from the following resources:
- [Cosmetic ingredient database (Cosing) - Ingredients and Fragrance inventory](https://data.europa.eu/data/datasets/cosmetic-ingredient-database-ingredients-and-fragrance-inventory) for an inclusive list of cosmetic ingredients
- [PubChem PUG View web service](https://pubchemdocs.ncbi.nlm.nih.gov/pug-view) to collect data on each ingredient's therapeutic uses and toxicity
- [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/) to search research papers for adverse effects on skin related to each compound
- [Natural Language Toolkit (NLTK)](https://www.nltk.org/) to process the acquired paper abstracts for relevance

A presentation slideshow of this research is available on **Slideshare** at the link below.

**<a href="//www.slideshare.net/RobertSonger/a-natural-language-processing-approach-to-reviewing-research-abstracts" title="A Natural Language Processing Approach to Reviewing Research Abstracts" target="_blank">A Natural Language Processing Approach to Reviewing Research Abstracts</a>** from **<a href="//www.slideshare.net/RobertSonger" target="_blank">Robert Songer</a>**

> Research literature reviews have largely moved online and researchers must search through large quantities of digital documents to find research related to their academic pursuits. With recent developments in Natural Language Processing (NLP), computers can perform most of the searching and reduce the amount of time it takes researchers to find the papers they need. In this report, we introduce three basic NLP techniques (tokenization, frequency distributions, and in-sentence collocations) for searching the written texts of research abstracts downloaded from an online database. Real examples written in the Python programming language are provided along with a discussion of their efficacy in a project at Kanazawa University where an online research database was searched for research related to the adverse effects of hundreds of pharmaceutical compounds.
