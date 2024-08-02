def progressbar(value):
    def get_color(val):
        return "🟢" if val == 1 else ("🟡" if 2 <= val <= 4 else ("🟠" if 5 <= val <= 7 else ("🔴" if 8 <= val <= 10 else "⚪")))

    # Calculate the output circles
    left_half = ["⚪"] * 10
    right_half = ["⚪"] * 10

    # For positive values, color the right half
    if value > 0:
        for i in range(value):
            right_half[i] = get_color(i + 1)

    # For negative values, color the left half starting from the center
    elif value < 0:
        for i in range(-value):
            left_half[i] = get_color(i + 1)

    # Combine the halves with the blue center
    return ''.join(left_half[::-1]) + "💠" + ''.join(right_half)