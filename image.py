"""
Image generator for System Safety Tools.
This module creates programmatically generated icons for the application,
eliminating the need for external image files.
"""

import io
import os
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class ImageGenerator:
    """Generate programmatic icons for the application."""
    
    @staticmethod
    def create_circle_icon(color, size=48, bg_color=None, outline_color=None, outline_width=0):
        """Create a simple circle icon."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0) if bg_color is None else bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw a circle
        padding = outline_width + 2
        draw.ellipse(
            [(padding, padding), (size - padding, size - padding)],
            fill=color,
            outline=outline_color,
            width=outline_width
        )
        
        return img
    
    @staticmethod
    def create_square_icon(color, size=48, bg_color=None, outline_color=None, outline_width=0, corner_radius=10):
        """Create a rounded square icon."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0) if bg_color is None else bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw a rounded rectangle
        padding = outline_width + 2
        draw.rounded_rectangle(
            [(padding, padding), (size - padding, size - padding)],
            radius=corner_radius,
            fill=color,
            outline=outline_color,
            width=outline_width
        )
        
        return img
    
    @staticmethod
    def create_app_icon(size=64):
        """Create application icon - a shield with a checkmark."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw shield shape
        shield_color = "#3f51b5"  # Primary blue
        check_color = "#ffffff"   # White
        
        # Shield body
        shield_points = [
            (size//2, size//10),  # Top middle
            (size*9//10, size//4),  # Top right
            (size*9//10, size//2),  # Middle right
            (size//2, size*9//10),  # Bottom middle
            (size//10, size//2),    # Middle left
            (size//10, size//4),    # Top left
        ]
        draw.polygon(shield_points, fill=shield_color)
        
        # Checkmark
        check_width = 4
        check_points = [
            (size*3//10, size*5//10),  # Left point
            (size*4//10, size*7//10),  # Bottom point
            (size*7//10, size*3//10),  # Top right point
        ]
        draw.line(check_points, fill=check_color, width=check_width)
        
        return img
    
    @staticmethod
    def create_settings_icon(size=48):
        """Create settings icon (gear)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Settings gear
        gear_color = "#757575"  # Gray
        
        # Draw outer circle
        center = size // 2
        outer_radius = size * 0.4
        inner_radius = size * 0.2
        
        # Draw gear teeth
        num_teeth = 8
        tooth_depth = size * 0.1
        
        for i in range(num_teeth):
            angle = 2 * 3.14159 * i / num_teeth
            angle_next = 2 * 3.14159 * (i + 0.5) / num_teeth
            
            # Outer point
            x1 = center + (outer_radius + tooth_depth) * 0.9 * (0.5 - 0.5 * (i % 2)) * (0 if i % 2 else 1) * 1.5 * ((-1) ** (i // 2))
            y1 = center + (outer_radius + tooth_depth) * 0.9 * (0.5 - 0.5 * ((i + 1) % 2)) * (0 if (i + 1) % 2 else 1) * 1.5 * ((-1) ** ((i + 1) // 2))
            
            # Inner point
            x2 = center + inner_radius * 0.9 * (0.5 - 0.5 * (i % 2)) * (0 if i % 2 else 1) * 1.5 * ((-1) ** (i // 2))
            y2 = center + inner_radius * 0.9 * (0.5 - 0.5 * ((i + 1) % 2)) * (0 if (i + 1) % 2 else 1) * 1.5 * ((-1) ** ((i + 1) // 2))
            
            if i % 2 == 0:
                draw.rectangle([(int(x1-tooth_depth), int(y1-tooth_depth)), 
                              (int(x1+tooth_depth), int(y1+tooth_depth))], 
                              fill=gear_color)
            
        # Draw center circle
        draw.ellipse(
            [(center - inner_radius, center - inner_radius), 
             (center + inner_radius, center + inner_radius)],
            fill=gear_color
        )
        
        return img
    
    @staticmethod
    def create_help_icon(size=48):
        """Create help icon (question mark)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Question mark in a circle
        circle_color = "#2196f3"  # Blue
        text_color = "#ffffff"    # White
        
        # Draw circle
        padding = 2
        draw.ellipse(
            [(padding, padding), (size - padding, size - padding)],
            fill=circle_color
        )
        
        # Draw question mark
        font_size = size // 2
        # Since drawing text is complex without a font, we'll approximate a question mark
        # with shapes
        
        # Question mark stem
        stem_width = size // 8
        draw.ellipse(
            [(size//2 - stem_width//2, size*2//3), 
             (size//2 + stem_width//2, size*2//3 + stem_width)],
            fill=text_color
        )
        
        # Question mark top curve
        curve_width = size // 6
        for i in range(0, 180, 5):
            angle_rad = 3.14159 * i / 180
            x = size//2 + (size//4) * (1 if i < 90 else -1)
            y = size//3 + (size//4) * (1 if i > 90 else 0)
            draw.ellipse(
                [(x - curve_width//2, y - curve_width//2),
                 (x + curve_width//2, y + curve_width//2)],
                fill=text_color
            )
        
        return img
    
    @staticmethod
    def create_clean_icon(size=48):
        """Create clean icon (broom)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Broom
        handle_color = "#8d6e63"  # Brown
        bristles_color = "#ffecb3"  # Light yellow
        
        # Draw broom handle
        handle_width = size // 12
        draw.line(
            [(size//4, size//4), (size*3//4, size*3//4)],
            fill=handle_color,
            width=handle_width
        )
        
        # Draw bristles
        bristle_width = size // 15
        for i in range(-3, 4):
            draw.line(
                [(size*2//3 + i*bristle_width, size*2//3 + i*bristle_width), 
                 (size*2//3 + i*bristle_width + size//10, size*2//3 + i*bristle_width + size//5)],
                fill=bristles_color,
                width=bristle_width
            )
        
        return img
    
    @staticmethod
    def create_scan_icon(size=48):
        """Create scan icon (magnifying glass)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Magnifying glass
        glass_color = "#bbdefb"  # Light blue
        handle_color = "#1976d2"  # Darker blue
        outline_color = "#0d47a1"  # Even darker blue
        
        # Draw glass circle
        glass_radius = size // 3
        draw.ellipse(
            [(size//4 - glass_radius, size//4 - glass_radius), 
             (size//4 + glass_radius, size//4 + glass_radius)],
            fill=glass_color,
            outline=outline_color,
            width=2
        )
        
        # Draw handle
        handle_width = size // 10
        draw.line(
            [(size//4 + glass_radius*0.7, size//4 + glass_radius*0.7), 
             (size*3//4, size*3//4)],
            fill=handle_color,
            width=handle_width
        )
        
        return img
    
    @staticmethod
    def create_repair_icon(size=48):
        """Create repair icon (wrench)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Wrench
        wrench_color = "#78909c"  # Blue gray
        highlight_color = "#cfd8dc"  # Lighter blue gray
        
        # Draw wrench body (simplified as a polygon)
        wrench_points = [
            (size//6, size//6),
            (size//3, size//3),
            (size*2//3, size*2//3),
            (size*5//6, size*5//6),
            (size*5//6 - size//12, size*5//6),
            (size*2//3 - size//12, size*2//3),
            (size//3 - size//12, size//3),
            (size//6 - size//12, size//6),
        ]
        draw.polygon(wrench_points, fill=wrench_color)
        
        # Draw wrench openings (circles at each end)
        draw.ellipse(
            [(size//6 - size//8, size//6 - size//8),
             (size//6 + size//8, size//6 + size//8)],
            fill=highlight_color
        )
        
        draw.ellipse(
            [(size*5//6 - size//8, size*5//6 - size//8),
             (size*5//6 + size//8, size*5//6 + size//8)],
            fill=highlight_color
        )
        
        return img
    
    @staticmethod
    def create_success_icon(size=48):
        """Create success icon (checkmark)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Checkmark in circle
        circle_color = "#4caf50"  # Green
        check_color = "#ffffff"   # White
        
        # Draw circle
        padding = 2
        draw.ellipse(
            [(padding, padding), (size - padding, size - padding)],
            fill=circle_color
        )
        
        # Draw checkmark
        check_width = size // 10
        check_points = [
            (size//4, size//2),
            (size*2//5, size*2//3),
            (size*3//4, size//3)
        ]
        draw.line(check_points, fill=check_color, width=check_width)
        
        return img
    
    @staticmethod
    def create_error_icon(size=48):
        """Create error icon (X mark)."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # X mark in circle
        circle_color = "#f44336"  # Red
        x_color = "#ffffff"      # White
        
        # Draw circle
        padding = 2
        draw.ellipse(
            [(padding, padding), (size - padding, size - padding)],
            fill=circle_color
        )
        
        # Draw X
        x_width = size // 10
        draw.line([(size//4, size//4), (size*3//4, size*3//4)], fill=x_color, width=x_width)
        draw.line([(size*3//4, size//4), (size//4, size*3//4)], fill=x_color, width=x_width)
        
        return img
    
    @classmethod
    def get_image_dict(cls, size=48):
        """Return a dictionary of all icons."""
        return {
            "app_icon": ImageTk.PhotoImage(cls.create_app_icon(size=64)),
            "settings": ImageTk.PhotoImage(cls.create_settings_icon(size=size)),
            "help": ImageTk.PhotoImage(cls.create_help_icon(size=size)),
            "clean": ImageTk.PhotoImage(cls.create_clean_icon(size=size)),
            "scan": ImageTk.PhotoImage(cls.create_scan_icon(size=size)),
            "repair": ImageTk.PhotoImage(cls.create_repair_icon(size=size)),
            "success": ImageTk.PhotoImage(cls.create_success_icon(size=size)),
            "error": ImageTk.PhotoImage(cls.create_error_icon(size=size))
        }
    
    @classmethod
    def save_all_images(cls, output_dir="resources/icons", size=48):
        """Save all icons to files."""
        # Create directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create and save all icons
        icons = {
            "app_icon": cls.create_app_icon(size=64),
            "settings": cls.create_settings_icon(size=size),
            "help": cls.create_help_icon(size=size),
            "clean": cls.create_clean_icon(size=size),
            "scan": cls.create_scan_icon(size=size),
            "repair": cls.create_repair_icon(size=size),
            "success": cls.create_success_icon(size=size),
            "error": cls.create_error_icon(size=size)
        }
        
        for name, img in icons.items():
            img.save(output_path / f"{name}.png")
        
        return [str(output_path / f"{name}.png") for name in icons.keys()]


if __name__ == "__main__":
    # When run as a script, save all images to the resources/icons directory
    saved_files = ImageGenerator.save_all_images()
    print(f"Saved {len(saved_files)} icon files:")
    for file in saved_files:
        print(f"  - {file}")
    
    # Optionally display the images in a simple Tkinter window
    try:
        root = tk.Tk()
        root.title("Generated Icons")
        
        # Create a frame to hold the icons
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack()
        
        # Load and display each icon with a label
        images = {}  # Keep references to images
        icons = ImageGenerator.get_image_dict()
        
        row = 0
        col = 0
        max_cols = 4
        
        for name, img in icons.items():
            images[name] = img  # Keep reference to prevent garbage collection
            
            # Create a label with the icon and name
            label_frame = tk.Frame(frame, padx=5, pady=5)
            label_frame.grid(row=row, column=col, padx=10, pady=10)
            
            icon_label = tk.Label(label_frame, image=img)
            icon_label.pack()
            
            name_label = tk.Label(label_frame, text=name)
            name_label.pack()
            
            # Move to next position
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Run the Tkinter event loop
        root.mainloop()
    except Exception as e:
        print(f"Error displaying icons: {e}") 