# Your Personal Productivity GURU

This project is aimed at making the ultimate NOTION Personal Assistant. 
## CURRENT STATE: 3
### Stage 1:
* understanding how agentic AI interact with the user by making a simle todo database in notion and writing scripts to prompt LLMs to handle task scheduling for the user.

Features
* Handeling updateing and creatig task
* understanding user needs and scheduling tasks accordingly

Currently the whole project is running locally. In stage 2 it will have a better more interactive NOTION UI.
### Stage 2:
- Integrate with Thomans franks Ultimate task manager
    * [x] Needs to handle different projects
    * [x] access all the sub pages 
- [] adding markdown like text and images to tasks for more information 
    FEATURES
    - [x] the agent shold be exposed to minimal information and should use the tools to explore the pages (token usage optimization)
     * [x] methods to handle this exploration: recursive function keep calling wherever more information is requested
    - [x] every callout is a direct input to the llm. it serves as a interface. scrape for it to send it to llm
    - [x] quotes are for the llm to post general information and reply to user
    TOOLS
    - [x] create and fetch functions for within the project
    - [x] update functions for all
    - [x] access the projects and a brief description
### Stage 3 
- [] integrateing a local LLM for unristricted usage
    * might be slow (no gpu)
- [] customise the UI 
- [] use mem0ai for memory and context management
- [] start using tools like langchain

