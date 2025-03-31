# MCP Image Search and Icon Generation Service

A search service based on multiple image APIs and icon generation capabilities, specifically designed for integration with Cursor MCP service. Supports image search, download, and AI-generated icons.

![MCP Image Search Tool Example](examples/mcp_search_example.png)

## How It Works

This tool provides image search and icon generation capabilities for Cursor IDE through MCP (Model Control Protocol):

1. **Search Images**: Connect to image sources like Unsplash, Pexels, and Pixabay to search for high-quality images based on keywords
2. **Download Images**: Save found images to specified locations for direct use in your project
3. **Generate Icons**: Create custom icons based on text descriptions to meet project UI requirements

### System Workflow

```
User (in Cursor) → Ask Claude/LLM → LLM calls MCP tool → Tool processes request → Returns results → LLM displays results
```

For example, you can ask Claude in Cursor "Find me 5 images about space", and Claude will search and display images using the MCP tool. You can then request to download or generate specific icons.

## Features

* Support for multiple image sources (Unsplash, Pexels, Pixabay)
* High-quality icon generation (based on Together AI)
* Simple and easy-to-use API
* Complete error handling
* Custom save paths and filenames
* Adjustable image dimensions

## Environment Setup

### 1. Python Environment

* Python 3.10+
* Download from: https://www.python.org/downloads/
* Recommended to use pyenv to manage Python versions:

```bash
# Install pyenv on macOS
brew install pyenv

# Install Python
pyenv install 3.13.2
pyenv global 3.13.2
```

### 2. UV Package Manager

UV is a fast Python package manager that needs to be installed first:

```bash
# Install UV on macOS
brew install uv

# Or install with pip
pip install uv
```

### 3. Image API Keys

#### Unsplash API Key
1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Register/login
3. Create a new application
4. Get Access Key

#### Pexels API Key
1. Visit [Pexels API](https://www.pexels.com/api/)
2. Register/login
3. Request API key

#### Pixabay API Key
1. Visit [Pixabay API](https://pixabay.com/api/docs/)
2. Register/login
3. Get API key

#### Together AI API Key
1. Visit [Together AI API Keys](https://api.together.xyz/keys)
2. Register/login
3. Create a new API key

### 4. Cursor

* Download and install [Cursor IDE](https://cursor.sh/)
* Ensure Cursor is correctly configured with Python environment

## Installation & Configuration

1. Clone the project:

```bash
git clone https://github.com/yanjunz/mcp_search_images.git
```

2. Install dependencies:

```bash
python3 -m pip install fastmcp requests
```

If you encounter certificate issues, use:

```bash
python3 -m pip install fastmcp requests --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade --force-reinstall --no-cache-dir
```

3. Configure API keys:

Create a configuration file from the template:

```bash
# Copy the template file as your configuration file
cp config.json.template config.json

# Edit the configuration file to set API keys
nano config.json  # or use another editor
```

In `config.json`, modify the following configuration:

```json
{
    "api": {
        "unsplash_access_key": "your_unsplash_access_key",
        "pexels_api_key": "your_pexels_api_key",
        "pixabay_api_key": "your_pixabay_api_key",
        "together_api_key": "your_together_api_key",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5
    },
    // ...other configurations...
}
```

> **Note**: Make sure not to commit configuration files containing API keys to version control systems.
> The project's `.gitignore` file is already configured to ignore `config.json` but keep `config.json.template`.

## Running the Service

### Method 1: Direct Python Execution

This is the simplest way to run the service directly with Python:

```bash
python3.11 mcp_search_images.py
```

The service will display the following information after starting:
```
Starting Image Search Service - Port: 5173
Tools provided: search_images, download_image, generate_icon
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5173 (Press CTRL+C to quit)
```

### Method 2: Using fastmcp Command

If you've installed the fastmcp package, you can also run it with:

1. Run in development mode (with debug interface):

```bash
fastmcp dev mcp_search_images.py
```

2. Run in production mode:

```bash
fastmcp run mcp_search_images.py
```

3. If the port is occupied, specify another port:

```bash
PORT=5174 fastmcp dev mcp_search_images.py
```

### Method 3: Using UV

If you use UV as your package manager:

```bash
uv run --with fastmcp fastmcp run mcp_search_images.py
```

Or in development mode:

```bash
uv run --with fastmcp fastmcp dev mcp_search_images.py
```

### How Cursor and MCP Work Together

To better understand and troubleshoot connection issues, here's how Cursor interacts with the MCP service:

1. **MCP Service Startup Process**:
   * When running `python3.11 mcp_search_images.py`, the service initializes and creates an SSE (Server-Sent Events) application
   * Service starts listening on the specified port (default 5173)
   * Service registers tool functions (search_images, download_image, generate_icon)
   * For ServerLink connections, the service needs to correctly handle SSE requests on the `/sse` path

2. **Cursor Connection Process**:
   * When adding an MCP tool in Cursor settings, Cursor attempts to establish a connection with the provided URL
   * Cursor sends an initialization request to check if the service responds properly
   * The service needs to return the correct MCP protocol response, including the list of available tools
   * After successful connection, Cursor will add the tool to the list of available tools
   
3. **Diagnosing Connection Issues**:
   * Check if the service is running: `lsof -i :5173`
   * Check network connection: `curl http://localhost:5173`
   * Check if the service correctly implements the MCP protocol: Service startup logs should display registered tools
   * Check firewall and network permissions: Local services might sometimes be blocked by firewalls
   
4. **Complete Testing Process**:
   ```bash
   # 1. Stop any potentially running services
   pkill -f "python.*mcp_search_images.py"
   
   # 2. Start the service (run in foreground to see logs)
   python3.11 mcp_search_images.py
   
   # 3. In a new terminal window, test the connection
   curl http://localhost:5173
   
   # 4. Test the SSE endpoint (for ServerLink method)
   curl http://localhost:5173/sse
   
   # 5. Add the MCP tool in Cursor and test
   ```

If you still can't connect after following these steps, you might need to check Python version compatibility or if dependencies are correctly installed. Sometimes reinstalling dependencies can help:

```bash
python3.11 -m pip uninstall fastmcp mcp uvicorn starlette -y
python3.11 -m pip install fastmcp mcp uvicorn starlette
```

## Usage Guide

### Using in Cursor IDE

1. Ensure the service is running
   ```bash
   # Run the Python script directly
   python3.11 mcp_search_images.py
   ```
   The service will display the following information after startup:
   ```
   Starting Image Search Service - Port: 5173
   Tools provided: search_images, download_image, generate_icon
   INFO:     Started server process [xxxxx]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:5173 (Press CTRL+C to quit)
   ```

2. Add MCP service in Cursor:
   * Open Cursor IDE
   * Click the gear icon in the bottom left to open settings
   * Select "AI & Copilot" settings
   * In the "MCP Tools" section, click "Add MCP Tool"
   * Fill in the following information:
     - Name: Image Search Service
     - Type: SSE (Server-Sent Events)
     - URL: http://localhost:5173
     - Click "Save"
     
   **Alternative Configuration Method**:
   * Some versions of Cursor might require using ServerLink configuration:
     - Name: Image Search Service
     - Type: sse
     - ServerLink: http://localhost:5173/sse
     - Click "Save"

   > **Note**: If you encounter a "Fail to create client" error, check the following:
   > 1. Confirm the service is running (check if the port is being listened to with `lsof -i :5173`)
   > 2. Try accessing `http://localhost:5173` in a browser to test connectivity
   > 3. Ensure the URL has no extra slashes or spaces
   > 4. For ServerLink method, ensure you're using the correct endpoint path `/sse`
   > 5. Restart the service and try adding it again
   > 6. Sometimes you may need to restart Cursor IDE to clear previous connection cache

3. Start using the MCP tool:
   * Open a Claude or other LLM dialog window that supports tool calling in Cursor
   * When the service is running, the LLM can automatically discover and use the tool
   * If the LLM doesn't automatically discover the tool, you can prompt it: "Please use the image search service to find images"

4. Use during development:
   * When coding and needing icon resources, directly describe your needs to the LLM
   * For example: "Find me some icons suitable for a login button"
   * The LLM will call the MCP tool to search for images and display results
   * You can further request to download or generate custom icons

5. View saved icon location:
   * By default, icons are saved in the `icons` folder in the project root
   * You can view saved icons with the following command:
     ```bash
     ls -la icons
     ```

### Usage Examples

#### Searching Images

You can directly describe your needs to the LLM:
```
Search for images with the keyword "technology"
```
Or provide a more specific description:
```
Please search for 5 images about "artificial intelligence" on Unsplash
```

#### Downloading Images

When the LLM displays search results, you can request to download a specific image:
```
Download the 2nd image and save it as tech-icon.png
```
Or specify a save path:
```
Save the 3rd image to /Users/username/Desktop/ with the filename ai-image.jpg
```

#### Generating Icons

You can provide detailed descriptions to generate icons that meet your requirements:
```
Generate a blue tech-style icon and save it as blue-tech.png
```
Or a more detailed description:
```
Please create a flat design email icon with red outline, white background, icon size 256x256, and save it as email-icon.png
```

### Real Conversation Example

Check out the [example dialog](examples/dialog_example_en.md) to see how to interact with Claude/LLM to search for and generate icons in real usage.

### Integration into Project Workflow

1. Batch generate icons at the project's initial phase:
   * When creating a design system, generate multiple related icons at once
   * For example: "Help me generate a set of app icons including home, settings, user, and notification"

2. Search on-demand during development:
   * Look for needed image resources while writing code
   * For example: "I'm developing a weather app and need several weather-related icons"

3. Customize icons during project refinement:
   * Optimize icons to match the application style
   * For example: "Generate a set of social media sharing icons that match my current app style"

### Best Practices

1. **Use Clear Keywords**: Use specific, clear keywords when searching to get more precise results
2. **Specify Image Source**: Choose appropriate image sources based on needs (Unsplash for nature, Pixabay for business images, etc.)
3. **Use Structured Naming**: Use structured naming for icons, like `category-name-size.png`
4. **Batch Operations**: Request multiple related icons at once instead of one by one
5. **Integrate with Code**: Mention code context in actual development, the LLM can better understand your needs

## Troubleshooting

### Cursor MCP Connection Errors

If you encounter a "Fail to create client" error when adding the MCP service in Cursor, try these solutions:

1. **Check Service Status**:
   ```bash
   # Check if the service is running
   lsof -i :5173
   # If no output, the service is not running, start it
   python3.11 mcp_search_images.py
   ```

2. **Test Connection**:
   ```bash
   # Use curl to test API connection
   curl -v http://localhost:5173
   ```

3. **Modify Connection Settings**:
   * Make sure you've selected the correct connection type: SSE
   * Try using IP address instead of localhost: `http://127.0.0.1:5173`
   * Ensure URL has no extra slashes: use `http://localhost:5173` not `http://localhost:5173/`
   * Try using ServerLink configuration:
     - Type: sse
     - ServerLink: http://localhost:5173/sse
   * Some versions of Cursor might have specific URL format requirements, both methods are worth trying

4. **Restart Components**:
   * Stop and restart the MCP service
   * Restart Cursor IDE
   * If using macOS, check if firewall settings are blocking the connection

5. **Check Logs**:
   * Observe logs during service startup
   * When attempting to connect from Cursor, check if there are new log outputs on the server side

6. **Try Different Ports**:
   * Modify the port in the code (e.g., change to 5174) and restart the service:
   ```python
   uvicorn.run(sse_app, host="0.0.0.0", port=5174)
   ```

### Other Common Issues

If you encounter problems, check:

1. If the service is running properly
2. If the save path is correct
3. If directory permissions are correct
4. If network connection is normal
5. If API keys are valid
6. If Python environment is correctly configured
7. If UV is correctly installed
8. If dependency packages are fully installed

## Contribution

Issues and pull requests are welcome to improve the project.

## License

[MIT License](LICENSE) 