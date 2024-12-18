# Tnufa Auto

Implementation of the speech-to-grant product of Catalyzator for the Tnufa Grant.

## Thought model

We have a structured data model and information about the grant.
Additionally, we create a vector database for the innovator's profile.

We then create a structured output of the answers to the questions using a RAG approach on the innovator's profile database.

We use a templated prompt to generate the answers to the questions.
The prompt is composed of the grant information, the question and the extracted and augmented information from the innovator's profile database.

## Current state of the project

- implement validity agent
- The flow is implemented and the LLM client is working.
- The innovator's profile database and the profile provider are not implemented yet.
- The prompt building is there and will be improved if needed.
    - more focus and guidance on technological innovation.
- We need to implement the database population.
- We need to implement the critique agent.
- We need to implement an update flow for cases where
    - the innovator's profile is updated.
    - the grant is updated.
    - there are comments and suggestions for the answers.

## Grant Extraction Process

We are currently extracting the grant questions and information semi-manually.
Some important insights of the semi-manual process to know when implementing the automated extraction:

- Using claude is much better than using gpt
- Instructing to follow structure and schema is crucial
- Instructing to use markdown following the schema is much better than using a JSON structure as output
- Allow multiple iterations as the response is very long

The meaning of those insights is the need to implement a markdown <-> JSON converter.
