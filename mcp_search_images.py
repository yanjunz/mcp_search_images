import os
import json
import base64
import requests
import sys
from mcp.server import FastMCP

# 加载配置文件
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
CONFIG_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json.template")

try:
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(CONFIG_TEMPLATE):
            print(f"配置文件不存在，请从模板创建: {CONFIG_TEMPLATE} -> {CONFIG_FILE}")
        else:
            print(f"配置文件和模板都不存在，请创建配置文件: {CONFIG_FILE}")
        sys.exit(1)
        
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
        
    # 检查必要的API密钥
    missing_keys = []
    if not CONFIG["api"]["unsplash_access_key"]:
        missing_keys.append("unsplash_access_key")
    if not CONFIG["api"]["pexels_api_key"]:
        missing_keys.append("pexels_api_key")
    if not CONFIG["api"]["pixabay_api_key"]:
        missing_keys.append("pixabay_api_key")
        
    if missing_keys:
        print(f"警告: 以下API密钥未配置: {', '.join(missing_keys)}")
        print(f"某些功能可能无法正常工作，请在配置文件中设置API密钥: {CONFIG_FILE}")
        
    # 处理输出目录路径
    if not os.path.isabs(CONFIG["output"]["base_folder"]):
        CONFIG["output"]["base_folder"] = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            CONFIG["output"]["base_folder"]
        )
        
except Exception as e:
    print(f"加载配置文件时出错: {str(e)}")
    sys.exit(1)

# 创建输出目录
os.makedirs(CONFIG["output"]["base_folder"], exist_ok=True)

# 用于支持MCP服务的实例
app = FastMCP(name=CONFIG["server"]["name"])

@app.tool()
def search_images(query: str, source: str = "unsplash", max_results: int = 10) -> str:
    """搜索图片
    
    Args:
        query: 图片搜索关键词
        source: 图片来源 (unsplash, pexels, pixabay)
        max_results: 最大返回结果数量，必须是整数
        
    Returns:
        str: 包含搜索结果的JSON字符串
    """
    # 确保max_results是整数
    try:
        max_results = int(max_results)
    except (TypeError, ValueError):
        return json.dumps({"error": "max_results必须是整数"})
        
    results = []
    
    if max_results > CONFIG["image"]["max_results"]:
        max_results = CONFIG["image"]["max_results"]
    
    try:
        if source.lower() == "unsplash":
            # Unsplash API
            api_url = f"https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {CONFIG['api']['unsplash_access_key']}"
            }
            params = {
                "query": query,
                "per_page": max_results
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("results", []):
                    results.append({
                        "id": item.get("id"),
                        "url": item.get("urls", {}).get("small"),
                        "thumb": item.get("urls", {}).get("thumb"),
                        "source": "unsplash",
                        "author": item.get("user", {}).get("name"),
                        "download_url": item.get("urls", {}).get("raw")
                    })
        
        elif source.lower() == "pexels":
            # Pexels API
            api_url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": CONFIG['api']['pexels_api_key']
            }
            params = {
                "query": query,
                "per_page": max_results
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("photos", []):
                    results.append({
                        "id": item.get("id"),
                        "url": item.get("src", {}).get("medium"),
                        "thumb": item.get("src", {}).get("small"),
                        "source": "pexels",
                        "author": item.get("photographer"),
                        "download_url": item.get("src", {}).get("original")
                    })
        
        elif source.lower() == "pixabay":
            # Pixabay API
            api_url = "https://pixabay.com/api/"
            params = {
                "key": CONFIG['api']['pixabay_api_key'],
                "q": query,
                "per_page": max_results
            }
            
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("hits", []):
                    results.append({
                        "id": item.get("id"),
                        "url": item.get("webformatURL"),
                        "thumb": item.get("previewURL"),
                        "source": "pixabay",
                        "author": item.get("user"),
                        "download_url": item.get("largeImageURL")
                    })
                    
        else:
            return json.dumps({"error": f"不支持的图片源: {source}. 支持的选项: unsplash, pexels, pixabay"})
            
    except Exception as e:
        return json.dumps({"error": f"搜索图片时发生错误: {str(e)}"})
        
    return json.dumps({"results": results})

@app.tool()
def download_image(url: str, file_name: str, save_folder: str = None) -> str:
    """下载图片
    
    Args:
        url: 图片URL
        file_name: 保存的文件名
        save_folder: 保存目录路径
        
    Returns:
        str: 包含下载结果的JSON字符串
    """
    try:
        # 验证并设置保存路径
        if save_folder is None:
            save_folder = CONFIG["output"]["base_folder"]
        
        # 确保目录存在
        os.makedirs(save_folder, exist_ok=True)
        
        # 验证文件扩展名
        _, ext = os.path.splitext(file_name)
        if not ext:
            file_name += CONFIG["output"]["default_extension"]
        elif ext.lower() not in CONFIG["output"]["allowed_extensions"]:
            return json.dumps({"error": f"不支持的文件扩展名: {ext}. 支持的扩展名: {', '.join(CONFIG['output']['allowed_extensions'])}"})
        
        # 完整的保存路径
        save_path = os.path.join(save_folder, file_name)
        
        # 下载图片
        response = requests.get(url, stream=True, timeout=CONFIG["api"]["timeout"])
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            return json.dumps({
                "success": True,
                "message": f"图片已保存到: {save_path}",
                "file_path": save_path
            })
        else:
            return json.dumps({
                "success": False,
                "error": f"下载图片失败，HTTP状态码: {response.status_code}"
            })
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"下载图片时发生错误: {str(e)}"
        })

@app.tool()
def generate_icon(prompt: str, file_name: str, save_folder: str = None, width: int = None, height: int = None) -> str:
    """生成图标
    
    Args:
        prompt: 图标生成提示词
        file_name: 保存的文件名
        save_folder: 保存目录路径
        width: 生成图标的宽度(可选)
        height: 生成图标的高度(可选)
        
    Returns:
        str: 包含生成结果的JSON字符串
    """
    try:
        # 验证并设置保存路径
        if save_folder is None:
            save_folder = CONFIG["output"]["base_folder"]
        
        # 确保目录存在
        os.makedirs(save_folder, exist_ok=True)
        
        # 设置默认尺寸
        if width is None:
            width = CONFIG["image"]["default_width"]
        if height is None:
            height = CONFIG["image"]["default_height"]
            
        # 验证文件扩展名
        _, ext = os.path.splitext(file_name)
        if not ext:
            file_name += CONFIG["output"]["default_extension"]
        elif ext.lower() not in CONFIG["output"]["allowed_extensions"]:
            return json.dumps({"error": f"不支持的文件扩展名: {ext}. 支持的扩展名: {', '.join(CONFIG['output']['allowed_extensions'])}"})
        
        # 完整的保存路径
        save_path = os.path.join(save_folder, file_name)
        
        # 检查Together API密钥是否配置
        if CONFIG["api"].get("together_api_key"):
            # 使用Together API生成图标
            api_url = "https://api.together.xyz/v1/images/generation"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CONFIG['api']['together_api_key']}"
            }
            
            payload = {
                "model": "stabilityai/stable-diffusion-xl-base-1.0",
                "prompt": prompt,
                "width": width,
                "height": height,
                "steps": 30,
                "seed": 42,
                "num_images": 1
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    image_data = data.get("output", {}).get("choices", [{}])[0].get("image_base64", "")
                    
                    if image_data:
                        # 将base64解码为二进制数据并保存
                        with open(save_path, 'wb') as f:
                            f.write(base64.b64decode(image_data))
                            
                        return json.dumps({
                            "success": True,
                            "message": f"图标已生成并保存到: {save_path}",
                            "file_path": save_path
                        })
                    else:
                        raise Exception("API响应中没有图像数据")
                except Exception as inner_e:
                    raise Exception(f"处理API响应时出错: {str(inner_e)}")
            else:
                error_msg = f"生成图标API请求失败，HTTP状态码: {response.status_code}"
                if response.text:
                    error_msg += f", 响应: {response.text}"
                raise Exception(error_msg)
        else:
            # 未配置Together API密钥，使用本地替代方案
            print("警告: Together API密钥未配置，将使用本地示例图标替代")
            # 为了测试，我们简单地复制sample-icon.png来模拟生成的图标
            sample_icon_path = os.path.join(CONFIG["output"]["base_folder"], "sample-icon.png")
            
            if os.path.exists(sample_icon_path):
                with open(sample_icon_path, 'rb') as src_file, open(save_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
                    
                return json.dumps({
                    "success": True,
                    "message": f"图标已生成并保存到: {save_path}（使用样例图标替代）",
                    "file_path": save_path
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "无法找到示例图标文件，生成失败。请配置Together API密钥，或确保sample-icon.png存在"
                })
                
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"生成图标时发生错误: {str(e)}"
        })

if __name__ == "__main__":
    # 启动MCP服务器
    import uvicorn
    from starlette.applications import Starlette
    
    # 创建SSE应用
    sse_app = app.sse_app()
    
    # 打印启动信息
    print(f"启动图片搜索服务 - 端口: {CONFIG['server']['port']}")
    print(f"提供的工具: search_images, download_image, generate_icon")
    
    # 运行服务
    uvicorn.run(sse_app, host=CONFIG["server"]["host"], port=CONFIG["server"]["port"]) 