<a id="readme-top"></a>
<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/shafiqninaba/gov-seek">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">GovSeek</h3>

  <p align="center">
    POC for a RAG-based chatbot for government services
    <br />
    <a href="https://gov-seek-e2a21ca71a09.herokuapp.com/">View Demo</a> (message me on <a href="https://linkedin.com/in/shafiq-ninaba">LinkedIn</a> for login password)
    <br>
    <a href="https://github.com/shafiqninaba/gov-seek/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/shafiqninaba/gov-seek/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

### Built With

* [![Python][Python-img]][Python-url]
* [![uv][uv-img]][uv-url]
* [![LangChain][LangChain-img]][LangChain-url]
* [![OpenAI][openai-img]][openai-url]
* <a href="https://qdrant.tech/"><img src="https://raw.githubusercontent.com/qdrant/qdrant/master/docs/logo.svg" alt="Qdrant" width="80" height="24" style="vertical-align:middle"></a>


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

This is a personal project to demonstrate the use of Retrieval-Augmented Generation (RAG) for a chatbot that helps users find more information about anything found in https://www.gov.sg/trusted-sites. The chatbot is built using LangChain, OpenAI's GPT-4o-mini for the chat model and Qdrant for the vector store. The chatbot is hosted on Heroku and can be accessed [here](https://gov-seek-e2a21ca71a09.herokuapp.com/). The chatbot is password-protected, so please message me on [LinkedIn](https://linkedin.com/in/shafiq-ninaba) for the password.

###

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/shafiqninaba/gov-seek.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin shafiqninaba/gov-seek
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Top contributors:

<a href="https://github.com/shafiqninaba/gov-seek/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=shafiqninaba/gov-seek" alt="contrib.rocks image" />
</a>

<!-- CONTACT -->
## Contact

Shafiq Ninaba | shafiqninaba@gmail.com | [LinkedIn](https://linkedin.com/in/shafiq-ninaba)

Project Link: [https://github.com/shafiqninaba/gov-seek](https://github.com/shafiqninaba/gov-seek)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/shafiqninaba/gov-seek.svg?style=for-the-badge
[contributors-url]: https://github.com/shafiqninaba/gov-seek/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/shafiqninaba/gov-seek.svg?style=for-the-badge
[forks-url]: https://github.com/shafiqninaba/gov-seek/network/members
[stars-shield]: https://img.shields.io/github/stars/shafiqninaba/gov-seek.svg?style=for-the-badge
[stars-url]: https://github.com/shafiqninaba/gov-seek/stargazers
[issues-shield]: https://img.shields.io/github/issues/shafiqninaba/gov-seek.svg?style=for-the-badge
[issues-url]: https://github.com/shafiqninaba/gov-seek/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/shafiq-ninaba
[product-screenshot]: images/screenshot.png
[LangChain-img]: https://img.shields.io/badge/LangChain-ffffff?logo=langchain&logoColor=green
[LangChain-url]: https://www.langchain.com/
[Python-img]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[uv-img]: https://img.shields.io/badge/uv-package%20manager-blueviolet
[uv-url]: https://docs.astral.sh/uv/
[openai-img]: https://shields.io/badge/-OpenAI-93f6ef?logo=openai
[openai-url]: https://platform.openai.com/
