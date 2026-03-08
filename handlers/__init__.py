from handlers import unsupported, user_commands, user_messages


def register_routers(dp) -> None:
    dp.include_router(user_commands.router)
    dp.include_router(unsupported.router)
    dp.include_router(user_messages.router)