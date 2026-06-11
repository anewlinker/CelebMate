from server import get_upcoming_birthdays, generate_congratulation_poster, get_member_info

print("Upcoming birthdays:")
print(get_upcoming_birthdays(365)[:2])

print("\nMember info for 권혁주:")
print(get_member_info("권혁주"))

print("\nGenerating poster:")
result = generate_congratulation_poster("권혁주", "혁주님 생일 축하합니다!\n앞으로도 행복한 일만 가득하시길 바랍니다.", "생일")
print(result)
