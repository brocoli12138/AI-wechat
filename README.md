# AI-WeChat Bot

An intelligent WeChat bot powered by large language models (LLM) that can automatically respond to messages from your friends.

## Features

- **LLM Integration**: Connects with OpenAI-compatible APIs to generate intelligent responses
- **Message Handling**: Processes various message types including text, voice, images, videos, and files
- **Context Management**: Maintains conversation history for more coherent interactions
- **Debounce Mechanism**: Prevents message flooding by implementing a debounce pool
- **Multi-Friend Support**: Listens to and responds to multiple friends simultaneously
- **Extensible Tools**: Supports custom tools that can be invoked by the LLM

## Prerequisites

- Python 3.8 or higher
- WeChat desktop application <= 3.9 (required for `wxauto` library)
- OpenAI-compatible API key and endpoint

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/AI-wechat.git
   cd AI-wechat
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirement.txt
   ```

3. Configure the environment:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your configuration:
     ```bash
     # OpenAI API settings
     OPENAI_KEY = your_openai_key
     OPENAI_ENDPOINT = your_openai_endpoint
     MODEL_NAME = your_model_name
     MODEL_TEMPERATURE = 1.0
     MODEL_TOP_P = 0.95
     
     # System prompt and tools
     SYSTEM_PROMPT_PATH = ./system_prompt.json
     TOOLS_DESCRIPTION_PATH = ./tools_descriptions.json
     TOOLS_IMPLEMENTATION_PATH = ./tools_implementations.py
     
     # Context management
     CONTEXT_WINDOW_LENGTH = 10
     CONTEXT_STAY_DURATION = 5
     CONTEXT_STORAGE_DIR = ./chat_history
     
     # Debounce settings
     DEBOUNCE_THRESHOLD = 10
     MAX_WAIT_DURAION = 10
     
     # File download directory
     FILE_DOWNLOAD_DIR = ./files

     # Information files LLM can send to friends
     INFO_FILES_DIRECTORY = ./files
     ```

4. Configure friends to listen to:
   - Edit `listen_friendname.txt` and add the WeChat names of friends you want the bot to respond to, one per line:
     ```
     Friend Name 1
     Friend Name 2
     File Transfer Assistant
     ```

## Usage

1. Make sure WeChat desktop application is running and logged in

2. Run the bot:
   ```bash
   python wechat_bot.py
   ```

3. The bot will start listening to messages from the friends specified in `listen_friendname.txt`

## Project Structure

```
AI-wechat/
├── wechat_bot.py          # Main bot class that orchestrates all components
├── wechat_client.py       # WeChat client using wxauto library
├── config.py              # Configuration loader
├── system_prompt.json     # System prompt for the LLM
├── tools_descriptions.json# Custom Tool descriptions for the LLM
├── tools_implementations.py# Custom Tool implementations
├── listen_friendname.txt  # List of friends to listen to
├── requirement.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── LLM/                   # LLM related modules
│   ├── responsor.py       # LLM response handler
│   └── debounce_pool.py   # Message debounce mechanism
├── context/               # Context management modules
│   ├── context_manager.py # Main context manager
│   ├── context_trimmer.py # Context trimming utilities
│   ├── file_manager.py    # File operations for context
│   └── storage_manager.py # Context storage management
├── tools/                 # Default tools for the bot
│   ├── tools_manager.py   # Tool management
│   ├── default_descriptions.json
│   └── default_implementations.py
└── tests/                 # Unit tests
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_KEY | Your OpenAI-compatible API key | - |
| OPENAI_ENDPOINT | Your OpenAI-compatible API endpoint | - |
| MODEL_NAME | Model name to use | - |
| MODEL_TEMPERATURE | Sampling temperature | 1.0 |
| MODEL_TOP_P | Nucleus sampling parameter | 0.95 |
| SYSTEM_PROMPT_PATH | Path to system prompt file | ./system_prompt.json |
| TOOLS_DESCRIPTION_PATH | Path to tools description file | ./tools_descriptions.json |
| TOOLS_IMPLEMENTATION_PATH | Path to tools implementation file | ./tools_implementations.py |
| CONTEXT_WINDOW_LENGTH | Number of messages to keep in context | 10 |
| CONTEXT_STAY_DURATION | Duration to keep context in memory (seconds) | - |
| CONTEXT_STORAGE_DIR | Directory to store chat history | ./chat_history |
| DEBOUNCE_THRESHOLD | Time threshold for message debouncing (seconds) | 10 |
| MAX_WAIT_DURAION | Maximum wait duration for messages (seconds) | 10 |
| FILE_DOWNLOAD_DIR | Directory to download received files | - |
| INFO_FILES_DIRECTORY | Information files LLM can send to friends | ./files |

## How It Works

1. **Message Reception**: The bot uses `wxauto` library to listen for messages from specified friends in WeChat
2. **Debouncing**: Messages are first sent to a debounce pool to prevent flooding
3. **Context Retrieval**: When processing a message, the bot retrieves conversation history from the context manager
4. **LLM Processing**: The message and context are sent to the LLM for response generation
5. **Response Sending**: The LLM's response is sent back to the user via WeChat
6. **Context Update**: Both the user's message and the bot's response are added to the conversation context

## Extending Functionality

### Adding Custom Tools

1. Define your tool in `tools_descriptions.json` following the format:
   ```json
   {
    "type": "function",
    "function": {
      "name": "tool_name",
      "description": "Description of what the tool does",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "Type of this parameter, ",
            "description": "Description of this parameter"
          }
        },
        "required": []
      }
    }
  }
   ```

2. Implement the tool in `tools_implementations.py`:
   ```python
   def tool_name(param1: Any, user_id: str):
       # YOU MUST ADD AN EXTRA PARAM HERE: user_id, a string, which is used to identify which friend the tool is working for. You can also use this user_id parameter in your implementation!
       # Implementation here
       return result
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. If you have any questions for it, do not hesitate sending me an e-mail, and I would be so happy to hear from all of you!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

### AI-wechat Project Comprehensive Disclaimer

**Version: 1.0**
**Effective Date: October 15, 2023**
**Publisher: AI-wechat Development Team**

---

#### **I. Purpose and Scope of the Disclaimer**
This disclaimer (hereinafter referred to as the “Disclaimer”) applies to all individuals, organizations, or entities (collectively referred to as “Users”) who access, download, install, use, or otherwise engage with the AI-wechat project in any capacity. AI-wechat is an open-source initiative designed exclusively for educational and research purposes, aiming to advance understanding of artificial intelligence within the context of instant messaging environments—encompassing fundamental principles, development workflows, and practical applications such as natural language processing and automated scripting. This Disclaimer does not constitute a legally binding agreement but serves as a foundational condition for project utilization. **By continuing to use any feature of this project, you expressly acknowledge that you have read, fully understood, and voluntarily agreed to comply with all terms herein.** Should you dissent from any part of this Disclaimer, please discontinue use immediately.

---

#### **II. Nature of the Project and Usage Restrictions**
1. **Strictly Educational Use Only**
   - The AI-wechat project is intended solely for non-commercial educational and academic pursuits, including but not limited to:
     - Personal skill development and self-directed learning (e.g., programming, AI algorithm experimentation);
     - Scholarly research (e.g., university course projects, thesis-related experiments);
     - Non-profit technological community engagement (e.g., open-source contributions, academic workshops).
   - **Prohibited Uses:** Users must not employ this project in the following contexts:
     - Commercial activities (e.g., corporate marketing, revenue-generating services);
     - Illegal conduct (e.g., dissemination of malware, cyber fraud, privacy violations);
     - Actions endangering national security, public order, or the rights of others (e.g., spreading misinformation, incitement to violence);
     - Any application violating WeChat platform policies or the laws and regulations of the People's Republic of China.
   - **Liability Notice:** Users bear sole responsibility for determining whether their activities remain within permissible educational boundaries. Should usage be deemed to extend beyond such scope (e.g., commercial deployment), the development team reserves the right to revoke access privileges, and users shall assume full legal consequences.

2. **Relationship with Third-Party Platforms**
   - The AI-WeChat project relies on Wechat, a service operated by Tencent Holdings Limited. **Notably, this project is neither an official WeChat product nor endorsed or authorized by Tencent.**
   - Users expressly acknowledge that changes to WeChat’s terms of service, policy updates, or technical limitations may adversely affect the functionality of this project (e.g., API deprecation, feature degradation). The development team assumes no obligation to explain, compensate for, or guarantee continuity against actions taken by the WeChat platform.

---

#### **III. User Responsibilities and Obligations**
As direct users of the project, individuals assume the following duties. Failure to uphold these obligations may result in legal exposure or termination of access:
1. **Compliance with Laws and Platform Policies**
   - Users must strictly adhere to:
     - National legislation including the *Cybersecurity Law*, *Data Security Law*, and *Personal Information Protection Law* of the People’s Republic of China;
     - WeChat's comprehensive terms, including the *Software License and Service Agreement*, *Official Account Operational Guidelines*, and *Personal Account Usage Policy*;
     - All applicable local laws in their jurisdiction (e.g., GDPR compliance for users in the European Union).
   - **Special Advisory:** In jurisdictions with specific restrictions on AI tools or cross-border data transfers (e.g., bans on unsanctioned automated messaging), users are responsible for ensuring full legal conformity.

2. **Responsible Content Management**
   - **All content generated, transmitted, or received via AI-WeChat on WeChat—including text, images, and hyperlinks—is the sole legal responsibility of the user.**
   - Users must ensure that all content:
     - Is lawful and does not infringe upon intellectual property rights, image rights, reputational rights, or other protected interests;
     - Is harmless and free from malicious elements such as computer viruses, phishing links, or executable exploits;
     - Upholds societal ethics and public order, avoiding politically sensitive, pornographic, abusive, or discriminatory expression.
   - **Assumption of Risk:** Consequences arising from content violations—such as WeChat account suspension, legal action, or third-party claims—shall be borne entirely by the user. The development team will not intervene in disputes.

3. **Data Security and Privacy Protection**
   - Users should refrain from processing highly sensitive personal data (e.g., national ID numbers, bank account details, biometric identifiers) through this project.
   - When utilizing functionalities involving data exchange, users must:
     - Obtain explicit, informed consent from data subjects in advance;
     - Employ encryption or other appropriate safeguards to protect data in transit and at rest;
     - Adhere to the principle of data minimization and avoid unnecessary or excessive data collection.
   - **Disclaimer of Liability:** The development team assumes no responsibility for data breaches, unauthorized modification, or loss resulting from user actions. Privacy incidents caused by improper usage fall outside the scope of protection.

---

#### **IV. Limitation of Liability for the Development Team**
The AI-wechat Development Team, including its members, contributors, and sponsors, hereby explicitly disclaims, to the fullest extent permitted by law, all express or implied liabilities, including but not limited to the following:
1. **Content Liability Waiver**
   - The team assumes no responsibility for monitoring, reviewing, guaranteeing, or bearing secondary liability for any messages sent, received, or stored via this project on WeChat. The authenticity, legality, and implications of such content rest entirely with the user.
   - While the team reserves the right to remove content that violates guidelines, such action shall not be construed as endorsement or assumption of liability.

2. **Technical and Service Exclusions**
   - **No Warranty of Performance:** As an open-source tool, the project may contain imperfections, bugs, or security vulnerabilities. The team makes no warranties regarding:
     - Continuous availability (e.g., interruptions due to GitHub outages or network issues);
     - Compatibility assurance (e.g., malfunction following WeChat app updates);
     - Immunity from malware, hacking attempts, or external interference.
   - **Exclusion of Indirect Damages:** Under no circumstances shall the team be liable for any direct, indirect, incidental, or consequential damages arising from project use, including but not limited to data loss, business interruption, financial loss, or reputational harm.

3. **Third-Party Dependencies**
   - Services such as WeChat APIs, hosting providers, and open-source libraries operate independently of this project. The team assumes no liability for:
     - Policy modifications or discontinuation of WeChat API access;
     - Risks cascading from third-party service failures (e.g., endpoint outages);
     - Disputes between users and third parties arising from reliance on this project.

4. **Liability Cap**
   - In no event shall the team’s aggregate liability exceed the actual fees paid by the user for using the project (noting that the project is provided at no cost, rendering the maximum liability nil). This limitation does not apply where prohibited by law, such as in cases of gross negligence, intentional misconduct, or personal injury.

---

#### **V. Intellectual Property and Usage Guidelines**
1. **Ownership and Rights**
   - All source code, documentation, trademarks, and associated materials related to AI-WeChat are the sole property of the development team and protected under the *Copyright Law of the People's Republic of China*.
   - Users may use and modify the code in accordance with the terms of the [MIT Open Source License](https://opensource.org/licenses/MIT), provided that they do not claim the project as their own original creation or seek patent protection over derivative works.

2. **Prohibited Conduct**
   - Users must not:
     - Reverse-engineer or decompile the core logic for integration into commercial products;
     - Represent or imply endorsement by the development team for external services;
     - Deploy the project for automated mass messaging, traffic inflation, or other activities that contravene WeChat’s operational rules.

---

#### **VI. Risk Warnings and User Advisories**
1. **Enumerated Risks**
   - **Technical Risks:** The AI model may generate inaccurate, misleading, or inappropriate outputs due to inherent limitations; human oversight and verification are imperative.
   - **Legal Risks:** Regulatory frameworks governing AI vary globally (e.g., China’s *Interim Measures for the Management of Generative AI Services*); users are responsible for maintaining ongoing compliance.
   - **Security Risks:** Open-source software may be vulnerable to tampering; users are strongly advised to obtain the project exclusively from the [official GitHub repository](https://github.com/AI-wechat).
   - **Ethical Risks:** Misuse of AI may erode social trust; users are encouraged to act in accordance with the principle of *technology for good*.

2. **Recommended Practices**
   - Regularly review updates to WeChat’s service terms;
   - Conduct small-scale trials before executing high-impact operations (e.g., bulk messaging);
   - Maintain detailed usage logs to support accountability in case of disputes.

---

#### **VIII. Contact Information**
For inquiries, suggestions, or issue reports regarding this Disclaimer, please reach out via:
- **Official Email:** brocoli12138@gmail.com
- **GitHub Issues:** [Submit a Ticket](https://github.com/ai-wechat/project/issues)
- **Response Time:** All valid submissions will be acknowledged within five (5) business days.

---

### **Critical Acknowledgment**
**Your continued use of the AI-wechat project constitutes irrevocable affirmation that you:**
- Fully comprehend the boundaries of permissible educational use and your attendant responsibilities;
- Commit to abiding by WeChat’s policies and all applicable national laws;
- Clearly recognize the scope of the development team’s disclaimers and voluntarily accept all associated risks.

**With innovation comes accountability. Use this tool wisely—its potential lies not only in advancement, but in ethical stewardship.**

> *The AI-WeChat Development Team remains dedicated to promoting accessible AI education. However, safety and compliance are shared responsibilities. The final interpretation of this Disclaimer rests solely with the AI-wechat Development Team.*
> **Download or use of the project signifies unconditional acceptance of all terms herein.**