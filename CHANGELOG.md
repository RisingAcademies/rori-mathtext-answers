
## [0.0.17](https://gitlab.com/tangibleai/community/mathtext-fastapi/-/tags/0.0.17)

Add error validation and logging and add NLU keyword detection
- Adds Sentry logging to the application
- Adds payload validation and error handling in the /nlu endpoint
- Integrates fuzzy keyword matching for all keywords in Rori stack, including 'easier', 'exit', 'harder', 'hint', 'next', 'stop', 'tired', 'tomorrow', 'finished', 'help', 'please', 'understand', 'question', 'easier', 'easy', 'support', 'skip', 'menu'


## [0.0.12](https://gitlab.com/tangibleai/community/mathtext-fastapi/-/tags/0.0.12)

Improve NLU capabilities
- Improved handling for integers (1), floats (1.0), and text numbers (one)
- Integrates fuzzy keyword matching for 'easier', 'exit', 'harder', 'hint', 'next', 'stop'
- Integrates intent classification for user messages
- Improved conversation management system
- Created a data-driven quiz prototype


## [0.0.0](https://gitlab.com/tangibleai/community/mathtext-fastapi/-/tags/0.0.0)

Initial release
- Basic text to integer NLU evaluation of user responses
- Basic sentiment analysis evaluation of user responses
- Prototype conversation manager using finite state machines
- Support for logging of user message data
