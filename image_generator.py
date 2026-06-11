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

            # Draw Title & Message
            try:
                font_title = ImageFont.truetype("malgunbd.ttf", 90) # Use bold if possible
                font_subtitle = ImageFont.truetype("malgun.ttf", 55)
                font_msg = ImageFont.truetype("malgun.ttf", 45)
            except IOError:
                try:
                    font_title = ImageFont.truetype("malgun.ttf", 90)
                    font_subtitle = ImageFont.truetype("malgun.ttf", 55)
                    font_msg = ImageFont.truetype("malgun.ttf", 45)
                except IOError:
                    font_title = ImageFont.load_default()
                    font_subtitle = ImageFont.load_default()
                    font_msg = ImageFont.load_default()

            # Official Navy/Gold Government Typography Layout
            try:
                font_logo = ImageFont.truetype("malgunbd.ttf", 55)
                font_sub = ImageFont.truetype("malgunbd.ttf", 45)
                font_main = ImageFont.truetype("malgunbd.ttf", 95)
                font_medal = ImageFont.truetype("malgunbd.ttf", 40)
                font_msg = ImageFont.truetype("malgunbd.ttf", 75) # Flashy huge text
                font_sig = ImageFont.truetype("malgunbd.ttf", 45)
            except IOError:
                font_logo = font_title
                font_sub = font_subtitle
                font_main = font_title
                font_medal = font_subtitle
                font_msg = font_msg
                font_sig = font_title

            def draw_shadowed_text(y, text, font, fill_color, shadow_radius=10, shadow_opacity=200):
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                x = (bg_width - w) // 2
                
                shadow_img = Image.new('RGBA', (bg_width, bg_height), (0,0,0,0))
                s_draw = ImageDraw.Draw(shadow_img)
                for dx in [-2, 0, 2]:
                    for dy in [-2, 0, 2]:
                        s_draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, shadow_opacity))
                shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_radius))
                base_image.paste(shadow_img, (0, 0), shadow_img)
                
                draw.text((x, y), text, font=font, fill=fill_color)
            
            # 1. Top Logo
            draw_shadowed_text(100, "행정안전부", font_logo, (255, 255, 255))

            # 2. Sub-header
            draw_shadowed_text(170, f"행정안전부 {member_name} {member_rank}님", font_sub, (230, 230, 230))

            # 3. Main Congratulations
            event_text = f"{member_rank} 승진" if event_type == "승진" else event_type
            draw_shadowed_text(240, f"{event_text}을 축하합니다!", font_main, (255, 215, 0))

            # 4. Gold Medal Text (Placed dynamically above photo)
            draw_shadowed_text(420, f"{event_text}", font_medal, (255, 255, 255))

            # 5. Lower Descriptive Text (Flashy Movie Poster Tagline Format)
            import textwrap
            lines = textwrap.wrap(message, width=20)
            msg_y = bg_height - 350 - (len(lines) * 40)
            for line in lines:
                draw_shadowed_text(msg_y, line, font_msg, (255, 255, 255), shadow_radius=15, shadow_opacity=255)
                msg_y += 90

            # 6. Signature
            draw_shadowed_text(bg_height - 150, "행정안전부 일동", font_sig, (255, 215, 0))

            # Save
            output_path = os.path.join(self.output_dir, output_filename)
            base_image.save(output_path, quality=95)
            return output_path

        except Exception as e:
            print(f"Error generating poster: {e}")
            return None
