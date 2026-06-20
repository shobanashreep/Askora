import google.generativeai as genai

print(genai.__file__)

model = genai.GenerativeModel("gemini-2.5-flash")
print("Success")