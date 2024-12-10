# Tnufa Auto

Implementation of the speech-to-grant product of Catalyzator for the Tnufa Grant.

## Thought model

We have a structured data model and information about the grant.
Additionally, we create a vector database for the innovator's profile.

We then create a structured output of the answers to the questions using a RAG approach on the innovator's profile database.

We use a templated prompt to generate the answers to the questions.
The prompt is composed of the grant information, the question and the extracted and augmented information from the innovator's profile database.

## Current state of the project

- The flow is implemented and the LLM client is working.
- The innovator's profile database and the profile provider are not implemented yet.
- The prompt building is there and will be improved if needed.
- We need to implement the database population.
- We need to implement an update flow for cases where
    - the innovator's profile is updated.
    - the grant is updated.
    - there are comments and suggestions for the answers.
