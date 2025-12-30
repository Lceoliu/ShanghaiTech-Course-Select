__all__ = ["js_var_to_py"]
import json
import re


def js_var_to_py(js_code: str, var_name: str = "lessonJSONs"):
    pat = rf'\bvar\s+{re.escape(var_name)}\s*='
    if re.search(pat, js_code) is None:
        raise ValueError(f"没找到 `var {var_name} = ...;` 片段")

    try:
        import quickjs
    except ImportError as e:
        raise RuntimeError("缺少依赖 quickjs。请先执行：pip install quickjs") from e

    ctx = quickjs.Context()

    try:
        ctx.eval(js_code)
    except Exception as e:
        raise RuntimeError(f"执行 JS 失败（可能有语法/引用错误）：{e}") from e

    try:
        s = ctx.eval(f"JSON.stringify({var_name})")
    except Exception as e:
        raise RuntimeError(f"无法 stringify({var_name})：{e}") from e

    return json.loads(s)
