# client.py
import requests
import json
from smolagents import AgentLogger, Text, Group

logger = AgentLogger()

payload = {
    "task": "I need to synthesize a sample of safinamide. Please tell me how to synthesize it. Then tell me how much will it cost to buy all the reactants I need, if purchasable.",
    "model": "gpt4"
}

# 发起 POST 请求，开启流式读取
resp = requests.post("http://localhost:8080/run", json=payload, stream=True)


for line in resp.iter_lines(decode_unicode=True):
    if not line:
        continue
    try:
        recv_data = json.loads(line)
    except json.JSONDecodeError as e:
        print("❌ JSON 解码失败:", e)
        continue

    msg_type = recv_data.get("type")

    if msg_type == "log":
        sub_type = recv_data.get("sub_type", "")
        if sub_type == "Testing":
            print("TEST INFO:", recv_data.get("data", ""))
        else:
            data = recv_data.get("data", {})
            if sub_type == "Task":
                logger.log_task(
                    content=data.get("content", ""),
                    subtitle=data.get("subtitle", ""),
                    level=data.get("level", 0),
                    title=data.get("title", ""),
                )
            # Rule 日志
            elif sub_type == "Rule":
                logger.log_rule(
                    title=data.get("title", ""),
                    level=data.get("level", 0)
                )
            # Code 日志
            elif sub_type == "Code":
                logger.log_code(
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                    level=data.get("level", 0)
                )
            # Markdown 日志
            elif sub_type == "Markdown":
                logger.log_markdown(
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                    level=data.get("level", 0),
                    style=data.get("style", "")
                )
            # Error 日志
            elif sub_type == "Error":
                logger.log_error(
                    title=data.get("title", ""),
                    content=data.get("content", "")
                )
            
            elif sub_type == "Log":
                text = data.get("text", "")
                level = data.get("level", 0)
                appendix = data.get("appendix", "")
            
                text_list = text.split('||||||||||')
                appendix_list = appendix.split('||||||||||')

                log_list = []
                assert len(text_list) == len(appendix_list), "文本和附录长度不一致"
                for text_i, appendix_i in zip(text_list, appendix_list):
                    log_list.append(
                        Text(
                            text_i,
                            style=appendix_i.strip(),
                        )
                    )
                
                logger.log(
                    Group(*log_list),
                    level=level
                )


    elif msg_type == "result":
        print("✅ RESULT:", recv_data["result"])
        break

    elif msg_type == "error":
        print("❌ SERVER ERROR:", recv_data.get("data", "unknown error"))
        break

    else:
        print("⚠️ unknown message:", data)