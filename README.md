# MCP 图像搜索与图标生成服务

基于多个图片API的搜索服务和图标生成功能，专门设计用于与 Cursor MCP 服务集成。支持图片搜索、下载和AI生成图标。

![MCP图像搜索工具示例](examples/mcp_search_example.png)

## 工作原理

本工具通过MCP (Model Control Protocol) 为Cursor IDE提供图像搜索和图标生成功能：

1. **搜索图片**: 连接Unsplash、Pexels和Pixabay等图片源，根据关键词搜索高质量图片
2. **下载图片**: 将搜索到的图片下载到指定位置，方便直接在项目中使用
3. **生成图标**: 基于文本描述生成自定义图标，满足项目UI需求

### 系统工作流程

```
用户 (在Cursor中) → 向Claude/大模型提问 → 大模型调用MCP工具 → 工具处理请求 → 返回结果 → 大模型展示结果
```

比如，你可以在Cursor中向Claude询问"帮我找5张关于太空的图片"，Claude会通过MCP工具搜索并展示图片，然后你可以进一步要求下载或生成特定图标。

## 功能特点

* 支持多个图片源搜索 (Unsplash, Pexels, Pixabay)
* 高质量图标生成 (基于Together AI)
* 简单易用的API
* 完整的错误处理
* 自定义保存路径和文件名
* 可调整图片尺寸

## 环境准备

### 1. Python 环境

* Python 3.10+
* 下载地址： https://www.python.org/downloads/
* 推荐使用 pyenv 管理 Python 版本：

```bash
# macOS 安装 pyenv
brew install pyenv

# 安装 Python
pyenv install 3.13.2
pyenv global 3.13.2
```

### 2. uv 包管理工具

uv 是一个快速的 Python 包管理器，需要先安装：

```bash
# macOS 安装 uv
brew install uv

# 或者使用 pip 安装
pip install uv
```

### 3. 图片API密钥

#### Unsplash API 密钥
1. 访问 [Unsplash Developers](https://unsplash.com/developers)
2. 注册/登录账号
3. 创建新的应用程序
4. 获取 Access Key

#### Pexels API 密钥
1. 访问 [Pexels API](https://www.pexels.com/api/)
2. 注册/登录账号
3. 请求API密钥

#### Pixabay API 密钥
1. 访问 [Pixabay API](https://pixabay.com/api/docs/)
2. 注册/登录账号
3. 获取API密钥

#### Together AI API 密钥
1. 访问 [Together AI API Keys](https://api.together.xyz/keys)
2. 注册/登录账号
3. 创建新的 API 密钥

### 4. Cursor

* 下载并安装 [Cursor IDE](https://cursor.sh/)
* 确保 Cursor 已正确配置 Python 环境

## 安装配置

1. 克隆项目：

```bash
git clone https://github.com/yanjunz/mcp_search_images.git
```

2. 安装依赖：

```bash
python3 -m pip install fastmcp requests
```

出现证书问题可以使用：

```bash
python3 -m pip install fastmcp requests --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade --force-reinstall --no-cache-dir
```

3. 配置 API 密钥：

从模板创建配置文件：

```bash
# 复制模板文件作为配置文件
cp config.json.template config.json

# 编辑配置文件，设置API密钥
nano config.json  # 或使用其他编辑器
```

在 `config.json` 中修改以下配置：

```json
{
    "api": {
        "unsplash_access_key": "你的Unsplash访问密钥",
        "pexels_api_key": "你的Pexels API密钥",
        "pixabay_api_key": "你的Pixabay API密钥",
        "together_api_key": "你的Together API密钥",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5
    },
    // ...其他配置...
}
```

> **注意**：请确保不要将包含API密钥的配置文件提交到版本控制系统中。
> 项目中的 `.gitignore` 文件已配置为忽略 `config.json`，但保留 `config.json.template`。

## 运行服务

### 方法一：直接使用Python运行

这是最简单的方式，直接使用Python运行服务：

```bash
python3.11 mcp_search_images.py
```

服务启动后会显示以下信息:
```
启动图片搜索服务 - 端口: 5173
提供的工具: search_images, download_image, generate_icon
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5173 (Press CTRL+C to quit)
```

### 方法二：使用fastmcp命令运行

如果您安装了fastmcp包，也可以使用fastmcp命令运行：

1. 开发模式运行（带调试界面）：

```bash
fastmcp dev mcp_search_images.py
```

2. 生产模式运行：

```bash
fastmcp run mcp_search_images.py
```

3. 如果端口被占用，可以指定其他端口：

```bash
PORT=5174 fastmcp dev mcp_search_images.py
```

### 方法三：使用uv运行

如果您使用uv作为包管理器：

```bash
uv run --with fastmcp fastmcp run mcp_search_images.py
```

或者在开发模式下：

```bash
uv run --with fastmcp fastmcp dev mcp_search_images.py
```

### Cursor与MCP的工作原理

为了更好地理解和解决连接问题，以下是Cursor与MCP服务交互的基本工作原理：

1. **MCP服务启动流程**：
   * 当运行`python3.11 mcp_search_images.py`时，服务初始化并创建SSE（Server-Sent Events）应用
   * 服务在指定端口（默认5173）开始监听请求
   * 服务注册工具函数（search_images, download_image, generate_icon）
   * 对于使用ServerLink方式的连接，服务需要在`/sse`路径上正确处理SSE请求

2. **Cursor连接流程**：
   * 当在Cursor设置中添加MCP工具时，Cursor尝试与提供的URL建立连接
   * Cursor发送初始化请求，检查服务是否正常响应
   * 服务需要返回正确的MCP协议响应，包括可用工具列表
   * 连接成功后，Cursor会将该工具添加到可用工具列表
   
3. **诊断连接问题**：
   * 检查服务是否在运行：`lsof -i :5173`
   * 检查网络连接：`curl http://localhost:5173`
   * 检查服务是否正确实现MCP协议：服务启动日志应显示注册的工具
   * 检查防火墙和网络权限：本地服务有时可能被防火墙阻止
   
4. **完整的测试流程**：
   ```bash
   # 1. 停止任何可能正在运行的服务
   pkill -f "python.*mcp_search_images.py"
   
   # 2. 启动服务（在前台运行以查看日志）
   python3.11 mcp_search_images.py
   
   # 3. 在新的终端窗口中，测试连接
   curl http://localhost:5173
   
   # 4. 测试SSE端点（用于ServerLink方式）
   curl http://localhost:5173/sse
   
   # 5. 在Cursor中添加MCP工具并测试
   ```

如果按照以上步骤操作后仍然无法连接，可能需要检查Python版本兼容性或依赖包是否正确安装。有时重新安装依赖包也有帮助：

```bash
python3.11 -m pip uninstall fastmcp mcp uvicorn starlette -y
python3.11 -m pip install fastmcp mcp uvicorn starlette
```

## 使用说明

### 在 Cursor IDE 中使用

1. 确保服务正在运行
   ```bash
   # 直接运行Python脚本
   python3.11 mcp_search_images.py
   ```
   服务启动后会显示以下信息:
   ```
   启动图片搜索服务 - 端口: 5173
   提供的工具: search_images, download_image, generate_icon
   INFO:     Started server process [xxxxx]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:5173 (Press CTRL+C to quit)
   ```

2. 在Cursor中添加MCP服务:
   * 打开Cursor IDE
   * 点击左下角的齿轮图标，打开设置
   * 选择"AI & Copilot"设置
   * 在"MCP工具"部分点击"添加MCP工具"
   * 填写以下信息:
     - 名称: 图片搜索服务
     - 类型: SSE (Server-Sent Events)
     - URL: http://localhost:5173
     - 点击"保存"
     
   **备选配置方法**:
   * 某些版本的Cursor可能需要使用ServerLink配置:
     - 名称: 图片搜索服务
     - 类型: sse
     - ServerLink: http://localhost:5173/sse
     - 点击"保存"

   > **注意**: 如果出现"Fail to create client"错误，请检查以下几点:
   > 1. 确认服务正在运行 (通过`lsof -i :5173`检查端口是否被监听)
   > 2. 尝试在浏览器中访问`http://localhost:5173`测试连接性
   > 3. 确保URL没有多余的斜杠或空格
   > 4. 对于ServerLink方式，确保使用正确的端点路径`/sse`
   > 5. 重启服务后再次尝试添加
   > 6. 有时需要重启Cursor IDE以清除之前的连接缓存

3. 开始使用MCP工具:
   * 在Cursor中打开包含Claude或其他支持工具调用的大模型对话窗口
   * 当服务正在运行时，大模型可以自动发现并使用该工具
   * 如果大模型未自动发现工具，可以提示它:"请使用图片搜索服务来查找图片"

4. 在开发过程中随时使用:
   * 编写代码时需要图标素材，可以直接向大模型描述需求
   * 例如:"帮我找一些适合作为登录按钮的图标"
   * 大模型会调用MCP工具搜索图片并展示结果
   * 你可以进一步要求下载或生成自定义图标

5. 查看图标保存位置:
   * 默认情况下，图标会保存在项目根目录下的`icons`文件夹中
   * 可以通过以下命令查看已保存的图标:
     ```bash
     ls -la icons
     ```

### 功能使用示例

#### 搜索图片

可以直接向大模型描述需求:
```
搜索关键词为"technology"的图片
```
或更具体的描述:
```
请在Unsplash上搜索5张关于"artificial intelligence"的图片
```

#### 下载图片

当大模型显示搜索结果后，你可以要求下载特定图片:
```
下载第2张图片并保存为tech-icon.png
```
或者指定保存路径:
```
将第3张图片下载到/Users/username/Desktop/，文件名为ai-image.jpg
```

#### 生成图标

可以提供详细的描述来生成符合需求的图标:
```
生成一个蓝色科技风格的图标，保存为blue-tech.png
```
或者更详细的描述:
```
请创建一个扁平化设计的邮件图标，红色轮廓，白色背景，图标尺寸为256x256，保存为email-icon.png
```

### 实际对话示例

查看[示例对话](examples/dialog_example.md)了解如何在实际使用中与Claude/大模型交互来搜索和生成图标。

### 集成到项目工作流

1. 在项目初始阶段批量生成图标:
   * 创建设计系统时，可以一次性生成多个相关图标
   * 例如:"帮我生成一套包含主页、设置、用户、消息通知的应用图标"

2. 开发过程中按需搜索:
   * 在编写代码时随时查找所需图片资源
   * 例如:"我正在开发一个天气应用，需要几个天气相关的图标"

3. 项目完善阶段定制图标:
   * 根据应用风格统一优化图标
   * 例如:"生成一组与我当前应用风格一致的社交媒体分享图标"

### 最佳实践

1. **使用明确的关键词**: 搜索时使用具体、明确的关键词获得更精确的结果
2. **指定图片源**: 根据需求选择合适的图片源（Unsplash适合自然风光，Pixabay适合商业图片等）
3. **保存结构化命名**: 为图标使用结构化命名，如`category-name-size.png`
4. **批量操作**: 一次性请求多个相关图标而不是逐个请求
5. **与代码结合**: 在实际开发中提及代码上下文，大模型可以更准确地理解你的需求

## 错误排查

### Cursor MCP连接错误

如果在Cursor中添加MCP服务时遇到"Fail to create client"错误，请尝试以下解决方法：

1. **检查服务状态**：
   ```bash
   # 检查服务是否正在运行
   lsof -i :5173
   # 如果没有输出，表示服务未运行，请启动服务
   python3.11 mcp_search_images.py
   ```

2. **测试连接**：
   ```bash
   # 使用curl测试API连接
   curl -v http://localhost:5173
   ```

3. **修改连接设置**：
   * 确保选择了正确的连接类型：SSE
   * 尝试使用IP地址代替localhost：`http://127.0.0.1:5173`
   * 确保URL不含额外斜杠：使用`http://localhost:5173`而非`http://localhost:5173/`
   * 尝试使用ServerLink方式配置：
     - 类型: sse
     - ServerLink: http://localhost:5173/sse
   * 有些版本的Cursor可能对URL格式有特定要求，两种方式都值得尝试

4. **重启组件**：
   * 停止并重启MCP服务
   * 重启Cursor IDE
   * 如果使用macOS，检查防火墙设置是否阻止了连接

5. **检查日志**：
   * 观察服务启动时的日志输出
   * 当尝试从Cursor连接时，查看服务端有无新的日志输出

6. **尝试其他端口**：
   * 修改代码中的端口（如改为5174）并重启服务：
   ```python
   uvicorn.run(sse_app, host="0.0.0.0", port=5174)
   ```

### 其他常见问题

如果遇到问题，请检查：

1. 服务是否正常运行
2. 保存路径是否正确
3. 目录权限是否正确
4. 网络连接是否正常
5. API 密钥是否有效
6. Python 环境是否正确配置
7. uv 是否正确安装
8. 依赖包是否完整安装

## 贡献

欢迎提交问题和拉取请求来改进项目。

## 许可

[MIT License](LICENSE) 