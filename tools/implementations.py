def get_weather(location: str, unit: str = "celsius") -> str:
    """模拟天气查询"""
    return f"Weather in {location}: 22°C, sunny"

def compare(a: float, b: float):
    if a > b:
        return f'{a} is greater than {b}'
    elif a < b:
        return f'{b} is greater than {a}'
    else:
        return f'{a} is equal to {b}'
