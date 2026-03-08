from services.llm_service import LLMService

service = LLMService()
reply = service.chat("У перепёлки вялость и она плохо ест. Что проверить сначала?")
print(reply)