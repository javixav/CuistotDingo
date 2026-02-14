def hex_to_rgba(hex_color, alpha = 1.0):
    ''' Converts a hexadecimal color code to an RGBA tuple.

    Args:
            hex_color (str): The hexadecimal color string (e.g., "#RRGGBB", "#RRGGBBAA", "RRGGBB").
            alpha (float, optional): The default alpha value (0.0 to 1.0) if not provided in hex_color.
                                    Defaults to 1.0.

    Returns:
            tuple: An RGBA tuple (red, green, blue, alpha), where each component
            is a float between 0.0 and 1.0. '''

    hex_color = hex_color.lstrip('#')
    length = len(hex_color)

    if length == 6:  # RRGGBB format
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = alpha
        
    elif length == 8:  # RRGGBBAA format
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0
    else:
        raise ValueError("Invalid hex color format. Expected 6 or 8 characters.")

    return [r, g, b, a]

def rgba_to_hex(r, g, b, a):
    '''  Converts RGBA color values to an 8-digit hexadecimal string.

    Args:
            r (int or float): Red component (0-1).
            g (int or float): Green component (0-1).
            b (int or flaot): Blue component (0-1).
            a (float): Alpha component (0.0-1.0).

    Returns:
            str: 8-digit hexadecimal color string (e.g., '#RRGGBBAA'). '''

    r,g,b = int(r*255),int(g*255),int(b*255)
    # Ensure RGB values are within the valid range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    # Convert alpha from 0.0-1.0 to 0-255 integer
    alpha_int = int(round(a * 255))
    alpha_int = max(0, min(255, alpha_int))

    # Format as an 8-digit hex string
    return f'#{r:02x}{g:02x}{b:02x}{alpha_int:02x}'
