import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def get_weather(city: str) -> str:
    data = {
        "jakarta": "Hujan deras, 26°C",
        "surabaya": "Cerah terik, 34°C",
        "bandung": "Sejuk berawan, 21°C"
    }
    return data.get(city.lower(), "City not found")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Mendapatkan informasi cuaca terkini untuk kota tertentu di Indonesia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Nama kota, contoh: 'Jakarta', 'Bandung', 'Surabaya'"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

messages = [
    {"role": "user", "content": "Bagaimana kondisi cuaca di jakarta, bandung dan ciamis sekarang?"},
{"role": "user", "content": "bagaimana kondisi cuaca di kuningan"}
]

print("> langkah pertama mengirim pertanyaan ke ai...")
response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-super-vl:free",  # atau model lain yang support tool calling
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
# buat output_log.json
with open("output_log.json", "w", encoding="utf-8") as file:
    file.write(response.model_dump_json(indent=2))

# conversi ke json
with open("output_log.json", "r", encoding="utf-8") as file:
    output = file.read()
output_json = json.loads(output)

msg = response.choices[0].message
print("Finsih Reason:", response.choices[0].finish_reason)

if msg.tool_calls:
    print("\n > langkah kedua memutuskan memanggil tool!")
    messages.append(msg)
    print(messages)

    for tool_call in msg.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        print(f" > memanggil tool {func_name} dengan argumen {func_args}")

        if func_name == "get_weather":
            hasil = get_weather(func_args["city"])
            print(f"Hasil eksekusi lokal: {hasil}")

            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": hasil})

    print("\n > langkah ketiga mengirim hasil eksekusi tool ke ai...")
    response2 = client.chat.completions.create(
        model="nvidia/nemotron-3.5-super-vl:free",
        messages=messages
    )

    print("\n" + "="*50)
    print("Jawaban akhir ai")
    print(response2.choices[0].message.content)

    print("="*50)

else:
    print("Ai langsung menjawab tanpa memanggil tool", msg.content)


