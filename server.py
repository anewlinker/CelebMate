from mcp.server.fastmcp import FastMCP
from data_manager import DataManager
from image_generator import ImageGenerator
import os

# Initialize FastMCP
mcp = FastMCP("CelebMate")

# Constants
ONW_DIR = r"c:\Users\AnewLinker\Desktop\OnW"
EXCEL_PATH = os.path.join(ONW_DIR, "구성원 명부 (30명).xlsx")
OUTPUT_DIR = os.path.join(ONW_DIR, "결과물")

# Initialize modules
data_manager = DataManager(EXCEL_PATH)
image_generator = ImageGenerator(OUTPUT_DIR)

@mcp.tool()
def get_upcoming_birthdays(days: int = 30) -> list:
    """
    Get a list of members who have birthdays coming up within the specified number of days.
    """
    return data_manager.get_upcoming_events(event_type="생일", days=days)

@mcp.tool()
def get_upcoming_promotions(days: int = 30) -> list:
    """
    Get a list of members who have promotion anniversaries coming up within the specified number of days.
    """
    return data_manager.get_upcoming_events(event_type="승진", days=days)

@mcp.tool()
def get_member_info(name: str) -> dict:
    """
    Get detailed information about a specific member by their name.
    """
    info = data_manager.get_member_info(name)
    if info:
        return info
    return {"error": f"Member {name} not found"}

@mcp.tool()
def generate_congratulation_poster(member_name: str, message: str, event_type: str) -> str:
    """
    Generate a congratulatory poster for a member with their photo and a custom message.
    :param member_name: The name of the member (e.g., '권혁주')
    :param message: The AI-generated celebratory message to print on the poster.
    :param event_type: The type of event ('생일', '승진', '수상' 등).
    :return: The file path to the generated poster image.
    """
    # Assuming photo is named like "권혁주.jpg" or "권혁주.png" in OnW folder
    photo_path_jpg = os.path.join(ONW_DIR, f"{member_name}.jpg")
    photo_path_png = os.path.join(ONW_DIR, f"{member_name}.png")
    
    photo_path = photo_path_jpg
    if not os.path.exists(photo_path) and os.path.exists(photo_path_png):
        photo_path = photo_path_png
        
    output_filename = f"{member_name}_{event_type}_축하.png"
    
    result_path = image_generator.generate_poster(photo_path, message, output_filename, member_name)
    if result_path:
        return f"Successfully generated poster at: {result_path}"
    return "Failed to generate poster. Check logs."

if __name__ == "__main__":
    # Run the server
    mcp.run()
