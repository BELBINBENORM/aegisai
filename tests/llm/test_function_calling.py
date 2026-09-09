import pytest

from app.llm.function_calling import FunctionCallingClient


@pytest.mark.asyncio
async def test_function_calling():
    client = FunctionCallingClient()

    weather_function = {
        "name": "get_weather",
        "description": "Get the weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name.",
                }
            },
            "required": ["city"],
        },
    }

    function_call = await client.generate_function_call(
        prompt="What is the weather in Chennai?",
        function_declaration=weather_function,
    )

    assert function_call is not None
    assert function_call.name == "get_weather"
    assert function_call.args["city"]