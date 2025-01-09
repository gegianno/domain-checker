# Domain Availability Checker

A Python script that checks the availability of multiple domain names using the WHOIS protocol.

## Installation

1. Clone this repository or download the files
2. Install the required dependency:

```bash
pip install -r requirements.txt
```

## Usage

There are three ways to check domain availability:

### 1. Command Line Arguments

Check multiple domains by passing them as arguments:

```bash
python main.py example.com mydomain.org another-domain.com
```

### 2. Text File Input

Create a text file with one domain per line:

```text
example.com
mydomain.org
test-domain.com
```

Then run the script with the file:

```bash
python main.py domains.txt
```

### 3. Interactive Mode

Run the script without arguments to enter domains interactively:

```bash
python main.py
```

Then type one domain per line and press:

- Ctrl+D (Unix/Linux/MacOS) or
- Ctrl+Z (Windows)
  when done.

## Output

For each domain, the script will display:

- Domain name
- Availability status
- For registered domains:
  - Expiration date
  - Registrar information
- Any errors encountered during the check
