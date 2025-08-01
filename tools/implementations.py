def get_weather(location: str, unit: str = "celsius") -> str:
    """模拟天气查询"""
    return f"Weather in {location}: 22°C, sunny"

def search_web(query: str, num_results: int = 3) -> list:
    """模拟网络搜索"""
    return [
        f"Result 1 for '{query}'",
        f"Result 2 for '{query}'",
        f"Result 3 for '{query}'"
    ]
