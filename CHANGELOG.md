## 2.0.2
Adjust dependencies to use latest version of FastAPI
- Remove mathactive dependency
- Upgrade FastAPI version
- Upgrade Uvicorn version


## 2.0.1
Remove support for 'next' keyword
- Remove 'next' keyword tests
- Remove 'next' from approved keywords
- Upgrade mathtext to 2.0.2


## 2.0.0
Refactor endpoint to support V3 Rori content and technical needs
- Adjust endpoint evaluations to work with V3 Rori content
- Add /nlu/intent-recognition endpoint for keyword and intent evaluation
- Add asynchronous batch logging of endpoint request/response data
- Improve testing
- Support migration from GitLab to GitHub
- Support changing hosting environment to Google Cloud
- Add support for caching via Redis
- Reorganize project
- Remove conversation state management and generative quizzes


## [0.0.17](https://github.com/RisingAcademies/rori-mathtext-answers/tree/0.0.17)
Improve NLU capabilities and add generative quizzes
- Add keywords and improve handling of keywords
- Add mathactive and FSM quizzes
- Adjust simulated tests of endpoint evaluations


## [0.0.12](https://github.com/RisingAcademies/rori-mathtext-answers/tree/0.0.12)

Improve NLU capabilities
- Improved handling for integers (1), floats (1.0), and text numbers (one)
- Integrates fuzzy keyword matching for 'easier', 'exit', 'harder', 'hint', 'next', 'stop'
- Integrates intent classification for user messages
- Improved conversation management system
- Created a data-driven quiz prototype


## [0.0.0](https://github.com/RisingAcademies/rori-mathtext-answers/tree/0.0.0)

Initial release
- Basic text to integer NLU evaluation of user responses
- Basic sentiment analysis evaluation of user responses
- Prototype conversation manager using finite state machines
- Support for logging of user message data
