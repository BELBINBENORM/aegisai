def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price: float = 0.0,
    output_price: float = 0.0,
) -> float:
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price

    return input_cost + output_cost