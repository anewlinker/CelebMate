from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap
import rembg
import math

class ImageGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def draw_text_with_shadow(self, draw, xy, text, font, text_color, shadow_color, shadow_offset=(3, 3)):
        x, y = xy
        # drop shadow
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=text_color)

    def generate_poster(self, photo_path, message, output_filename, member_name, event_type="축하", member_rank="", template_path=""):
        try:
            # 1080x1920 고화질 세로 포스터 해상도
            bg_width, bg_height = 1080, 1920
            
            # 1. Load Custom Template or Base Background
            if template_path and os.path.exists(template_path):
                base_image = Image.open(template_path).convert('RGB')
                base_image = base_image.resize((bg_width, bg_height), Image.Resampling.LANCZOS)
            else:
                base_image = Image.new('RGB', (bg_width, bg_height), (20, 20, 25))
            
            draw = ImageDraw.Draw(base_image)

            # Load and process user photo (Remove Background)
            if os.path.exists(photo_path):
                photo = Image.open(photo_path).convert("RGBA")
                # Remove background cleanly
                no_bg_photo = rembg.remove(photo)
                
                # Upscale person to be high-res (target height ~ 1100px)
                target_height = 1100
                aspect_ratio = no_bg_photo.width / no_bg_photo.height
                new_width = int(target_height * aspect_ratio)
                no_bg_photo = no_bg_photo.resize((new_width, target_height), Image.Resampling.LANCZOS)
                
                # Calculate position (Centered horizontally, anchored near the bottom)
                photo_x = (bg_width - new_width) // 2
                photo_y = bg_height - target_height - 100 # 100px from bottom margin
                
                # Create a shadow of the person for depth
                shadow = no_bg_photo.copy()
                r, g, b, a = shadow.split()
                black = Image.new('L', shadow.size, 0)
                shadow = Image.merge('RGBA', (black, black, black, a))
                shadow = shadow.filter(ImageFilter.GaussianBlur(30))
                
                # Paste shadow then person
                base_image.paste(shadow, (photo_x + 20, photo_y + 30), shadow)
                base_image.paste(no_bg_photo, (photo_x, photo_y), no_bg_photo)
            else:
                print(f"Photo not found at {photo_path}")

            # Determine Style Type
            style_type = 1
            if "template_2" in template_path: style_type = 2
            elif "template_3" in template_path: style_type = 3
            elif "template_4" in template_path: style_type = 4

            # Load Fonts
            try:
                if style_type in [3, 4]:
                    font_logo = ImageFont.truetype("Jua-Regular.ttf", 50)
                    font_sub = ImageFont.truetype("Jua-Regular.ttf", 45)
                    font_main = ImageFont.truetype("Jua-Regular.ttf", 90)
                    font_msg = ImageFont.truetype("Jua-Regular.ttf", 60)
                    font_sig = ImageFont.truetype("Jua-Regular.ttf", 40)
                else:
                    font_logo = ImageFont.truetype("malgunbd.ttf", 45)
                    font_sub = ImageFont.truetype("malgunbd.ttf", 40)
                    font_main = ImageFont.truetype("malgunbd.ttf", 85)
                    font_msg = ImageFont.truetype("malgunbd.ttf", 55)
                    font_sig = ImageFont.truetype("malgunbd.ttf", 40)
            except IOError:
                font_main = font_msg = font_sub = font_logo = font_sig = ImageFont.load_default()

            def draw_shadowed_text(y, text, font, fill_color, shadow_radius=10, shadow_opacity=200, shadow_color=(0,0,0)):
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                x = (bg_width - w) // 2
                
                # Simple native drop shadow instead of heavy gaussian blur loop
                draw.text((x+4, y+4), text, font=font, fill=shadow_color)
                # Draw text with a thin stroke to ensure it's always readable over the photo
                draw.text((x, y), text, font=font, fill=fill_color, stroke_width=2, stroke_fill=shadow_color)

            def draw_outlined_text(y, text, font, fill_color, outline_color, outline_width=6):
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                x = (bg_width - w) // 2
                
                # Use Pillow's native stroke functionality for crisp, clean outlines
                draw.text((x, y), text, font=font, fill=fill_color, stroke_width=outline_width, stroke_fill=outline_color)

            import textwrap
            lines = textwrap.wrap(message, width=22)
            # Adjust spacing dynamically based on lines
            line_spacing = 80
            msg_y = bg_height - 350 - (len(lines) * line_spacing)

            event_text = f"{member_rank} 승진" if event_type == "승진" else event_type

            if style_type == 1:
                # Style 1: Official Navy
                draw_shadowed_text(100, "행정안전부", font_logo, (255, 255, 255))
                draw_shadowed_text(160, f"행정안전부 {member_name} {member_rank}님", font_sub, (230, 230, 230))
                draw_shadowed_text(220, f"{event_text}을 축하합니다!", font_main, (255, 215, 0))
                for line in lines:
                    draw_shadowed_text(msg_y, line, font_msg, (255, 255, 255), shadow_color=(0, 0, 0))
                    msg_y += line_spacing
                draw_shadowed_text(bg_height - 120, "행정안전부 일동", font_sig, (255, 215, 0))

            elif style_type == 2:
                # Style 2: Cinematic Movie
                draw_shadowed_text(100, "행정안전부", font_logo, (200, 200, 255), shadow_color=(0, 50, 150))
                draw_shadowed_text(160, f"행정안전부 {member_name} {member_rank}님", font_sub, (255, 255, 255), shadow_color=(0, 50, 150))
                draw_shadowed_text(220, f"{event_text}을 축하합니다!", font_main, (255, 255, 255), shadow_color=(0, 50, 150))
                for line in lines:
                    draw_shadowed_text(msg_y, line, font_msg, (255, 255, 255), shadow_color=(0, 50, 150))
                    msg_y += line_spacing
                draw_shadowed_text(bg_height - 120, "행정안전부 일동", font_sig, (200, 200, 255))

            elif style_type == 3:
                # Style 3: Pop Art Mix
                draw_outlined_text(100, "행정안전부", font_logo, (255, 255, 0), (0, 0, 0), outline_width=4)
                draw_outlined_text(160, f"행정안전부 {member_name} {member_rank}님", font_sub, (255, 255, 255), (0, 0, 0), outline_width=4)
                draw_outlined_text(220, f"{event_text}을 축하합니다!", font_main, (255, 20, 147), (255, 255, 255), outline_width=6)
                for line in lines:
                    draw_outlined_text(msg_y, line, font_msg, (0, 255, 255), (0, 0, 0), outline_width=4)
                    msg_y += line_spacing
                draw_outlined_text(bg_height - 120, "행정안전부 일동", font_sig, (255, 255, 0), (0, 0, 0), outline_width=4)

            elif style_type == 4:
                # Style 4: MZ Sticker
                draw_outlined_text(100, "행정안전부", font_logo, (147, 112, 219), (255, 255, 255), outline_width=5)
                draw_outlined_text(160, f"행정안전부 {member_name} {member_rank}님", font_sub, (0, 0, 0), (255, 255, 255), outline_width=5)
                draw_outlined_text(220, f"{event_text}을 축하합니다!", font_main, (255, 105, 180), (255, 255, 255), outline_width=8)
                for line in lines:
                    draw_outlined_text(msg_y, line, font_msg, (0, 0, 0), (255, 255, 255), outline_width=6)
                    msg_y += line_spacing
                draw_outlined_text(bg_height - 120, "행정안전부 일동", font_sig, (147, 112, 219), (255, 255, 255), outline_width=5)

            # Save
            output_path = os.path.join(self.output_dir, output_filename)
            base_image.save(output_path, quality=95)
            return output_path

        except Exception as e:
            print(f"Error generating poster: {e}")
            return None
